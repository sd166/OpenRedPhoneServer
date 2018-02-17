from __future__ import unicode_literals
import sys
import base64


if sys.version_info[0] == 3:
    unicode = str


class Base64(object):
    @staticmethod
    def encode_without_padding(data):
        # type: ([str, unicode, bytes, bytearray]) -> bytes
        if isinstance(data, (str, unicode)):
            data = data.encode("utf-8")
        return base64.b64encode(bytes(data)).rstrip(b'=')

    @staticmethod
    def decode_without_padding(data):
        # type: ([str, unicode, bytes, bytearray]) -> bytes
        if isinstance(data, (str, unicode)):
            data = data.encode("utf-8")
        return base64.b64decode(bytes(data) + b'===')
