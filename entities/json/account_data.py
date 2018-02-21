from __future__ import unicode_literals
from info.s1z.utils.json_serializable import JsonSerializable
from info.s1z.utils.json_serializable import json_property
from .account_device import AccountDevice


class AccountData(JsonSerializable):

    @json_property(int, null=True)
    def whitelisted(self): pass

    @json_property(bytes)
    def number(self): pass

    @json_property([AccountDevice], AccountDevice)
    def devices(self): pass

    @json_property(bytes)
    def identity_key(self): pass

    def get_devices(self):
        return self.devices

    def get_device(self, _id):
        # type: (int) -> AccountDevice
        for device in self.devices:
            if _id == device.id:
                return device
