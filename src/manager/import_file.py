from pyspatialite import dbapi2 as db

from qgis.core import QgsVectorLayer
from qgis.utils import iface

from PyQt4.QtCore import pyqtSignal, QObject, QThread

from semantic_model import UvcModel, Uvc
from geo_model import Polygon, PolygonModel

from carhab_layer_registry import CarhabLayerRegistry

class Import(QObject):
    
    finished = pyqtSignal(bool, int)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    
    def __init__(self, layer):
        super(Import, self).__init__()
        
        self.layer = layer
        
        # To let aborting thread from outside
        self.stop = False
        

    def insertPolygon(self, geometry):
        
        # Convert geometry
        wktGeom = geometry.exportToWkt()
        geom = "GeomFromText('"
        geom += "" + wktGeom + ""
        geom += "', 2154)"
        
        polygon = Polygon(geom)
        uvc = Uvc()
        
        cur = self.connection.cursor()
        
        cur.execute(UvcModel().insertStatement(uvc)) # Insert an empty UVC before a polygon.
        polygon.uvc = cur.lastrowid #  Foreign key management.

        cur.execute(PolygonModel().insertStatement(polygon))

    def run(self ):

        try:

            if CarhabLayerRegistry.instance().currentLayer:
                
                # Connect to db.
                self.connection = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
                
                # To let import geos invalid geometries.
                self.layer.setValid(True)
                layerFeatCount = self.layer.featureCount()
                
                # Initialisation of useful variables to calculate progression.
                lastDecimal = 0
                i = 0
                
                for feature in self.layer.getFeatures():

                    if not self.stop:
                        
                        featGeom = feature.geometry()
                        
                        if featGeom.type() == 2: # Polygons case
                            
                            if featGeom.isMultipart(): # Split multipolygons
                                
                                for part in featGeom.asGeometryCollection():
                                
                                    if not part.isGeosValid(): # May be a problem...
                                        print 'part not valid :('
                                        
                                    self.insertPolygon(part)
                                    
                            else:
                                
                                self.insertPolygon(feature.geometry())
                            
                            # Calculate and emit new progression value (each percent only).
                            newDecimal = int(100*i/layerFeatCount)
                            if lastDecimal != newDecimal:
                                self.progress.emit(newDecimal)
                                lastDecimal = newDecimal
    
                            i = i + 1
                                
                    else: # Thread has been aborted
                        print 'abort'
                        # Cancel already done insert
                        self.connection.rollback()
                        self.finished.emit(False, 2)
                        break
                    
                self.connection.commit()
                self.connection.close()
                
                self.finished.emit(True, 0)
                
            else: # None current carhab layer (error code 1)
                self.finished.emit(False, 1)
            
        except:
            
            print 'exception'
            import traceback
            print traceback.format_exc()
            self.error.emit(traceback.format_exc())
            self.finished.emit(False, 0)
