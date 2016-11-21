# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
# Prepare processing framework 
sys.path.append(':/plugins/processing')
from processing.core.Processing import Processing
Processing.initialize()
from processing.tools import *
import os
import csv
import time
from qgis.core import (QgsApplication, QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI,
    QgsCoordinateReferenceSystem, QgsProject, QgsLayerTreeGroup, QgsMessageLog, QgsRectangle)
from qgis.gui import QgsMessageBar, QgsMapCanvasLayer
from qgis.utils import iface
from PyQt4.QtCore import QThread, pyqtSignal, QObject, QSettings
from PyQt4.QtGui import QFileDialog
from config import PROJECT_NAME, CRS_CODE, get_spatial_column, get_spatial_tables, DB_STRUCTURE
from db_manager import Db, Recorder
from utils import Singleton, log
from export_format import ExportStd
from legend_actions import CheckCompletion
from communication import pluginDirectory, ProgressBarMsg, file_dlg, no_work_lyr_msg, popup, typ_lyr_msg, question

def run_import():
    c_wk_lyr = WorkLayerRegistry.instance().current_work_layer()
    if not c_wk_lyr:
        no_work_lyr_msg()
        return
    sel_file = file_dlg()
    if sel_file:
        settings = QSettings()
        old_proj_value = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")
        layer = QgsVectorLayer(sel_file, 'geometry', "ogr")
        layer.setCrs(QgsCoordinateReferenceSystem(2154, QgsCoordinateReferenceSystem.EpsgCrsId))
        settings.setValue("/Projections/defaultBehaviour", old_proj_value)
        c_wk_lyr = WorkLayerRegistry.instance().current_work_layer()
        c_wk_lyr.import_layer(layer)
            
def run_import_std():
    c_wk_lyr = WorkLayerRegistry.instance().current_work_layer()
    if not c_wk_lyr:
        no_work_lyr_msg()
        return
    sel_dir = QFileDialog.getExistingDirectory(None, 'Sélectionner un dossier...', None, QFileDialog.ShowDirsOnly)
    if sel_dir:
        c_wk_lyr.import_std(sel_dir)
#        std = ExportStd(sel_dir)
#        std.finished_worker.connect(c_wk_lyr.import_std)
#        std.create()
    
def run_export():
    c_wk_lyr = WorkLayerRegistry.instance().current_work_layer()
    if not c_wk_lyr:
        no_work_lyr_msg()
        return
    sel_dir = QFileDialog.getExistingDirectory(None, 'Sélectionner un dossier...', None, QFileDialog.ShowDirsOnly)
    if sel_dir:
        c_wk_lyr.export(sel_dir)
        

class Import(QObject):
    
    finished = pyqtSignal(bool, int)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    
    def __init__(self, layer, dest_tbl):
        super(Import, self).__init__()
        
        self.layer = layer
        self.table = dest_tbl
        self.geom_col = get_spatial_column(dest_tbl)
        
        # To let aborting thread from outside
        self.killed = False
    
    def insert_feat(self, obj, geom, recorder):
        
        # Convert geometry
        wkt = geom.exportToWkt()
        # To force 2D geometry
        if len(wkt.split('Z')) > 1:
            wkt = wkt.split('Z')[0] + wkt.split('Z')[1]
            wkt = wkt.replace(" 0,", ",")
            wkt = wkt.replace(" 0)", ")")
        geom = "GeomFromText('"
        geom += wkt
        geom += "', "+unicode(CRS_CODE)+")"

