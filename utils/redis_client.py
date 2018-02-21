import tornadis
import tornado.gen
import concurrent.futures
from info.s1z.utils.log import Log


TAG = "RedisClient"


class RedisClient(object):

    CONNECTION_TIMEOUT = 10  # type: int
    host = None  # type: bytes
    port = None  # type: int
    login = None  # type: bytes
    password = None  # type: bytes
    db = None  # type: int
    is_running = None  # type: bool
    _client = None # type: tornadis.Client

    def __init__(self, host=b"localhost", port=6379,
                 login=None, password=None, db=0):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.db = db
        self._client = None

    def start(self):
        self.is_running = True
        if self._client is None:
            self._client = tornadis.Client(
                autoconnect=False,
                password=self.password,
                db=self.db,
                **dict(
                    read_callback=self.on_connected_callback,
                    close_callback=self.on_close_callback,
                    host=self.host,
                    port=self.port,
                    tcp_nodelay=True,
                    connect_timeout=self.CONNECTION_TIMEOUT,
                    read_timeout=self.CONNECTION_TIMEOUT,
                )
            )
        self.connect()

    def stop(self):
        self.is_running = False
        self.disconnect()

    @tornado.gen.coroutine
    def connect(self):
        if self._client is not None:
            while not (yield self._client.connect()):
                Log.e(TAG, "client connect error. retry after 1 sec")
                yield tornado.gen.sleep(1)
            raise tornado.gen.Return()
        raise AttributeError("tornadis client is None!")

    @tornado.gen.coroutine
    def disconnect(self):
        if self._client is not None and self._client.is_connected():
            self._client.disconnect()

    @tornado.gen.coroutine
    def on_connected_callback(self):
        Log.d(TAG, "on_connected_callback")

    @tornado.gen.coroutine
    def on_close_callback(self):
        Log.d(TAG, "on_connected_callback")
        if self.is_running is True:
            self._client.disconnect()
            yield self.connect()

    @tornado.gen.coroutine
    def set(self, key, value):
        # type: (bytes, bytes) -> bool
        if self._client.is_connected() and self.is_running is True:
            result = yield self._client.call("SET", key, value)
            if not isinstance(result, tornadis.ConnectionError):
                raise tornado.gen.Return(True)
        raise tornado.gen.Return(False)

    @tornado.gen.coroutine
    def setex(self, key, ttl, value):
        # type: (bytes, int, bytes) -> bool
        if self._client.is_connected() and self.is_running is True:
            result = yield self._client.call("SETEX", key, ttl, value)
            if not isinstance(result, tornadis.ConnectionError):
                raise tornado.gen.Return(True)
        raise tornado.gen.Return(False)

    @tornado.gen.coroutine
    def get(self, key):
        # type: (bytes) -> bytes or None
        if self._client.is_connected() and self.is_running is True:
            result = yield self._client.call(b"GET", key)
            if isinstance(result, tornadis.ConnectionError):
                raise result
            raise tornado.gen.Return(result)
