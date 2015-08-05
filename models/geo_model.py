from pyspatialite import dbapi2 as db
from db import Session
from numpy import integer
from semantic_model import UvcModel, Uvc
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsApplication
from PyQt4.QtCore import pyqtSignal, QObject
from array import array
try:
    from PyQt4.Qt import QDate, QString
    
except ImportError:
    QString = str
#from processing.core.ProcessingConfig import ProcessingConfig
#import ctypes
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
    
    def insert(self, polygon):
        
        # creating a Cursor
        cur = self.connection.cursor()
        
        uvc = Uvc()
        cur.execute(UvcModel().insertStatement(uvc))
        
        polygon.uvc = uvc.id
        
        sql = self.insertStatement(polygon)
        
        cur.execute(sql)
        self.connection.commit()
        self.connection.close()

