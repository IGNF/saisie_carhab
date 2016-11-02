# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from communication import popup, file_dlg, pluginDirectory,\
    no_work_lyr_msg, file_dlg
from utils import encode
from PyQt4.QtGui import QFileDialog, QLineEdit, QPushButton
from PyQt4.QtCore import Qt, QThread, QVariant
from PyQt4.uic import loadUi

from functools import partial
from qgis.utils import iface
import os
import time
from qgis.core import QgsVectorFileWriter, QgsVectorLayer, QgsField, QgsDataSourceURI, QgsFields, QGis, QgsCoordinateReferenceSystem, QgsFeature
from qgis.gui import QgsMessageBarItem
from config import DB_STRUCTURE, get_no_spatial_tables, get_spatial_tables, get_table_info, CRS_CODE
from db_manager import Db, Recorder
import csv
from utils import log
from communication import ProgressBarMsg, popup


            
class ExportStd(object):
    """
    /***************************************************************************
     Import FSE Class
            
            Convert FSE layer (csv) to carhab layer format (sqlite).
     **************************************************************************/
     """
    def __init__(self, folder):
        """ Constructor. """
        self._folder = folder
        self._layers = {}
        self._csv_files = {}
        self.import_killed = False
        if not os.path.exists(folder):
            self.make_folder()
        else:
            self.check_conformity()
    
    @property
    def folder(self):
        return self._folder
    
    @property
    def layers(self):
        return self._layers
    
    @property
    def csv_files(self):
        return self._csv_files
    
    def make_folder(self):
        os.mkdir(self.folder)
        fld_typ_map = {
            'TEXT': QVariant.String,
            'INTEGER': QVariant.Int,
            'REAL': QVariant.Double,
            'POINT': QGis.WKBPoint,
            'LINESTRING': QGis.WKBMultiLineString,
            'POLYGON': QGis.WKBMultiPolygon,
        }
        for tbl_name, desc in DB_STRUCTURE:
            std_name = desc.get('std_name')
            if std_name:
                sfx = '.shp' if desc.get('spatial') else '.csv'
                file_path = os.path.join(self.folder, std_name + sfx)

                tbl_fields = get_table_info(tbl_name).get('fields')
                file_fields = [(fld_n, d) for fld_n, d in tbl_fields if d.get('std_name') or d.get('spatial')]
                if desc.get('spatial'):
                    fields = QgsFields()
                    for fld_n, fld_info in file_fields:
                        fld_typ = fld_typ_map.get(fld_info.get('type').split(' ')[0])
                        if fld_info.get('spatial'):
                            geom_typ = fld_typ
                        else:
                            fields.append(QgsField(fld_info.get('std_name'), fld_typ))
                    crs = QgsCoordinateReferenceSystem.EpsgCrsId
                    proj = QgsCoordinateReferenceSystem(CRS_CODE, crs)
                    shp_writer = QgsVectorFileWriter(file_path, "utf-8", fields, geom_typ, proj, "ESRI Shapefile")
                    if shp_writer.hasError() != QgsVectorFileWriter.NoError:
                        log("Error when creating shapefile: " +  shp_writer.errorMessage())
                    self._layers[desc.get('std_name')] = file_path
                else:
                    csvw = csv.DictWriter(open(file_path, "wb"), [encode(d.get('std_name')) for fld_n, d in file_fields])
                    csvw.writeheader()
                    self._csv_files[desc.get('std_name')] = file_path
                    
    def kill_import(self):
        self.import_killed = True
        
    def import_data(self, wk_lyr):
        self.import_killed = False
        rowcount = 0
        progress_value = 0
        db = Db(wk_lyr.db_path)
        for tbl in DB_STRUCTURE:
            r = Recorder(db, tbl[0])
            rowcount += r.count_rows()
        if not rowcount == 0:
            pgbar = ProgressBarMsg('Export en cours...')
            pgbar.aborted.connect(self.kill_import)
            pgbar.add_to_iface()
            for tbl_name, desc in DB_STRUCTURE:
                if desc.get('spatial'):
                    shp_lyr = QgsVectorLayer(self.layers.get(desc.get('std_name')), "", "ogr")
                    shapefile = shp_lyr.dataProvider()
                    layer = wk_lyr.qgis_layers.get(tbl_name)
                    std_features = []
                    for feat in layer.getFeatures():
                        if self.import_killed is False:
                            std_feat = QgsFeature(shapefile.fields())
                            std_feat.setGeometry(feat.geometry())
                            for fld_n, fld_d in desc.get('fields'):
                                if fld_d.get('std_name'):
                                    std_feat.setAttribute(fld_d.get('std_name'), feat[fld_n])
                                    std_features.append(std_feat)
                                    progress_value += 1
                                    pgbar.update(int(100*progress_value/rowcount))
                    shapefile.addFeatures(std_features)
                else:
                    r = Recorder(db, tbl_name)
                    tbl_rows = r.select_all()
                    csv_rows = []
                    for row in tbl_rows:
                        if self.import_killed is False:
                            csv_row = {}
                            for db_field, value in row.items():
                                for field, field_d in desc.get('fields'):
                                    if field == db_field and field_d.get('std_name'):
                                        csv_row[encode(field_d.get('std_name'))] = encode(value)
                                        break
                            progress_value += 1
                            pgbar.update(int(100*progress_value/rowcount))
                            csv_rows.append(csv_row)
                    csv_path = self.csv_files.get(desc.get('std_name'))
                    header = csv.DictReader(open(csv_path)).fieldnames
                    with open(csv_path, "ab") as csv_file:
                        writer = csv.DictWriter(csv_file, header)
                        writer.writerows(csv_rows)
            pgbar.remove()
        popup("Export terminé.")

    def check_conformity(self):
        conformity = True
        return conformity
