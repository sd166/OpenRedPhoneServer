#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import traceback
import logging


class Log(object):

    logger = logging.getLogger(__name__)
    handler = logging.NullHandler()

    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    @staticmethod
    def log(level, tag, message, ex):
        if ex is not None:
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            message = "%s\n%s" % (message, traceback.format_exc())
        msg = "{}::{}".format(tag, message)
        Log.logger.log(level, msg)

    @staticmethod
    def d(tag, message, ex=None):
        return Log.log(logging.DEBUG, tag, message, ex)

    @staticmethod
    def i(tag, message, ex=None):
        return Log.log(logging.INFO, tag, message, ex)

    @staticmethod
    def w(tag, message, ex=None):
        return Log.log(logging.WARN, tag, message, ex)

    @staticmethod
    def e(tag, message, ex=None):
        return Log.log(logging.ERROR, tag, message, ex)
