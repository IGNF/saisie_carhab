from pyspatialite import dbapi2 as db

from qgis.core import QgsVectorLayer

from PyQt4.QtCore import pyqtSignal, QObject, QThread

from semantic_model import UvcModel, Uvc
from geo_model import Polygon, PolygonModel

from carhab_layer_registry import *

#class Import(QObect):
class Import(QThread):
    
    finished = pyqtSignal(bool, float)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    def __init__(self, layer):
        super(Import, self).__init__()
        self.layer = layer

    def run(self ):
        print 'debut import'
        try:
            print 'dans try d\'import'
            self.connection = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
            self.layer.setValid(True)
            layercountfeat = self.layer.featureCount()
            # creating a Cursor
            cur = self.connection.cursor()
            #cur.execute("PRAGMA synchronous = OFF")
            invalidGeometries = []
            lastDecimal = 0
            # inserting some POLYGONs
            i = 0
            for feature in self.layer.getFeatures():
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
                            
                            cur.execute(PolygonModel().insertStatement(polygon))
                            i = i + 1
                    else:
                        wktGeom = feature.geometry().exportToWkt()
                        geom = "GeomFromText('"
                        geom += "" + wktGeom + ""
                        geom += "', 2154)"
                        polygon = Polygon(geom)
                        
                        uvc = Uvc()
                        cur.execute(UvcModel().insertStatement(uvc))
                        
                        polygon.uvc = cur.lastrowid
                        
                        cur.execute(PolygonModel().insertStatement(polygon))
                        
                        newDecimal = int(100*i/layercountfeat)
                        if lastDecimal != newDecimal:
                            
                            
                            self.progress.emit(100*i/layercountfeat)
                            
                            
                            lastDecimal = newDecimal
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
            del self.connection
            del self.filePath
        except:
            print 'exception'
            import traceback
            print traceback.format_exc()
            self.error.emit(traceback.format_exc())
            self.finished.emit(False, 1.0)

        else:
            
            self.finished.emit(True, 1.0)
