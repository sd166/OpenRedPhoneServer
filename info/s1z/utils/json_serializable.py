# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# TODO(s1z): fallback to json
# TODO(s1z): This is madness! You have to clean this shit :)
import sys
import simplejson as json
from .log import Log

try:
    range = xrange
except ImportError:
    # python 3 has no unicode
    unicode = str


TAG = "JsonSerializable"


class DefaultSerializer(object):
    @staticmethod
    def loads(data):
        return data

    @staticmethod
    def dumps(data):
        return data


class JProperty(property):

    value_type = None
    serializer = None
    null = None

    def __init__(self, fget, fset, fdel, value_type, serializer, null, jsonize):
        super(JProperty, self).__init__(fget, fset, fdel)
        self.value_type = value_type
        self.serializer = serializer
        self.null = null
        self.jsonize = jsonize

    def get_value_type(self):
        return self.value_type

    def get_serializer(self):
        return self.serializer

    def get_null(self):
        return self.null

    def get_jsonize(self):
        # type: (self) -> bool
        return self.jsonize is True


def json_property(value_type, serializer=DefaultSerializer, null=False, j=True):

    def check_type(self, name, value):
        setattr(self, "_serialized_%s" % name, serializer.dumps(value))
        return value

    def wrap(f):
        def getter(self):
            return getattr(
                self,
                "_serializable_%s" % f.__name__,
                None
            ) or f(self)

        def setter(self, value):
            setattr(self, "_serializable_%s" % f.__name__, value)
            # TODO(s1z): Do we need to serialize in real time or when dumping?
            setattr(
                self, "_serialized_%s" % f.__name__, serializer.dumps(value)
            )

        def deleter(self):
            delattr(self, "_serializable_%s" % f.__name__)

        return JProperty(
            getter, setter, deleter, value_type, serializer, null, j
        )
    return wrap


class MetaSerializable(type):

    def __new__(cls, name, bases, attrs):
        new_cls = super(MetaSerializable, cls).__new__(cls, name, bases, attrs)
        bases_serializable = {}
        for base in bases:
            if hasattr(base, "_serializable"):
                bases_serializable.update(base._serializable)
        new_cls._serializable = bases_serializable
        for k, v in attrs.items():
            if isinstance(v, JProperty):
                new_cls._serializable[k] = v
        return new_cls

    def __call__(cls, *args, **kwargs):
        return type.__call__(cls, *args, **kwargs)
        # TODO(s1z): Do we need to init default values ? I guess not
        # if len(args) < 0 or len(kwargs) < 0:
        #    for k in obj._serializable:
        #        getattr(obj, k)


class JsonSerializable(object):
    __metaclass__ = MetaSerializable
    _serializable = {}

    def _get_keys(self):
        return self._serializable.keys()

    def _get_value(self, key):
        serialized = getattr(self, "_serialized_%s" % key, None)
        return serialized if serialized is not None else getattr(self, key)

    @classmethod
    def _obj_dumps(cls, obj):
        if isinstance(obj, JsonSerializable):
            serialized = {}
            for key in obj._get_keys():
                p = cls._serializable.get(key, None)  # type: JProperty
                final_key = obj._unpythonize(key) if p.get_jsonize() else key
                value = obj._get_value(key)
                # TODO(s1z): Do we need to send if null ? Have to add setups
                if value is not None:
                    serialized[final_key] = value
                else:
                    if p is not None and p.get_null():
                        serialized[final_key] = None
                    else:
                        raise AttributeError("'%s':'%s'" % (key, value))
            return serialized

    @classmethod
    def _dumps(cls, obj):
        if type(obj) is list:
            serialized = []
            for data in obj:
                serialized.append(cls._obj_dumps(data))
            return serialized
        return cls._obj_dumps(obj)

    @classmethod
    def _obj_loads(cls, data):
        obj = cls.__new__(cls)
        if isinstance(data, dict):
            for k, v in data.items():
                real_name = cls._pythonize(k)
                p = cls._serializable.get(real_name, None)
                if p is not None and isinstance(p, JProperty):
                    serializer = p.get_serializer()
                    real_value = serializer.loads(v)
                    setattr(obj, real_name, real_value)
                    Log.d(TAG, "_obj_loads: {'%s': '%s'}" % (
                        real_name, real_value
                    ))
            # TODO(s1z): Check if all required fields are set.
            return obj

    @classmethod
    def _loads(cls, obj):
        if type(obj) is list:
            loaded = []
            for data in obj:
                loaded.append(cls._obj_loads(data))
            return loaded
        return cls._obj_loads(obj)

    @staticmethod
    def _unpythonize(s):
        if isinstance(s, (str, unicode)) and len(s) > 0:
            new_s = ''
            for i in range(len(s)):
                if i > 0 and s[i-1] == "_":
                    new_s += s[i].upper()
                elif s[i] == "_":
                    pass
                else:
                    new_s += s[i].lower()
            return new_s
        raise AttributeError("Incorrect type = '%s' or len < 1" % type(s))

    @staticmethod
    def _pythonize(s):
        return ''.join(["_%s" % l.lower() if l.isupper() else l for l in s])

    @classmethod
    def to_json(cls, obj):
        return json.dumps(obj, default=cls._dumps)

    @classmethod
    def from_json(cls, data):
        return cls._loads(json.loads(data))

    @classmethod
    def dumps(cls, value):
        return cls._dumps(value)

    @classmethod
    def loads(cls, value):
        return cls._loads(value)

    def to_string(self):
        return "{}".format(self.to_json(self))
