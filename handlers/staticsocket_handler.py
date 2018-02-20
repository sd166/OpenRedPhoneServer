# -*- coding: utf-8 -*-
import tornado.escape
import tornado.web
import tornado.gen
import tornado.httputil
from utils.static_socket_connection import StaticSocketConnection
from info.s1z.utils.log import Log


TAG = "StaticSocketHandler"


class StaticSocketHandler(tornado.web.RequestHandler):

    _status_code = None
    _static_connection = None
    open_args = None
    open_kwargs = None

    is_static = False
    is_closed = False

    def start_static(self, *args, **kwargs):
        self.open_args = args
        self.open_kwargs = kwargs

        self.is_static = True
        self.is_closed = False

        self._static_connection = StaticSocketConnection(self)
        self._static_connection.add_on_open_callback(self.on_open)
        self._static_connection.add_on_close_callback(self.on_close)
        self._static_connection.accept_connection()

    def on_open(self, *args, **kwargs):
        Log.d(TAG, "on_open %r" % id(self))

    def on_close(self, *args, **kwargs):
        Log.d(TAG, "on_open %r" % id(self))
        if not self.is_closed:
            self.is_closed = True
            if self._static_connection is not None:
                self._static_connection.abort()
                self._static_connection = None
            super(StaticSocketHandler, self)._break_cycles()

    def r400(self):
        self.set_status(400, "Bad Request")
        self.finish()

    def r401(self):
        self.set_status(401, "Unauthorized")
        self.add_header("WWW-Authenticate", 'Basic realm="Unauthorized"')
        self.finish()

    def r402(self, data=None):
        self.set_status(402)
        self.write(data or b"Unknown error")
        self.finish()

    def r404(self):
        self.set_status(404)
        self.finish()

    def __del__(self):
        # Will not be invoke if there is a memory leak somewhere
        # TODO(s1z): Remove it when everything is done
        Log.d(TAG, "__del__ %s" % StaticSocketHandler.__name__)
