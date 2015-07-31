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
from processing.core.ProcessingConfig import ProcessingConfig
import ctypes
class Polygon(object):
    def __init__(self, geometry):
        self.uvc = None
        self.geometry = geometry

class PolygonModel(QObject):
    
    finished = pyqtSignal(bool, float)
    error = pyqtSignal(str)
    progress = pyqtSignal()
    def __init__(self, filePath):
        super(PolygonModel, self).__init__()
        self.filePath = filePath
    
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
    
    
    def importFeaturesFromFile(self ):
        print 'debut import'
        try:
            print 'dans try d\'import'
            self.connection = db.connect(Session().dbPath)
            layer = QgsVectorLayer(self.filePath, 'geometry', "ogr")
            layer.setValid(True)
            
            # creating a Cursor
            cur = self.connection.cursor()
            
            invalidGeometries = []
            
            # inserting some POLYGONs
            i = 0
            for feature in layer.getFeatures():
                featGeom = feature.geometry()
                if featGeom.type() == 2:
                    if featGeom.isMultipart():
                        print 'multipart : '+str(feature.id())
                        for part in featGeom.asGeometryCollection():
                            if not part.isGeosValid():
                                print 'part not valid :('
                            wktGeom = part.exportToWkt()
                            geom = "GeomFromText('"
                            geom += "" + wktGeom + ""
                            geom += "', 2154)"
                            polygon = Polygon(geom)
                            
                            uvc = Uvc()
                            cur.execute(UvcModel().insertStatement(uvc))
                            
                            polygon.uvc = cur.lastrowid
                            
                            cur.execute(self.insertStatement(polygon))
                    else:
                        wktGeom = feature.geometry().exportToWkt()
                        geom = "GeomFromText('"
                        geom += "" + wktGeom + ""
                        geom += "', 2154)"
                        polygon = Polygon(geom)
                        
                        uvc = Uvc()
                        cur.execute(UvcModel().insertStatement(uvc))
                        
                        polygon.uvc = cur.lastrowid
                        
                        cur.execute(self.insertStatement(polygon))
                        self.progress.emit()
                        i = i + 1
                if not featGeom.isGeosValid():
                    # try to load the LWGEOM library
                    """libpath = ProcessingConfig.getSetting("LWGEOM_PATH_SETTING")
                    lib = ctypes.CDLL(libpath)
                    
                    wkb_in_buf = ctypes.create_string_buffer(feature.geometry().asWkb())
                    wkb_in = ctypes.cast(ctypes.addressof(wkb_in_buf), ctypes.POINTER(ctypes.c_ubyte))
                    wkb_size_in = ctypes.c_size_t(feature.geometry().wkbSize())
                    LW_PARSER_CHECK_NONE = ctypes.c_char(chr(0))    #define LW_PARSER_CHECK_NONE   0
                    lwgeom_in = lib.lwgeom_from_wkb( wkb_in, wkb_size_in, LW_PARSER_CHECK_NONE )
                    lib.lwgeom_make_valid.argtypes = [ctypes.POINTER(LWGEOM)]
                    lib.lwgeom_make_valid.restype = ctypes.POINTER(LWGEOM)
                    lwgeom_out = lib.lwgeom_make_valid( lwgeom_in )
                    print lwgeom_out"""
                    print 'not valid : ' + str(feature.id())
                    invalidGeometries.append(feature.id())
            self.connection.commit()
            self.connection.close()
            self.connection = None
            self.filePath = None
            self.finished.emit(True, 1.0)
            
            #QgsApplication.processEvents()
        except:
            #pass
            import traceback
            #self.error.emit(traceback.format_exc())
            self.finished.emit(False, invalidGeometries)
        #else:
        #    self.finished.emit(False, invalidGeometries)
            

class GBOX(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_ubyte),
        ("xmin", ctypes.c_double),
        ("xmax", ctypes.c_double),
        ("ymin", ctypes.c_double),
        ("ymax", ctypes.c_double),
        ("zmin", ctypes.c_double),
        ("zmax", ctypes.c_double),
        ("mmin", ctypes.c_double),
        ("mmax", ctypes.c_double)
    ]
class LWGEOM(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ubyte),
        ("flags", ctypes.c_ubyte),
        ("bbox", ctypes.POINTER(GBOX)),
        ("srid", ctypes.c_uint),
        ("data", ctypes.c_void_p),
    ]
