#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tornado.httpserver
import tornado.ioloop
import tornado.web
import logging
import settings as s
from info.s1z.utils.log import Log
from info.s1z import apsql as models
from handlers.main_handler import MainHandler
from utils.auth_manager import AuthManager
from utils.redis_client import RedisClient


TAG = "Main"


def main():

    psql = models.Model.set_parameters(**s.POSTGRES)
    redis = RedisClient(**s.REDIS)

    initializer = dict(
        relay=object(),
        push=object(),
        session=object(),
        auth=AuthManager(redis)
    )
    application = tornado.web.Application([
        (
            r'^/session/(?P<device_id>\d+)/(?P<number>[0-9\+]{3,15})$',
            MainHandler,
            initializer
        )
    ])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(s.SERVER_PORT, s.SERVER_HOST)
    server.start()
    Log.d(TAG, "OpenRedPhoneServer is run")


if __name__ == "__main__":
    io_loop = tornado.ioloop.IOLoop.current()
    try:
        logging_config = {
            "format": "%(asctime)-23s %(levelname)8s: %(message)s",
            "level": logging.DEBUG,
        }
        logging.basicConfig(**logging_config)
        main()
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
