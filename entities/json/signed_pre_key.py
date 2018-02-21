from __future__ import unicode_literals
from info.s1z.utils.json_serializable import JsonSerializable
from info.s1z.utils.json_serializable import json_property


class SignedPreKey(JsonSerializable):

    @json_property(int)
    def key_id(self): pass

    @json_property(bytes)
    def public_key(self): pass

    @json_property(bytes)
    def signature(self): pass
