import tornado.gen
import tornado.web
from info.s1z.utils.log import Log


TAG = "MainHandler"


def wrap_static(*args, **kwargs):
    raise NotImplementedError()


class StaticSocketHandler(tornado.web.RequestHandler): pass


class MainHandler(StaticSocketHandler):

    _active_session = None  # type: int  # Do we need it here?
    account = None  # type: Account  # TODO(s1z): Create model

    # Clients
    relay_client = None
    push_client = None
    session_client = None
    required_clients = ["relay_client", "push_client", "session_client"]

    SUPPORTED_METHODS = (
        'GET', 'DELETE', 'RING', 'BUSY'
    )

    def initialize(self, *args, **kwargs):
        try:
            for client_name in self.required_clients:
                setattr(self, client_name, kwargs.pop(client_name))
        except KeyError:
            raise AttributeError(
                "Clients must be set (%s)" % ','.join(self.required_clients)
            )

    @tornado.gen.coroutine
    def handle_get(self):
        raise NotImplementedError()

    @tornado.gen.coroutine
    def handle_ring(self):
        raise NotImplementedError()

    @tornado.gen.coroutine
    def handle_busy(self):
        raise NotImplementedError()

    @tornado.gen.coroutine
    def handle_delete(self):
        raise NotImplementedError()

    @wrap_static
    def get(self, *args, **kwargs):
        self.handle_get(*args, **kwargs)

    @wrap_static
    def ring(self, *args, **kwargs):
        self.handle_ring(*args, **kwargs)

    @wrap_static
    def busy(self, *args, **kwargs):
        self.handle_busy(*args, **kwargs)

    @wrap_static
    def delete(self, *args, **kwargs):
        self.handle_delete(*args, **kwargs)

    def __del__(self):
        # Will not be invoke if there is a memory leak somewhere
        # TODO(s1z): Remove it when everything is done
        Log.d(TAG, "__del__ %s" % MainHandler.__name__)
