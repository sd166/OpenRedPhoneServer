from __future__ import unicode_literals


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 31337

POSTGRES = dict(
    host="127.0.0.1",
    port=5432,
    login="login",
    password="password",
    db="db"
)

REDIS = dict(
    host="localhost",
    port=6379,
    login=None,
    password=None,
    db=0
)
