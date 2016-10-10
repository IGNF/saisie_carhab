# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from utils_job import popup, execFileDialog, pluginDirectory,\
    no_carhab_lyr_msg, encode, execFileDialog
from carhab_layer_manager import CarhabLayerRegistry
from PyQt4.QtGui import QFileDialog, QLineEdit, QPushButton
from PyQt4.QtCore import QVariant, Qt, QThread, QObject
from PyQt4.uic import loadUi

from functools import partial
from qgis.utils import iface
import os
import time
from qgis.core import QgsVectorFileWriter, QgsVectorLayer, QgsField, QgsDataSourceURI, QgsFields, QgsField, QGis, QgsApplication, QgsMapLayerRegistry
from qgis.gui import QgsMessageBarItem
import shutil
from config import Config
from recorder import Recorder
from db_manager import DbManager
from job_manager import JobManager
from import_layer import ImportLayer
from import_file import Import
import csv
class ImportJob(QThread):
    def __init__(self, lyr):
        super(ImportJob, self).__init__()
        self.lyr = lyr
        self.progress_bar = loadUi(os.path.join(pluginDirectory, "progress_bar.ui"))
    def run(self):
        print 'into thread'
        print self.lyr
        wkr = Import(self.lyr)
        self.msg_bar_item = QgsMessageBarItem('', 'Import des entités', self.progress_bar)
        iface.messageBar().pushItem(self.msg_bar_item)
        wkr.progress.connect(self.update_progress_bar)
        wkr.run()

#        update_map = {feat.id(): {idx: feat['uvc']} for feat in lyr.getFeatures()}
#        this_lyr.changeAttributeValues(update_map)
    def update_progress_bar(self, val):
        self.progress_bar.setValue(val)
        
    
class ImportFSE(object):
    """
    /***************************************************************************
     Import FSE Class
            
            Convert FSE layer (csv) to carhab layer format (sqlite).
     **************************************************************************/
     """
    def __init__(self):
        """ Constructor. """
        self.ui = loadUi(os.path.join(pluginDirectory, 'form_import_fse.ui'))
        
    def run(self):
        '''Specific stuff at tool activating.'''
        self.ui.setWindowModality(2)
        
        iface.addDockWidget(Qt.AllDockWidgetAreas, self.ui)
        btn = self.ui.findChildren(QPushButton)
        for b in btn:
            try:
                b.clicked.disconnect()
            except:
                pass
            p = partial(self.select_file, b.objectName()[0:-4])
            b.clicked.connect(p)
        valid_b = self.ui.findChild(QPushButton, 'valid_btn')
        
        try:
            valid_b.clicked.disconnect()
        except:
            pass
        valid_b.clicked.connect(self.valid)
        
    def select_file(self, file_name):
        if file_name in ['polygon', 'polyline', 'point']:
            path = execFileDialog('*.shp')
        else:
            path = execFileDialog('*.csv')
        if path:
            line_edt = self.ui.findChild(QLineEdit, file_name)
            line_edt.setText(path)
            
    def valid(self):
        iface.removeDockWidget(self.ui)
        sqlite = execFileDialog('*.sqlite', 'Créer une couche de sortie', 'save')
        wk_lyr = JobManager().create_carhab_lyr(sqlite)
        for lyr in wk_lyr.getQgisLayers():
            if lyr.name().endswith('_polygon'):
                this_lyr = lyr
                iface.mapCanvas().setCurrentLayer(lyr)
        shp_path = self.ui.findChild(QLineEdit, this_lyr.name().split('_')[-1]).text()
        lyr = ImportLayer().createQgisVectorLayer(shp_path)
#        thread = QThread()
        worker = ImportJob(lyr)
#        worker.moveToThread(thread)
#        thread.start()
#        thread.wait()
#        worker.run()
        worker.start()
        print 'worker started'
        worker.wait()
        print 'finished'