#        geom_obj = {}
        obj[self.geom_col] = geom
        
        return recorder.input(obj)

    def run(self ):
        try:  
            # Connect to db.
            db = Db(WorkLayerRegistry.instance().current_work_layer().db_path)
            r = Recorder(db, self.table)
            # To let import geos invalid geometries.
            self.layer.setValid(True)
            layerFeatCount = self.layer.featureCount()
            if layerFeatCount > 0:
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
                        feat_obj = dict(zip([fld.name() for fld in feature.fields()], feature.attributes()))
                        if featGeom.isMultipart(): # Split multipolygons
                            for part in featGeom.asGeometryCollection():
                                if not part.isGeosValid(): # May be a problem...
                                    raise Exception('part not valid')
                                res = self.insert_feat(feat_obj, featGeom, r)
                        else:
                            res = self.insert_feat(feat_obj, feature.geometry(), r)
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
    

class ImportCsv(QObject):
    
    finished = pyqtSignal(bool, int)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    
    def __init__(self, csv_file, dest_tbl):
        super(ImportCsv, self).__init__()
        
        self.csv_file = csv_file
        self.table = dest_tbl
        
        # To let aborting thread from outside
        self.killed = False
    
    def insert_row(self, obj, recorder):
        return recorder.input(obj)

    def run(self ):
        try:  
            # Connect to db.
            db = Db(WorkLayerRegistry.instance().current_work_layer().db_path)
            db.execute('BEGIN')
            r = Recorder(db, self.table)
            r.delete_all()
            row_count = len(list(csv.DictReader(open(self.csv_file, 'rb'), delimiter=b';'))) - 1 # minus header row
            if row_count > 0:
                with open(self.csv_file, 'rb') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=b';')

                    # Initialisation of useful variables to calculate progression.
                    lastDecimal = 0
                    i = 0

                    tbl_flds = [tbl_d.get('fields') for tbl_n, tbl_d in DB_STRUCTURE
                        if tbl_n == self.table][0]
                    corr_flds = {field_d.get('std_name'):field_n for field_n, field_d in tbl_flds if field_d.get('std_name')}
                    for row in reader:
                        if self.killed is True: # Thread has been aborted
                            db.conn.rollback()
                            self.finished.emit(False, 1)
                            break
                        else:
                            data = {corr_flds.get(r).decode('utf-8'):v.decode('utf-8')
                                if v else None for r, v in row.items() if corr_flds.get(r)}
                            res = self.insert_row(data, r)
                            if not res == 1:
                                raise Exception(res)

                            # Calculate and emit new progression value (each percent only).
                            newDecimal = int(100*i/row_count)
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
    
    finished_worker = pyqtSignal(bool)
    
    def __init__(self, db_path):
        name = PROJECT_NAME + '_' + os.path.splitext(os.path.basename(db_path))[0]
        super(WorkLayer, self).__init__(name, checked=True)
        self._db_path = db_path
        self._id = time.strftime("%Y%m%d%H%M%S")
        self._qgis_layers = {}
        for tbl_name in get_spatial_tables():
            # Retrieve layer from provider.
            uri = QgsDataSourceURI()
            uri.setDatabase(self._db_path)
            geom_column = get_spatial_column(tbl_name)
            uri.setDataSource('', tbl_name, geom_column)

            layer = QgsVectorLayer(uri.uri(), tbl_name, 'spatialite')
            layer.setCrs(QgsCoordinateReferenceSystem(CRS_CODE, QgsCoordinateReferenceSystem.EpsgCrsId))

            # Add layer to map (False to add to group) and to layer group
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            self.addLayer(layer)
            layer.setCustomProperty('workLayer', self._id)
            self._qgis_layers[layer.name()] = layer
        self.setCustomProperty('workLayer', self._id)
        self.setCustomProperty('dbPath', self._db_path)
        
        self.layers_to_add_stack = []
        self.csv_to_add_stack = {}
        self.finished_worker.connect(self.on_finish_import)
        
                    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    @property
    def db_path(self):
        return self._db_path
    @property
    def qgis_layers(self):
        return self._qgis_layers
    
    def import_layer(self, src_lyr):
        for lyr in self.qgis_layers.values():
            if lyr.geometryType() == src_lyr.geometryType():
                dest_lyr = lyr
                break
        self.pgbar = ProgressBarMsg('Import des entités')
        self.pgbar.add_to_iface()
        # start the worker in a new thread
        tbl = QgsDataSourceURI(dest_lyr.dataProvider().dataSourceUri()).table()
        worker = Import(src_lyr, tbl)
        thread = QThread()
        self.pgbar.aborted.connect(worker.kill)
        worker.moveToThread(thread)
        worker.finished.connect(self.worker_finished)
        worker.error.connect(self.worker_error)
        worker.progress.connect(self.pgbar.update)
        thread.started.connect(worker.run)
        thread.start()
        self.c_thread = thread
        self.worker = worker
    
    def import_csv(self, csv_file):
        csv_name = csv_file[0]
        csv_path = csv_file[1]
        tbl = [(tbl_n, tbl_d) for tbl_n, tbl_d in DB_STRUCTURE if tbl_d.get('std_name') == csv_name][0]
        self.pgbar = ProgressBarMsg('Import de %s' % (csv_name))
        self.pgbar.add_to_iface()
        # start the worker in a new thread
        worker = ImportCsv(csv_path, tbl[0])
        thread = QThread()
        self.pgbar.aborted.connect(worker.kill)
        worker.moveToThread(thread)
        worker.finished.connect(self.worker_finished)
        worker.error.connect(self.worker_error)
        worker.progress.connect(self.pgbar.update)
        thread.started.connect(worker.run)
        thread.start()
