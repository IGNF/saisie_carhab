from pyspatialite import dbapi2 as db
from db import Session
from numpy import integer
from semantic_model import UvcModel, Uvc
try:
    from PyQt4.Qt import QDate, QString
except ImportError:
    QString = str

class ObjetGeo(object):
    def __init__(self):
        self.id = ObjetGeoModel().incrementId()
        self.uvc = integer

class ObjetGeoModel(object):
    def __init__(self):
        self.connection = db.connect(Session().dbPath)

    def incrementId(self):
        cur = self.connection.cursor()
        for row in cur.execute("SELECT max(id) FROM unite_vegetation_cartographiee"):
            if row[0]:
                return row[0] + 1
            else:
                return 1

    def insertStatement(self, objetGeo):

        sql = "INSERT INTO objet_geographique (uvc) "
        sql += "VALUES ('%d')" % (objetGeo.uvc)
        return sql

    def insert(self, objetGeo):
        # creating a Cursor
        cur = self.connection.cursor()
        sql = self.insertStatement(objetGeo)
        cur.execute(sql)
        self.connection.commit()
        self.connection.close()

class Polygon(ObjetGeo):
    def __init__(self, geometry):
        self.objetGeo = None
        self.geometry = geometry

class PolygonModel(object):
    
    def __init__(self):
        self.connection = db.connect(Session().dbPath)

    def insert(self, polygon):
        
        # creating a Cursor
        cur = self.connection.cursor()
        
        uvc = Uvc()
        cur.execute(UvcModel().insertStatement(uvc))
        
        objetGeo = ObjetGeo()
        objetGeo.uvc = uvc.id
        cur.execute(ObjetGeoModel().insertStatement(objetGeo))
        
        polygon.objetGeo = objetGeo.id
        
        sql = "INSERT INTO polygon (obj_geo, the_geom) "
        sql += "VALUES (%d, %s)" % (polygon.objetGeo, polygon.geometry)
        cur.execute(sql)
        self.connection.commit()
        self.connection.close()