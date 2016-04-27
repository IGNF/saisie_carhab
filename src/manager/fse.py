# -*- coding: utf-8 -*-
from utils_job import popup, execFileDialog, pluginDirectory, no_carhab_lyr_msg
from carhab_layer_manager import CarhabLayerRegistry
from PyQt4.QtGui import QFileDialog
import os
import time
from qgis.core import QgsVectorFileWriter
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

            for tbl, desc in Config.DB_STRUCTURE.items():
                csv_name = None
                if tbl == 'uvc':
                    csv_name = 'St_UniteCarto_Description.csv'
                elif tbl == 'sigmaf':
                    csv_name = 'St_CompoSigmaFacies.csv'
                elif tbl == 'composyntaxon':
                    csv_name = 'St_CompoReelleSyntaxons.csv'
                if csv_name:
                    field_names = []
                    for value in desc:
                        field_names.append(value[2])
                    with open(os.path.join(directory, csv_name), "wb") as csv_file:
                        writer = csv.DictWriter(csv_file, fieldnames=field_names)
                        writer.writeheader()
                        db = DbManager(cur_carhab_lyr.dbPath)
                        r = Recorder(db, tbl)
                        tbl_content = r.select_all()
                        for tbl_row in tbl_content:
                            csv_row = {}
                            for field_desc in desc:
                                value = tbl_row.get(field_desc[0])
                                if isinstance(value, str) or isinstance(value, unicode):
                                    csv_row[field_desc[2].encode('utf8')] = value.encode('utf8')
                                else:
                                    csv_row[field_desc[2].encode('utf8')] = value
                            writer.writerow(csv_row)

            for vlyr in cur_carhab_lyr.getQgisLayers():
                shp_name = 'St_SIG_' + vlyr.name().split('_')[-1].title()
                shp_path = os.path.join(directory, shp_name)
                QgsVectorFileWriter.writeAsVectorFormat(vlyr,
                                                        shp_path,
                                                        'utf-8',
                                                        None,
                                                        'ESRI Shapefile')

            popup('Export effectué')