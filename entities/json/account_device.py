from __future__ import unicode_literals
from info.s1z.utils.json_serializable import JsonSerializable
from info.s1z.utils.json_serializable import json_property
from .signed_pre_key import SignedPreKey


class AccountDevice(JsonSerializable):

    @json_property(int)
    def id(self): pass

    @json_property(bytes, null=True)
    def name(self): pass

    @json_property(bytes)
    def auth_token(self): pass

    @json_property(bytes)
    def salt(self): pass

    @json_property(bytes)
    def signaling_key(self): pass

    @json_property(bytes, null=True)
    def gcm_id(self): pass

    @json_property(bytes, null=True)
    def apn_id(self): pass

    @json_property(bytes, null=True)
    def voip_apn_id(self): pass

    @json_property(int)
    def push_timestamp(self): pass

    @json_property(bool)
    def fetches_messages(self): pass

    @json_property(int)
    def registration_id(self): pass

    @json_property(SignedPreKey, SignedPreKey)
    def signed_pre_key(self): pass

    @json_property(int)
    def last_seen(self): pass

    @json_property(int)
    def created(self): pass

    @json_property(bool)
    def voice(self): pass

    @json_property(bytes)
    def user_agent(self): pass
