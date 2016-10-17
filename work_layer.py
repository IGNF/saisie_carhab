# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
# Prepare processing framework 
sys.path.append(':/plugins/processing')
from processing.core.Processing import Processing
Processing.initialize()
from processing.tools import *
import os.path
import time

from qgis.core import (QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI,
    QgsCoordinateReferenceSystem, QgsProject, QgsLayerTreeGroup, QgsLayerTreeModel)
from qgis.utils import iface
from PyQt4.QtCore import QThread, pyqtSignal, QObject
from config import DB_STRUCTURE, PROJECT_NAME, CRS_CODE
from db_manager import Db, Recorder
from communication import pluginDirectory, popup, ProgressBarMsg, file_dlg

def run_import():
    sel_file = file_dlg()
    if sel_file:
        # Set corresponding layer.
        settings = QSettings()
        oldProjValue = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")
        qgisLayer = QgsVectorLayer(sel_file, 'geometry', "ogr")
        qgisLayer.setCrs(QgsCoordinateReferenceSystem(2154, QgsCoordinateReferenceSystem.EpsgCrsId))
        settings.setValue("/Projections/defaultBehaviour", oldProjValue)
        # Carhab layer should not overlaps itself. Calculate difference between layers.
        diffLayer = self.makeDifference(qgisLayer)

        if diffLayer:
            if diffLayer.featureCount() == 0:
                popup(('Emprise de la couche à importer déjà peuplée '
                       'dans la couche Carhab : aucune entité ajoutée.'))
            else:
                # Import only difference between layers.
                self.makeImport(diffLayer)
        else:
            popup(('Erreur inconnue : aucune entité ajoutée.'))
    
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


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
        
        db = Db(WorkLayerRegistry.instance().current_work_layer().db_path)
        
        r = Recorder(db, 'polygon')
        r.input(geomObj)
        
        db.commit()
        db.close()

    def run(self ):
        print 'run worker'
        try:
            print 'begin try'
            if WorkLayerRegistry.instance().current_work_layer():
                
                # Connect to db.
                self.db = Db(WorkLayerRegistry.instance().current_work_layer().db_path)
                
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

class ImportLayer(object):
    """
    /***************************************************************************
     ImportLayer Class
            
            Do the stuff import features from shapefile to carhab layer.
     ***************************************************************************/
     """    
    def makeDifference(self, importLayer):
        # Launch difference processing.
        processingResult = general.runalg("qgis:difference", importLayer, iface.mapCanvas().currentLayer(), None)
        # Get the tmp shp path corresponding to the difference processing result layer
        differenceLayerPath = processingResult['OUTPUT']
        return self.createQgisVectorLayer(differenceLayerPath)

    def closeImport(self, success, code):
        if not success:
            if code == 0:
                popup('Erreur inconnue : aucune entité ajoutée.')
            elif code == 1:
                popup('Pas de couche carhab initialisée : aucune entité ajoutée.')
            elif code == 2:
                popup('Import annulé : aucune entité ajoutée')
        if self.progressBar:
            self.progressBar.setValue(100)
            self.progressValue = 100
            iface.messageBar().popWidget(self.msgBarItem)
        self.canvas.currentLayer().updateExtents()
        self.canvas.setExtent(self.canvas.currentLayer().extent())
        self.canvas.refresh()

class WorkLayer(QgsLayerTreeGroup):
    def __init__(self, db_path):
        name = PROJECT_NAME + '_' + os.path.splitext(os.path.basename(db_path))[0]
        super(QgsLayerTreeGroup, self).__init__(name, checked=True)
        
        self._db_path = db_path
        self._id = time.strftime("%Y%m%d%H%M%S")
        
        spatial_tbls = [(tbl_info[0], tbl_info[1].get('fields')) for tbl_info in DB_STRUCTURE if tbl_info[1].get('spatial')]
        for tbl_name, tbl_flds in spatial_tbls:
            # Retrieve layer from provider.
            uri = QgsDataSourceURI()
            uri.setDatabase(db_path)
            geom_column = [f[0] for f in tbl_flds if f[1].get('spatial')][0]
            uri.setDataSource('', tbl_name, geom_column)
            
            layer = QgsVectorLayer(uri.uri(), tbl_name, 'spatialite')
            layer.setCrs(QgsCoordinateReferenceSystem(CRS_CODE, QgsCoordinateReferenceSystem.EpsgCrsId))
        
            # Add layer to map (False to add to group) and to layer group
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            self.addLayer(layer)
            layer.setCustomProperty('workLayerOwner', self._id)
        self.setCustomProperty('isWorkLayer', True)
            
                    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    @property
    def db_path(self):
        return self._db_path
    
    def import_geom(self, lyr):
        # Import only difference between layers.
        pgbar = ProgressBarMsg()
        pgbar.add_to_iface()
        thread = QThread()
        worker = Import(lyr)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(pgbar.update)
        thread.start()
        thread.wait()
    
    def last_db_version(self):
        db = Db(os.path.join(pluginDirectory, "empty.sqlite"))
        return db.version()
    
@Singleton
class WorkLayerRegistry(object):

    def __init__(self):
        self._work_layers = {}
        QgsProject.instance().layerTreeRoot().willRemoveChildren.connect(self._clean)
    
    @property
    def work_layers(self):
        return self._work_layers
    
    def init_work_layers(self):
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            wk_lyr_id = lyr.customProperty("workLayerOwner", None)
            if wk_lyr_id and not wk_lyr_id in self.work_layers:
                work_lyr = WorkLayer(lyr.dataProvider().dataSourceUri().split("dbname=")[1].split(" table")[0])
                work_lyr.id = wk_lyr_id
                self._work_layers[work_lyr.id] = work_lyr
            
    def _clean(self, node, idx_from, idx_to):
        # nodes in legend that will be removed, filter on layer groups :
        rm_nodes = [node.children()[idx_from + i] for i in range(idx_to - idx_from + 1) if isinstance(node.children()[idx_from + i], WorkLayer)]
        for r in rm_nodes:
            print r
        # corresponding work layers :
        rm_wkl = [self.work_layers_by_name(rm_node.name())[0] for rm_node in rm_nodes]
        for wk_lyr in rm_wkl:
            self._work_layers.pop(wk_lyr.id, None)
        
    def work_layers_by_name(self, work_lyr_name):
        return [wl for wl in self.work_layers.values() if wl.name() == work_lyr_name]
    
    def work_layer(self, work_lyr_id):
        res = [wl for wl_id, wl in self.work_layers.items() if wl_id == work_lyr_id]
        if res:
            return res[0]
    
    def current_work_layer(self):
        c_lyr = iface.mapCanvas().currentLayer()
        if c_lyr:
            c_wk_lyr_id = c_lyr.customProperty("workLayerOwner", None)
            return self.work_layer(c_wk_lyr_id)

    def add_work_lyr(self, work_lyr):
        QgsProject.instance().layerTreeRoot().addChildNode(work_lyr)
        self._work_layers[work_lyr.id] = work_lyr

    def remove_work_layer(self, work_lyr):
        QgsProject.instance().layerTreeRoot().removeChildNode(work_lyr)
        self._work_layers.pop(work_lyr.id, None)
