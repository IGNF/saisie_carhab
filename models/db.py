from pyspatialite import dbapi2 as db
import os
import shutil

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
        plugin_dir = os.path.dirname( os.path.abspath( __file__ ) )
        emptyDb = os.path.join(plugin_dir, 'empty.sqlite')
        shutil.copy(emptyDb, Session().dbPath)
