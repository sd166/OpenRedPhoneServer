import tornado.gen
import tornado.web
from info.s1z.utils.log import Log
from .staticsocket_handler import StaticSocketHandler

TAG = "MainHandler"


def wrap_static(*args, **kwargs):
    raise NotImplementedError()



class MainHandler(StaticSocketHandler):

    _active_session = None  # type: int  # Do we need it here?
    account = None  # type: Account  # TODO(s1z): Create model

    # Clients
    relay = None
    push = None
    session = None
    managers = ["relay", "push", "session"]

    SUPPORTED_METHODS = (
        'GET', 'DELETE', 'RING', 'BUSY'
    )

    def initialize(self, *args, **kwargs):
        try:
            for client_name in self.managers:
                setattr(self, client_name, kwargs.pop(client_name))
        except KeyError:
            raise AttributeError(
                "Clients must be set (%s)" % ','.join(self.managers)
            )

    @tornado.gen.coroutine
    def handle_create(self):
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

    def get(self, *args, **kwargs):
        self.handle_create(*args, **kwargs)

    def ring(self, *args, **kwargs):
        self.handle_ring(*args, **kwargs)

    def busy(self, *args, **kwargs):
        self.handle_busy(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.handle_delete(*args, **kwargs)

    def __del__(self):
        # Will not be invoke if there is a memory leak somewhere
        # TODO(s1z): Remove it when everything is done
        Log.d(TAG, "__del__ %s" % MainHandler.__name__)
