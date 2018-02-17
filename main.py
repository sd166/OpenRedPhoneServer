#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tornado.httpserver
import tornado.ioloop
import tornado.web
import logging
import settings as s
from info.s1z.utils.log import Log


TAG = "Main"


def main():
    initializer = dict(
        # rabbit_sender=rabbit_sender,
        # rabbit_rpc=rabbit_rpc,
        # redis_client=redis_client,
        # auth_client=auth_client
    )
    application = tornado.web.Application([
        #
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