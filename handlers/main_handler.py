import tornado.gen
import tornado.web
from info.s1z.utils.log import Log
from .static_handler import StaticSocketHandler


TAG = "MainHandler"


class MainHandler(StaticSocketHandler):

    _active_session = None  # type: int  # Do we need it here?
    account = None  # type: Account  # TODO(s1z): Create a model

    # Managers
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
    def handle_create(self, device_id, number):
        Log.d(TAG, "handle_create: %r, %r" % (device_id, number))
        self.set_status(200)
        self.finish()

    @tornado.gen.coroutine
    def handle_ring(self, device_id, number):
        self.set_status(200)
        self.finish()

    @tornado.gen.coroutine
    def handle_busy(self, device_id, number):
        self.set_status(200)
        self.finish()

    @tornado.gen.coroutine
    def handle_delete(self, device_id, number):
        self.set_status(200)
        self.finish()

    @StaticSocketHandler.static
    def get(self, device_id, number):
        Log.d(TAG, "get")
        return self.handle_create(device_id, number)

    @StaticSocketHandler.static
    def ring(self, device_id, number):
        Log.d(TAG, "ring")
        return self.handle_ring(device_id, number)

    @StaticSocketHandler.static
    def busy(self, device_id, number):
        Log.d(TAG, "busy")
        return self.handle_busy(device_id, number)

    @StaticSocketHandler.static
    def delete(self, device_id, number):
        Log.d(TAG, "delete")
        return self.handle_delete(device_id, number)

    def __del__(self):
        # Will not be invoke if there is a memory leak somewhere
        # TODO(s1z): Remove it when everything is done
        Log.d(TAG, b"__del__ %r" % MainHandler.__name__)
