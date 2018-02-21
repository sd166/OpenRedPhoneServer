from __future__ import unicode_literals
import tornado.gen
from hashlib import sha1
from info.s1z.utils.log import Log
from info.s1z.utils.jsonutil import JsonUtil
from info.s1z import apsql as models
from entities.json.account_data import AccountData
from entities.json.account_device import AccountDevice


class Account(models.Model):

    id = None  # type: int
    number = None  # type: bytes
    data = None  # type: AccountData
    devices = None  # type: list

    _all_fields = ["id", "number", "data", "devices"]

    def __init__(self, _id, number, data):
        # type: (int, bytes, dict) -> None
        self.id = _id
        self.number = number
        self.data = JsonUtil.from_json(data, AccountData)
        self.devices = self.data.get_devices()

    def get_device(self, _id):
        # type: (int) -> AccountDevice
        return self.data.get_device(_id)

    def auth(self, passw, count=None):
        # TODO(s1z): Please IMPLEMENT ME :)
        return True
        #type = "otp" if count is not None else "basic"
        #for device in self.devices:
        #    salt = device.salt
        #    if self.otp == sha1(device.salt+passw).hexdigest():
        #        return True
        #return False

    @classmethod
    @tornado.gen.coroutine
    def get(cls, **kwargs):
        request, params = cls.get_select(*cls._all_fields, **kwargs)
        result = yield cls.execute(request, params)
        if result is None:
            raise cls.DoesNotExist()
        raise tornado.gen.Return(cls._object(result))
