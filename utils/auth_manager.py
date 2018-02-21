from __future__ import unicode_literals
import sys
import tornado.gen
from info.s1z.utils.log import Log
from info.s1z.utils.base_64 import Base64
from utils.redis_client import RedisClient


if sys.version_info[0] == 3:
    unicode = str


TAG = "AuthManager"


class AuthManager(object):

    def __init__(self, redis):
        # type: (RedisClient) -> None
        self.redis = redis

    @tornado.gen.coroutine
    def authenticate(self, headers):
        # type: (dict) -> Account or None
        for header_name in ["Authorization", "WWW-Authorization"]:
            auth_data = headers.get(header_name, None)
            if auth_data is not None:
                try:
                    auth_type, token = auth_data.split(" ")
                    auth_method = {
                        "otp": self.auth_otp,
                        "basic": self.auth_basic
                    }.get(auth_type.lower(), None)
                    if auth_method is not None:
                        raise tornado.gen.Return((
                            yield auth_method(
                                Base64.decode(token).decode("utf-8")
                            )
                        ))
                except Exception as e:
                    Log.e(TAG, "authenticate error", e)

    @tornado.gen.coroutine
    def auth_basic(self, token):
        # type: (unicode) -> Account or None
        login, passw = token.split(":")
        account = yield self.redis.get(login)
        if account is not None:
            pass

    def auth_otp(self, token):
        # type: (unicode) -> Account or None
        login, passw, otp = token.split(":")
        account = yield self.redis.get(login)
        if account is not None:
            pass
