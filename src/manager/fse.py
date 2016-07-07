# -*- coding: utf-8 -*-
from utils_job import popup, execFileDialog, pluginDirectory, no_carhab_lyr_msg
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
    
    def encode_utf8(self, value):
        string = value
        if isinstance(value, str) or isinstance(value, unicode):
            string = value.encode('utf8')
        return string
    
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
                    for d in desc:
                        if d[2]:
                            field_names.append(self.encode_utf8(d[2]))
                    csv_path = os.path.join(directory, csv_name)
                    with open(csv_path, "wb") as csv_file:
                        writer = csv.DictWriter(csv_file, field_names)
                        writer.writeheader()
                        db = DbManager(cur_carhab_lyr.dbPath)
                        r = Recorder(db, tbl)
                        tbl_content = r.select_all()
                        for tbl_row in tbl_content:
                            csv_row = {}
                            for d in desc:
                                header_val = self.encode_utf8(d[2])
                                print header_val
                                if header_val:
                                    value = self.encode_utf8(tbl_row.get(d[0]))
                                    csv_row[header_val] = value
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
                attr_to_del = []
                attr_to_del.append(shapefile.fieldNameIndex('id'))
                attr_to_del.append(shapefile.fieldNameIndex('lgd_compl'))
                shapefile.deleteAttributes(attr_to_del)
                
            popup('Export effectué')