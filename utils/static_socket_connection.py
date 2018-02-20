# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tornado.gen
import tornado.iostream
import tornado.httputil as httputil
from tornado.escape import native_str, utf8
from info.s1z.utils.log import Log
from handlers.staticsocket_handler import StaticSocketHandler


TAG = "StaticSocketConnection"


try:
    range = xrange
except NameError:
    pass


class StaticSocketConnection(object):

    _handler = None
    _stream = None

    _server_terminated = False

    _on_open_callbacks = []
    _on_close_callbacks = []

    is_closed = False

    def __init__(self, handler):
        # type: (StaticSocketHandler) -> None
        self._handler = handler
        self._stream = handler.request.connection.detach()
        self._stream.set_close_callback(self.on_close)

    def abort(self):
        if not self.is_closed:
            self.is_closed = True
            self._handler = None
            self._stream.close()

    def clear_callbacks(self):
        self._on_open_callbacks = []
        self._on_close_callbacks = []

    def add_on_open_callback(self, callback):
        self._on_open_callbacks.append(callback)

    def add_on_close_callback(self, callback):
        self._on_close_callbacks.append(callback)

    @staticmethod
    def _execute_callbacks(queue, *args, **kwargs):
        # type: (list, tuple, dict) -> None
        for i in range(len(queue)):
            callback = queue.pop()
            try:
                callback(*args, **kwargs)
            except Exception as e:
                Log.e(TAG, "callback execute error", e)
        Log.d(TAG, "callbacks execution done")

    def on_close(self, *args, **kwargs):
        self._execute_callbacks(self._on_close_callbacks, *args, **kwargs)

    def on_open(self, *args, **kwargs):
        self._execute_callbacks(self._on_open_callbacks, *args, **kwargs)

    def accept_connection(self):
        if self._stream.closed():
            return self.abort()
        self.on_open(*self._handler.open_args, **self._handler.open_kwargs)
        self._receive_data()

    def write_headers(self, start_line, headers, chunk=None, callback=None):
        lines = [b" ".join([b'%r' % x for x in [
            start_line.version, start_line.code, start_line.reason
        ]])]
        for name, value in headers.items():
            lines.append(b"%r: %r" % (name, value))
        if not self._stream.closed():
            data = utf8(b"\r\n".join(lines) + b"\r\n\r\n")
            self._stream.write(data)

    @tornado.gen.coroutine
    def _handle_request(self, data):
        try:
            start_line, headers = self.parse_headers(data)
            request = httputil.HTTPServerRequest(
                headers=headers,
                start_line=httputil.parse_request_start_line(start_line)
            )
            deli = self._handler.application.find_handler(request)
            getattr(
                self._handler, request.method.lower(), self._handler.r404
            )(*deli.path_args, **deli.path_kwargs)
        except httputil.HTTPInputError as e:
            Log.e(TAG, "_handle_request error", e)

    @tornado.gen.coroutine
    def _handle_response(self, data):
        try:
            response = httputil.parse_response_start_line(data)
            Log.d(TAG, "_handle_response %r" % response)
        except httputil.HTTPInputError as e:
            Log.e(TAG, "_handle_response error", e)

    @tornado.gen.coroutine
    def _handle_data(self, data):
        if "HTTP" in data[:4]:
            # response
            yield self._handle_response(data)
        else:
            # try read request
            yield self._handle_request(data)
        self._receive_data()

    @tornado.gen.coroutine
    def _receive_data(self):
        if not self.is_closed:
            try:
                data_future = self._stream.read_until_regex(
                    b"\r?\n\r?\n",
                    max_bytes=65536
                )
                # TODO(s1z): Do we need a timeout here? I Think we need.
                data = yield data_future
                yield self._handle_data(data)
            except tornado.iostream.StreamClosedError:
                self.abort()

    @staticmethod
    def parse_headers(data):
        data = native_str(data.decode('latin1')).lstrip(b"\r\n")
        eol = data.find(b"\n")
        start_line = data[:eol].rstrip(b"\r")
        try:
            headers = httputil.HTTPHeaders.parse(data[eol:])
        except ValueError:
            raise httputil.HTTPInputError(
                "Malformed HTTP headers: %r" % data
            )
        return start_line, headers
