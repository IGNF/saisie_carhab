# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from communication import popup, file_dlg, pluginDirectory,\
    no_work_lyr_msg, file_dlg
from utils import encode, decode
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
        self._valid = False
        self.import_killed = False
        if not os.path.exists(folder):
            self.make_folder()
        else:
            self._build()
            self.check_validity()
    
    @property
    def folder(self):
        return self._folder
    
    @property
    def layers(self):
        return self._layers
    
    @property
    def csv_files(self):
        return self._csv_files
    
    @property
    def valid(self):
        return self._valid
    
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
                else:
                    csvw = csv.DictWriter(open(file_path, "wb"), [encode(d.get('std_name')) for fld_n, d in file_fields], delimiter=b';')
                    csvw.writeheader()
            self._build()
            
    def kill_import(self):
        self.import_killed = True
        
    def import_data(self, wk_lyr):
        self.import_killed = False
        rowcount = 0
        progress_value = 0
        db = Db(wk_lyr.db_path)
        db.clean()
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
                    header = csv.DictReader(open(csv_path), delimiter=b';').fieldnames
                    with open(csv_path, "ab") as csv_file:
                        writer = csv.DictWriter(csv_file, header, delimiter=b';')
                        writer.writerows(csv_rows)
            pgbar.remove()
        popup("Export terminé.")

    def _build(self):
        std_names = [d.get('std_name') for tbl, d in DB_STRUCTURE if d.get('std_name')]
        self._csv_files = {os.path.splitext(f)[0]:os.path.join(self.folder, f) for f in os.listdir(self.folder)
            if os.path.splitext(f)[1] == '.csv' and os.path.splitext(f)[0] in std_names}
        self._layers = {os.path.splitext(f)[0]:os.path.join(self.folder, f) for f in os.listdir(self.folder)
            if os.path.splitext(f)[1] == '.shp' and os.path.splitext(f)[0] in std_names}
    
    def check_validity(self):
        missing_files = [d.get('std_name') for tbl, d in DB_STRUCTURE if d.get('std_name')
            if not d.get('std_name') in self.csv_files and not d.get('std_name') in self.layers]
        if len(missing_files) > 0:
            popup('Manque(nt) le(s) fichier(s) :\n - %s' % (',\n - '.join(missing_files)))
            return False
        
        for file_name, csv_path in self.csv_files.items() + self.layers.items():
            for tbl_name, tbl_info in DB_STRUCTURE:
                if tbl_info.get('std_name') == file_name:
                    try:
                        header = csv.DictReader(open(csv_path), delimiter=b';').fieldnames
                    except :
                        shp_lyr = QgsVectorLayer(csv_path, "", "ogr")
                        shpfil = shp_lyr.dataProvider()
                        header = [f.name() for f in shpfil.fields()]
                    std_names = [field_info.get('std_name') for field_n , field_info in tbl_info.get('fields')
                        if field_info.get('std_name')]
                    unique_cols = [field_info.get('std_name') for field_n , field_info in tbl_info.get('fields')
                        if field_info.get('std_name') and ('PRIMARY KEY' in field_info.get('type') or field_info.get('unique'))]
                    missing_fields = [field for field in std_names if not field in header]
                    if len(missing_fields) > 0:
                        popup('Champ(s) manquant(s) dans %s :\n - %s'
                            % (encode(file_name), ',\n - '.join(missing_fields)))
                        return False
            data = {}
            try:
                with open(csv_path, 'rb') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=b';')
                    for row in reader:
                        for key, value in row.items():
                            try:
                                data[key].append(value)
                            except KeyError:
                                data[key] = [value]
            except:
                 for feat in shp_lyr.getFeatures():
                        for field in feat.fields():
                            key = field.name()
                            value = feat.attribute(field.name())
                            try:
                                data[key].append(value)
                            except KeyError:
                                data[key] = [value]
            for col in unique_cols:
                if data.get(col) and len(set(data.get(col))) < len(data.get(col)):
                    popup('Les valeurs de la colonne "%s" ("%s") ne sont pas uniques.'
                        % (col, shp_name))
                    return False
        self._valid = True
        return True
