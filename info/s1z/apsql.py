# -*- encoding: utf-8 -*-
import momoko
import tornado.gen
import tornado.ioloop


class BaseModel(object):

    class DoesNotExist(Exception):
        pass

    class UpdateFailed(Exception):
        pass

    class InsertError(Exception):
        pass


class Model(BaseModel):
    _table = None  # this should be overwritten

    _pool = None
    _pool_read = None
    #
    _min_size = 5  # Minimal numbers of connections
    _max_size = 100  # Max numbers of connections
    _raise_c_errors = False
    _reconnect_interval = 50  # milliseconds
    _auto_shrink = True
    #
    host = None
    port = None
    login = None
    password = None
    db = None

    @classmethod
    def _object(cls, args):
        for obj in args:
            return cls(*obj)

    @classmethod
    def _objects(cls, args):
        return [cls._object([x]) for x in args]

    @classmethod
    def _strip_count(cls, args):
        for val in args:
            for _id in val:
                return _id
        return 0

    @classmethod
    def get_returning_insert(cls, *returning, **fields):
        str_fields = ','.join(fields.keys())
        str_values = ','.join(['%s' for i in range(len(fields.keys()))])
        str_returning = "id, {fields}".format(
            fields=str_fields
        ) if len(returning) > 0 else ','.join(returning)
        return (
            " INSERT INTO {table} ({fields}) "
            " VALUES ({values}) "
            " RETURNING {returning} "
        ).format(
            table=cls._table,
            fields=str_fields,
            values=str_values,
            returning=str_returning
        ), fields.values()

    @classmethod
    def get_select(cls, *fields, **where):
        return (
            " SELECT {fields}"
            " FROM {table} "
            " WHERE {where} "
        ).format(
            table=cls._table,
            fields=','.join(fields),
            where=' AND '.join(['{} = %s'.format(f) for f in where.keys()])
        ), where.values()

    @staticmethod
    def set_parameters(host, port, login, password, db):
        Model.host = host
        Model.port = port
        Model.login = login
        Model.password = password
        Model.db = db
        Model._pool = Model.current()
        Model.connect()

    @staticmethod
    def set_read_parameters(host, port, login, password, db):
        # TODO(s1z): Add Read only DB instance
        Model.host = host
        Model.port = port
        Model.login = login
        Model.password = password
        Model.db = db
        Model._pool_read = Model.current()
        Model.connect()

    @staticmethod
    def new_instance():
        pool = momoko.Pool(
            dsn='dbname=%s user=%s password=%s host=%s port=%s' % (
                Model.db,
                Model.login,
                Model.password,
                Model.host,
                Model.port
            ),
            size=Model._min_size,
            max_size=Model._max_size,
            ioloop=tornado.ioloop.IOLoop.current(),
            setsession=["SET TIME ZONE UTC"],
            raise_connect_errors=Model._raise_c_errors,
            auto_shrink=Model._auto_shrink
        )
        return pool

    @staticmethod
    def current():
        current = getattr(Model, "_pool", None)
        if current is None:
            return Model.new_instance()
        return current

    @staticmethod
    def connect():
        if Model._pool is not None:
            Model._pool.connect()

    @staticmethod
    def disconnect():
        if Model._pool is not None and not Model._pool.closed:
            # Warning: blocking method !!!
            Model._pool.close()

    @classmethod
    @tornado.gen.coroutine
    def execute(cls, *args):
        if cls._pool is None:
            raise IOError("Momoko not connected to DB instance!")
        cursor = yield cls._pool.execute(*args)
        if cursor.description:
            # if there is a description in the cursor then we can fetch it
            raise tornado.gen.Return(cursor.fetchall())
