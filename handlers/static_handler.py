# -*- coding: utf-8 -*-
import tornado.escape
import tornado.web
import tornado.gen
import tornado.httputil
from utils.static_socket_connection import StaticSocketConnection
from info.s1z.utils.log import Log


TAG = "StaticSocketHandler"


class StaticSocketHandler(tornado.web.RequestHandler):

    _status_code = None  # type: int
    _static_connection = None  # type: StaticSocketConnection
    open_args = None  # type: tuple
    open_kwargs = None  # type: dict

    is_static = False  # type: bool
    is_closed = False  # type: bool

    @staticmethod
    def static(real_func):

        def basic_auth(wrap_func):
            @tornado.web.asynchronous
            def deco(self, *args, **kwargs):
                def callback():
                    return wrap_func(self, *args, **kwargs)
                self.auth(callback)
            return deco

        @basic_auth
        def wrapper(self, *args, **kwargs):
            if not self.is_static:
                self.start_static()
                real_func(self, *args, **kwargs)

        return wrapper

    @tornado.gen.coroutine
    def auth(self, callback):
        Log.d(TAG, "auth")
        if "Authorization" in self.request.headers:
            login, passw = get_loginpass(self.request.headers["Authorization"])
            if login == self.login and passw == self.passw:
                callback()
                return
        #try:
        #    raise NotImplementedError()
        #except NotImplementedError as e:
        #    Log.e(TAG, "auth is not implemented", e)
        #self.r500()

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
        if not self.is_closed and self.is_static:
            self.is_closed = True
            if self._static_connection is not None:
                self._static_connection.abort()
                self._static_connection = None
            super(StaticSocketHandler, self)._break_cycles()

    def static_flush(self, include_footers=False, callback=None):
        chunk = b"".join(self._write_buffer)
        self._write_buffer = []
        for transform in self._transforms:
            self._status_code, self._headers, chunk = \
                transform.transform_first_chunk(
                    self._status_code, self._headers,
                    chunk, include_footers)
        if self.request.method == "HEAD":
            chunk = None

        if hasattr(self, "_new_cookie"):
            for cookie in self._new_cookie.values():
                self.add_header("Set-Cookie", cookie.OutputString(None))

        start_line = tornado.httputil.ResponseStartLine(self.request.version,
                                                self._status_code,
                                                self._reason)
        if self._static_connection:
            self._static_connection.write_headers(
                start_line, self._headers, chunk
            )
            return self._static_connection._stream.write(
                chunk, callback=callback
            )

    def static_finish(self, chunk=None):
        if self._status_code == 304:
            assert not self._write_buffer, "Cannot send body with 304"
            self._clear_headers_for_304()
        elif "Content-Length" not in self._headers:
            content_length = sum(len(part) for part in self._write_buffer)
            self.set_header("Content-Length", content_length)
        self.static_flush(include_footers=True)

    def finish(self, *args, **kwargs):
        if not self.is_static:
            super(StaticSocketHandler, self).finish(*args, **kwargs)
        else:
            self.static_finish(*args, **kwargs)

    def close(self, *args, **kwargs):
        self.finish(*args, **kwargs)
        self.on_close()

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

    def r500(self):
        self.set_status(500)
        self.finish()

    def __del__(self):
        # Will not be invoke if there is a memory leak somewhere
        # TODO(s1z): Remove it when everything is done
        Log.d(TAG, "__del__ %s" % StaticSocketHandler.__name__)
