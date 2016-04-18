# -*- coding: utf-8 -*-
from utils_job import popup, execFileDialog, pluginDirectory
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
     ***************************************************************************/
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
     ***************************************************************************/
     """
    def __init__(self):
        """ Constructor. """
        pass
        
    def run(self):
        '''Specific stuff at tool activating.'''
        
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        print dir_
        print cur_carhab_lyr.getName()
        now = time.strftime("%Y-%m-%d-%H%M%S")
        directory = os.path.join(dir_, cur_carhab_lyr.getName() + '_' + now)
        print directory
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        for tbl, desc in Config.DB_STRUCTURE.items():
            print tbl
            csv_name = None
            if tbl == 'uvc':
                csv_name = 'St_UniteCarto_Description.csv'
            elif tbl == 'sigmaf':
                csv_name = 'St_CompoSigmaFacies.csv'
            elif tbl == 'composyntaxon':
                csv_name = 'St_CompoReelleSyntaxons.csv'
            if csv_name:
                field_names = []
                print desc
                for value in desc:
                    field_names.append(value[2])
                with open(os.path.join(directory, csv_name), "wb") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=field_names)
                    writer.writeheader()
                    db = DbManager(cur_carhab_lyr.dbPath)
                    r = Recorder(db, tbl)
                    tbl_content = r.select_all()
                    print tbl_content
                    for tbl_row in tbl_content:
                        print tbl_row
                        csv_row = {}
                        for field_desc in desc:
                            print value
                            value = tbl_row.get(field_desc[0])
                            csv_row[field_desc[2]] = value
                        print 'csv_row : ' + str(csv_row)
                        writer.writerow(csv_row)
         
        for vlyr in cur_carhab_lyr.getQgisLayers():
            shp_name = 'St_SIG_' + vlyr.name().split('_')[-1].title()
            shp_path = os.path.join(directory, shp_name)
            QgsVectorFileWriter.writeAsVectorFormat(vlyr,
                                                    shp_path,
                                                    'utf-8',
                                                    None,
                                                    'ESRI Shapefile')