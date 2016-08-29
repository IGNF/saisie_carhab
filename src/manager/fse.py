# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from utils_job import popup, execFileDialog, pluginDirectory,\
    no_carhab_lyr_msg, encode
from carhab_layer_manager import CarhabLayerRegistry
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QVariant
import os
import time
from qgis.core import QgsVectorFileWriter, QgsVectorLayer, QgsField, QgsDataSourceURI, QgsFields, QgsField, QGis
import shutil
from config import Config
from recorder import Recorder
from db_manager import DbManager
import csv

class ImportFSE(object):
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
        popup("Import FSE : c\'est pour bientôt !")
        
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
                                                'C:\\',
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