from pyspatialite import dbapi2 as db
import os.path

class Session(object):
    class __Session:
        def __init__(self):
            self.val = ''
        def __str__(self):
            return `self` + self.val

    instance = None

    def __new__(c):
        if not Session.instance:
            Session.instance = Session.__Session()
        return Session.instance

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, dbPath):
        return setattr(self.instance, attr, dbPath)

class Db(object):
    def __init__(self, path):
        Session().dbPath = path
        if not os.path.exists(path):
            self.initDb()
            
        
    def initDb(self):
        conn = db.connect(Session().dbPath)
        # creating a Cursor
        cur = conn.cursor()
        
        # initializing Spatial MetaData
        # using v.2.4.0 this will automatically create
        # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        sql = 'SELECT InitSpatialMetadata()'
        cur.execute(sql)
        
        f = open('db/db_script.sql')
        sql = f.read()

        sql_array = sql.split(";")
        for sql_statement in sql_array[:-1]:
            cur.execute(sql_statement)
        
        conn.commit()
        conn.close()

class Dbgen:
    def __init__(self):
        if os.path.exists('empty.sqlite'):
            os.remove('empty.sqlite')
        Db('empty.sqlite')

Dbgen()