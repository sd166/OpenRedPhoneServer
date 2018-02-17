# -*- coding: utf-8 -*-
import simplejson as json
from .log import Log


TAG = "JsonUtil"


class JsonProcessingException(Exception):
    pass


class JsonUtil(object):

    @staticmethod
    def to_json(obj):
        if getattr(obj, "to_json", None) is not None:
            return obj.__class__.to_json(obj)
        raise Exception("%s is not serializable" % obj.__class__)

    @staticmethod
    def from_json(text, cls):
        if getattr(cls, "from_json", None) is not None:
            return cls.from_json(text)
        raise JsonProcessingException("%s is not serializable" % cls)

    @staticmethod
    def json_loads(data, default=None):
        try:
            jdata = json.loads(data, strict=False)
            if isinstance(jdata, dict) or isinstance(jdata, list):
                return jdata
        except Exception as e:
            Log.e(TAG, "json_loads: Error = '%s'" % repr(e))
        return default

    @staticmethod
    def json_dumps(*args, **kwargs):
        try:
            return json.dumps(*args, **kwargs)
        except Exception as e:
            Log.e(TAG, "json_dumps: Error = '%s'" % repr(e))
            raise
