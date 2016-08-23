# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from utils_job import popup, execFileDialog, pluginDirectory,\
    no_carhab_lyr_msg, encode
from carhab_layer_manager import CarhabLayerRegistry
from PyQt4.QtGui import QFileDialog
import os
import time
from qgis.core import QgsVectorFileWriter, QgsVectorLayer, QgsField
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
        dir_ = QFileDialog.getExistingDirectory(None,
                                                'Select a folder:',
                                                'C:\\',
                                                QFileDialog.ShowDirsOnly)
        if dir_:
            now = time.strftime("%Y-%m-%d-%H%M%S")
            directory = os.path.join(dir_, cur_carhab_lyr.getName() + '_' + now)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            tbls = {
                        'uvc': 'St_UniteCarto_Description.csv',
                        'sigmaf': 'St_CompoSigmaFacies.csv',
                        'composyntaxon': 'St_CompoReelleSyntaxons.csv',
                    }
            for tbl_name, desc in Config.DB_STRUCTURE.items():
                if tbl_name in tbls:
                    csv_name = tbls[tbl_name]
                    field_names = [encode(d[2]) for d in desc if d[2]]
                    csv_path = os.path.join(directory, csv_name)
                    with open(csv_path, "wb") as csv_file:
                        writer = csv.DictWriter(csv_file, field_names)
                        writer.writeheader()
                        db = DbManager(cur_carhab_lyr.dbPath)
                        r = Recorder(db, tbl_name)
                        tbl_content = r.select_all()
                        for tbl_row in tbl_content:
                            csv_row = {}
                            for d in desc:
                                header_val = d[2]
                                value = tbl_row.get(d[0])
                                if header_val and value:
                                    csv_row[encode(header_val)] = encode(value)
                            writer.writerow(csv_row)

            for vlyr in cur_carhab_lyr.getQgisLayers():
                shp_name = 'St_SIG_' + vlyr.name().split('_')[-1].title()
                shp_path = os.path.join(directory, shp_name)
                QgsVectorFileWriter.writeAsVectorFormat(vlyr,
                                                        shp_path,
                                                        'utf-8',
                                                        None,
                                                        'ESRI Shapefile')
                shp_lyr = QgsVectorLayer(shp_path + '.shp', "", "ogr")
                shapefile = shp_lyr.dataProvider()
                attr_names = ['id', 'lgd_compl', 'pct_facies']
                attrs_to_del = [shapefile.fieldNameIndex(n) for n in attr_names]
                shapefile.deleteAttributes(attrs_to_del)
                
            popup('Export effectué')