#        msg = ''
#        miss_files = []
#        for l in self.ui.findChildren(QLineEdit):
#            if not l.text():
#                miss_files.append(l.objectName())
#        if not False in [typ in miss_files for typ in ['polygon', 'polyline', 'point']]:
#            msg += 'Il faut renseigner au moins une couche géométrique.\n'
#        for mf in miss_files:
#            if not mf in ['polygon', 'polyline', 'point']:
#                msg += mf + '\n'
#        if msg:
#            popup('Fichiers non renseignés :\n\n' + msg)
#            return
#        else:
#            sqlite = execFileDialog('*.sqlite', 'Créer une couche de sortie', 'save')
#            wk_lyr = JobManager().create_carhab_lyr(sqlite)
#            iface.removeDockWidget(self.ui)
#            for lyr in wk_lyr.getQgisLayers():
#                if lyr.name().endswith('_polygon'):
#                    this_lyr = lyr
#                    iface.mapCanvas().setCurrentLayer(lyr)
#            shp_path = self.ui.findChild(QLineEdit, this_lyr.name().split('_')[-1]).text()
#            lyr = iface.addVectorLayer(shp_path, 'tmp', 'ogr')
#            iface.setActiveLayer(lyr)
#            lyr.setSelectedFeatures([f.id() for f in iface.mapCanvas().currentLayer().getFeatures()])
#            iface.actionCopyFeatures().trigger()
#            iface.setActiveLayer(this_lyr)
#            this_lyr.startEditing()
#            iface.actionPasteFeatures().trigger()
#            this_lyr.commitChanges()
#            
#            update_map = {feat.id(): {idx: feat['uvc']} for feat in lyr.getFeatures()}
#            this_lyr.changeAttributeValues(update_map)
#            
#            QgsMapLayerRegistry.instance().removeMapLayer(lyr.id())
#            this_lyr.setSelectedFeatures([])
            
            
class ExportFSE(object):
    """
    /***************************************************************************
     Import FSE Class
            
            Convert FSE layer (csv) to carhab layer format (sqlite).
     **************************************************************************/
     """
    def __init__(self):
        """ Constructor. """
        pass
    
                    
    def run(self):
        '''Specific stuff at tool activating.'''
        
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        if not cur_carhab_lyr:
            no_carhab_lyr_msg()
            return
        csv_dir = QFileDialog.getExistingDirectory(None,
                                                'Select a folder:',
                                                None,
                                                QFileDialog.ShowDirsOnly)
        if csv_dir:
            now = time.strftime("%Y-%m-%d-%H%M%S")
            directory = os.path.join(csv_dir, cur_carhab_lyr.getName()+'_'+now)
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            for tbl_name, desc in Config.DB_STRUCTURE:
                file_name = desc.get('std_name')
                tbl_fields = desc.get('fields')
                if file_name:
                    if not desc.get('spatial'):
                        csv_name = file_name if file_name.endswith('.csv') else file_name + '.csv'
                        csv_path = os.path.join(directory, csv_name)
                        field_names = [row[1].get('std_name') for row in tbl_fields if row[1].get('std_name')]
                        db = DbManager(cur_carhab_lyr.dbPath)
                        r = Recorder(db, tbl_name)
                        tbl_rows = r.select_all()
                        csv_rows = []
                        for tbl_row in tbl_rows:
                            csv_row = {}
                            for dbf, value in tbl_row.items():
                                for field in desc.get('fields'):
                                    if dbf == field[0] and field[1].get('std_name'):
                                        csv_row[encode(field[1].get('std_name'))] = encode(value)
                                        break
                            csv_rows.append(csv_row)

                        with open(csv_path, "wb") as csv_file:
                            writer = csv.DictWriter(csv_file, field_names)
                            writer.writeheader()
                            writer.writerows(csv_rows)
                    else:
                        for vlyr in cur_carhab_lyr.getQgisLayers():
                            vlyr_tbl = QgsDataSourceURI(vlyr.dataProvider().dataSourceUri()).table()
                            if tbl_name == vlyr_tbl:
                                shp_name = file_name if file_name.endswith('.shp') else file_name + '.shp'
                                shp_path = os.path.join(directory, shp_name)
                                QgsVectorFileWriter.writeAsVectorFormat(vlyr, shp_path, 'utf-8', None)
                                shp_lyr = QgsVectorLayer(shp_path, "", "ogr")
                                shapefile = shp_lyr.dataProvider()
                                features = shapefile.getFeatures()
                                attrs_to_del = []
                                for attr, attr_desc in tbl_fields:
                                    std_attr = attr_desc.get('std_name')
                                    if not std_attr == attr:
                                        if std_attr:
                                            cur_field = shapefile.fields().field(attr)
                                            new_field = QgsField(cur_field)
                                            new_field.setName(std_attr)
                                            shapefile.addAttributes([new_field])
                                            for feat in features:
                                                idx = shapefile.fields().indexFromName(std_attr)
                                                update_map = {feat.id(): {idx: feat[attr]}}
                                                shapefile.changeAttributeValues(update_map)
                                        attrs_to_del.append(shapefile.fields().indexFromName(attr))
                                shapefile.deleteAttributes(attrs_to_del)
            popup('Export effectué')