from pyspatialite import dbapi2 as db

from carhab_layer_registry import *

class Polygon(object):
    def __init__(self, geometry):
        self.uvc = None
        self.geometry = geometry

class PolygonModel(object):
    
    def __init__(self):
        pass
    
    def insertStatement(self, polygon):
        sql = "INSERT INTO polygon (uvc, the_geom) "
        sql += "VALUES (%d, %s)" % (polygon.uvc, polygon.geometry)
        return sql
    
    def calculateSurface(self, polygon):
        
        conn = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        # creating a Cursor
        cur = conn.cursor()
        sql = "SELECT qsd(the_geom) FROM polygon WHERE id = " + str(polygon.id)
        cur.execute(sql)
        conn.commit()