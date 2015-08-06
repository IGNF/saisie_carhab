from pyspatialite import dbapi2 as db

from qgis.core import QgsVectorLayer
from qgis.utils import iface

from PyQt4.QtCore import pyqtSignal, QObject, QThread

from semantic_model import UvcModel, Uvc
from geo_model import Polygon, PolygonModel

from carhab_layer_registry import CarhabLayerRegistry

class Import(QObject):
    
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    def __init__(self, layer):
        super(Import, self).__init__()
        self.layer = layer
        self.stop = False
        
    def run(self ):

        try:

            self.connection = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
            
            self.layer.setValid(True)
            layerFeatCount = self.layer.featureCount()
            
            # creating a Cursor
            cur = self.connection.cursor()

            lastDecimal = 0
            # inserting some POLYGONs
            i = 0
            for feature in self.layer.getFeatures():
                if not self.stop:
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
                            
                            newDecimal = int(100*i/layerFeatCount)
                            if lastDecimal != newDecimal:
                                self.progress.emit(newDecimal)
                                lastDecimal = newDecimal
    
                            i = i + 1
                else:
                    print 'abort'
                    self.connection.rollback()
                    self.finished.emit(True)
                    break
            self.connection.commit()
            self.connection.close()
            
        except:
            print 'exception'
            import traceback
            print traceback.format_exc()
            self.error.emit(traceback.format_exc())
            self.finished.emit(False)

        else:
            
            self.finished.emit(True)
