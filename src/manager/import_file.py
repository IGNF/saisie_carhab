# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from PyQt4.QtCore import pyqtSignal, QObject

from carhab_layer_manager import CarhabLayerRegistry
from db_manager import DbManager
from recorder import Recorder

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
        # To force 2D geometry
        if len(wktGeom.split('Z')) > 1:
            wktGeom = wktGeom.split('Z')[0] + wktGeom.split('Z')[1]
            wktGeom = wktGeom.replace(" 0,", ",")
            wktGeom = wktGeom.replace(" 0)", ")")
        geom = "GeomFromText('"
        geom += wktGeom
        geom += "', 2154)"

        geomObj = {}
        geomObj['the_geom'] = geom
        
        db = DbManager(CarhabLayerRegistry.instance().getCurrentCarhabLayer().dbPath)
        
        r = Recorder(db, 'polygon')
        r.input(geomObj)
        
        db.commit()
        db.close()

    def run(self ):
        print 'run worker'
        try:
            print 'begin try'
            if CarhabLayerRegistry.instance().getCurrentCarhabLayer():
                
                # Connect to db.
                self.db = DbManager(CarhabLayerRegistry.instance().getCurrentCarhabLayer().dbPath)
                
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
                                        print 'part not valid'
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
                        # Cancel inserts already done
                        self.db.conn.rollback()
                        self.finished.emit(False, 2)
                        break
                self.db.commit()
                self.db.close()
                self.finished.emit(True, 0)
            else: # None current carhab layer (error code 1)
                self.finished.emit(False, 1)
            
        except:
            print 'exception'
            import traceback
            print traceback.format_exc()
            self.error.emit(traceback.format_exc())
            self.finished.emit(False, 0)
