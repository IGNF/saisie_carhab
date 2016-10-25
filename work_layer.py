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
    QgsCoordinateReferenceSystem, QgsProject, QgsLayerTreeGroup, QgsMessageLog)
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from PyQt4.QtCore import QThread, pyqtSignal, QObject, QSettings
from config import DB_STRUCTURE, PROJECT_NAME, CRS_CODE
from db_manager import Db, Recorder
from utils import Singleton, log
from communication import pluginDirectory, ProgressBarMsg, file_dlg, no_work_lyr_msg

def run_import():
    sel_file = file_dlg()
    if sel_file:
        settings = QSettings()
        old_proj_value = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")
        layer = QgsVectorLayer(sel_file, 'geometry', "ogr")
        layer.setCrs(QgsCoordinateReferenceSystem(2154, QgsCoordinateReferenceSystem.EpsgCrsId))
        settings.setValue("/Projections/defaultBehaviour", old_proj_value)
        c_wk_lyr = WorkLayerRegistry.instance().current_work_layer()
        if c_wk_lyr:
            c_wk_lyr.import_layer(layer)
        else:
            no_work_lyr_msg()
            

class Import(QObject):
    
    finished = pyqtSignal(bool, int)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    
    def __init__(self, layer):
        super(Import, self).__init__()
        
        self.layer = layer
        
        # To let aborting thread from outside
        self.killed = False
    
    def insertPolygon(self, geometry, recorder):
        
        # Convert geometry
        wktGeom = geometry.exportToWkt()
        # To force 2D geometry
        if len(wktGeom.split('Z')) > 1:
            wktGeom = wktGeom.split('Z')[0] + wktGeom.split('Z')[1]
            wktGeom = wktGeom.replace(" 0,", ",")
            wktGeom = wktGeom.replace(" 0)", ")")
        geom = "GeomFromText('"
        geom += wktGeom
        geom += "', "+unicode(CRS_CODE)+")"

        geomObj = {}
        geomObj['the_geom'] = geom
        return recorder.input(geomObj)

    def run(self ):
        try:  
            # Connect to db.
            db = Db(WorkLayerRegistry.instance().current_work_layer().db_path)
            r = Recorder(db, 'polygon')
            # To let import geos invalid geometries.
            self.layer.setValid(True)
            layerFeatCount = self.layer.featureCount()

            # Initialisation of useful variables to calculate progression.
            lastDecimal = 0
            i = 0
            db.execute('BEGIN')
            for feature in self.layer.getFeatures():
                if self.killed is True: # Thread has been aborted
                    # Cancel inserts already done
                    db.conn.rollback()
                    self.finished.emit(False, 1)
                    break
                else:
                    featGeom = feature.geometry()
                    if featGeom.type() == 2: # Polygons case
                        if featGeom.isMultipart(): # Split multipolygons
                            for part in featGeom.asGeometryCollection():
                                if not part.isGeosValid(): # May be a problem...
                                    print 'part not valid'
                                res = self.insertPolygon(part, r)
                        else:
                            res = self.insertPolygon(feature.geometry(), r)
                        if not res == 1:
                            raise Exception(res)
                            
                        # Calculate and emit new progression value (each percent only).
                        newDecimal = int(100*i/layerFeatCount)
                        if lastDecimal != newDecimal:
                            self.progress.emit(newDecimal)
                            lastDecimal = newDecimal
                        i = i + 1
            if self.killed is False:
                db.commit()
                db.close()
                self.progress.emit(100)
                self.finished.emit(True, 0)
        except:
            import traceback
            self.error.emit(traceback.format_exc())
            self.finished.emit(False, 0)
            
    def kill(self):
        self.killed = True
    