#        worker.run()
        self.c_thread = thread
        self.worker = worker
        
    def import_std(self, sel_dir):
        self.std = ExportStd(sel_dir)
        self.std.finished_worker.connect(self.import_std_valid)
        self.std.create()
    
    def import_std_valid(self, std):
        if std.valid:
            for lyr_path in std.layers.values():
                layer = QgsVectorLayer(lyr_path, '', 'ogr')
                self.layers_to_add_stack.append(layer)
            self.csv_to_add_stack = std.csv_files.items()
            self.on_finish_import()
            
    def on_finish_import(self, success=True):
        if success:
            if len(self.layers_to_add_stack) > 0:
                lyr = self.layers_to_add_stack[0]
                self.layers_to_add_stack.pop(0)
                self.import_layer(lyr)
            elif len(self.csv_to_add_stack) > 0:
                csv_file = self.csv_to_add_stack[0]
                self.csv_to_add_stack.pop(0)
                self.import_csv(csv_file)
            else:
                self.zoom_to_extent()
                
            
    def worker_error(self, exception_string):
        log('Worker thread raised an exception:\n{0}'.format(exception_string))
        
    def worker_finished(self, success, code):
        # clean up the worker and thread
        self.c_thread.quit()
        self.c_thread.wait()
        self.c_thread.deleteLater()
        if not success:
            # notify the user that something went wrong
            if code == 0:
                iface.messageBar().pushMessage('Une erreur est survenue ! Voir le journal des messages.',
                    level=QgsMessageBar.CRITICAL,
                    duration=3)
            elif code == 1:
                iface.messageBar().pushMessage('Import annulé : aucune entité ajoutée.',
                    level=QgsMessageBar.WARNING,
                    duration=3)
        # remove widget from message bar
        self.pgbar.remove()
        self.finished_worker.emit(success)
        
    def zoom_to_extent(self):
            lyr = iface.activeLayer()
            if lyr:
                lyr.updateExtents()
                iface.mapCanvas().setExtent(lyr.extent())
                lyr.triggerRepaint()
                iface.mapCanvas().refresh()

    def last_db_version(self):
        db = Db(os.path.join(pluginDirectory, "empty.sqlite"))
        return db.version()

    def export(self, folder):
        now = time.strftime("%Y%m%d%H%M%S")
        export_folder = os.path.join(folder, self.name() + now)
        std_format = ExportStd(export_folder)
        std_format.create()
        std_format.import_data(self)
        
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
        c_lyr = iface.activeLayer()
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