class WorkLayer(QgsLayerTreeGroup):
    def __init__(self, db_path):
        name = PROJECT_NAME + '_' + os.path.splitext(os.path.basename(db_path))[0]
        super(WorkLayer, self).__init__(name, checked=True)
        self._db_path = db_path
        self._id = time.strftime("%Y%m%d%H%M%S")

        spatial_tbls = [(tbl_info[0], tbl_info[1].get('fields')) for tbl_info in DB_STRUCTURE if tbl_info[1].get('spatial')]
        for tbl_name, tbl_flds in spatial_tbls:
            # Retrieve layer from provider.
            uri = QgsDataSourceURI()
            uri.setDatabase(self._db_path)
            geom_column = [f[0] for f in tbl_flds if f[1].get('spatial')][0]
            uri.setDataSource('', tbl_name, geom_column)

            layer = QgsVectorLayer(uri.uri(), tbl_name, 'spatialite')
            layer.setCrs(QgsCoordinateReferenceSystem(CRS_CODE, QgsCoordinateReferenceSystem.EpsgCrsId))

            # Add layer to map (False to add to group) and to layer group
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            self.addLayer(layer)
            layer.setCustomProperty('workLayer', self._id)
        self.setCustomProperty('workLayer', self._id)
        self.setCustomProperty('dbPath', self._db_path)
                    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    @property
    def db_path(self):
        return self._db_path
    
    def import_layer(self, lyr):
        # Import only difference between layers.
        self.pgbar = ProgressBarMsg()
        self.pgbar.add_to_iface()
        # start the worker in a new thread
        worker = Import(lyr)
        thread = QThread()
        self.pgbar.aborted.connect(worker.kill)
        worker.moveToThread(thread)
        worker.finished.connect(self.worker_finished)
        worker.error.connect(self.worker_error)
        worker.progress.connect(self.pgbar.update)
        thread.started.connect(worker.run)
        thread.start()
        self.thread = thread
        self.worker = worker
        
    def worker_error(self, exception_string):
        QgsMessageLog.logMessage('Worker thread raised an exception:\n'.format(exception_string), level=QgsMessageLog.CRITICAL)
        
    def worker_finished(self, success, code):
        # clean up the worker and thread
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        if not success:
            # notify the user that something went wrong
            if code == 0:
                iface.messageBar().pushMessage('Une erreur est survenue ! Voir le journal des messages.', level=QgsMessageBar.CRITICAL, duration=3)
            elif code == 1:
                iface.messageBar().pushMessage('Import annulé : aucune entité ajoutée.', level=QgsMessageBar.WARNING, duration=3)
        # remove widget from message bar
        self.pgbar.remove()
        iface.mapCanvas().currentLayer().updateExtents()
        iface.mapCanvas().setExtent(iface.mapCanvas().currentLayer().extent())
        iface.mapCanvas().currentLayer().triggerRepaint()
        iface.mapCanvas().refresh()
        
    
    def last_db_version(self):
        db = Db(os.path.join(pluginDirectory, "empty.sqlite"))
        return db.version()

@Singleton
class WorkLayerRegistry:
    def __init__(self):
        self._work_layers = {}
        QgsProject.instance().layerTreeRoot().willRemoveChildren.connect(self._on_remove_children)

    @property
    def work_layers(self):
        return self._work_layers

    def _on_remove_children(self, node, idx_from, idx_to):
        # nodes in legend that will be removed, filter on layer groups :
        rm_nodes = [node.children()[idx_from + i] for i in range(idx_to - idx_from + 1) if type(node.children()[idx_from + i]) == WorkLayer]
        # corresponding work layers :
        rm_wkl = [self.work_layers_by_name(rm_node.name())[0] for rm_node in rm_nodes if self.work_layers_by_name(rm_node.name())]
        for wk_lyr in rm_wkl:
            self._work_layers.pop(wk_lyr.id, None)
        
    
    def init_work_layers(self):
        self._work_layers = {}
        for grp_name in iface.legendInterface().groups():
            tree_grp = QgsProject.instance().layerTreeRoot().findGroup(grp_name)
            wk_lyr_id = tree_grp.customProperty("workLayer", None)
            if wk_lyr_id and not wk_lyr_id in self._work_layers:
                work_lyr = WorkLayer(tree_grp.customProperty("dbPath"))
                work_lyr.id = wk_lyr_id
                self._work_layers[work_lyr.id] = work_lyr
   
    def work_lyr_exists(self, file_path):
        return len([wk_lyr for wk_lyr in self.work_layers.values() if wk_lyr.db_path == file_path]) > 0
            
    def work_layers_by_name(self, work_lyr_name):
        return [wl for wl in self.work_layers.values() if wl.name() == work_lyr_name]
    
    def work_layer(self, work_lyr_id):
        return [wl for wl_id, wl in self.work_layers.items() if wl_id == work_lyr_id][0]
    
    def current_work_layer(self):
        c_lyr = iface.mapCanvas().currentLayer()
        if c_lyr:
            c_wk_lyr_id = c_lyr.customProperty("workLayer", None)
            if c_wk_lyr_id:
                return self.work_layer(c_wk_lyr_id)

    def add_work_lyr(self, work_lyr):
        if work_lyr.db_path in [wl.db_path for wl in self._work_layers.values()]:
            grp = QgsProject.instance().layerTreeRoot().findGroup(work_lyr.name())
            self._work_layers.pop(grp.customProperty('workLayer'))
            QgsProject.instance().layerTreeRoot().removeChildNode(grp)
        QgsProject.instance().layerTreeRoot().addChildNode(work_lyr)
        self._work_layers[work_lyr.id] = work_lyr