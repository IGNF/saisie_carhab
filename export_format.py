# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from communication import popup, file_dlg, pluginDirectory,\
    no_work_lyr_msg, file_dlg
from utils import encode, decode
from PyQt4.QtGui import QFileDialog, QLineEdit, QPushButton
from PyQt4.QtCore import Qt, QThread, pyqtSignal, QObject, QVariant
from PyQt4.uic import loadUi
from functools import partial
from qgis.utils import iface
import os
import time
from qgis.core import QgsVectorFileWriter, QgsVectorLayer, QgsField, QgsDataSourceURI, QgsFields, QGis, QgsCoordinateReferenceSystem, QgsFeature, QgsApplication
from qgis.gui import QgsMessageBarItem, QgsMessageBar
from config import DB_STRUCTURE, get_no_spatial_tables, get_spatial_tables, get_table_info, CRS_CODE
from db_manager import Db, Recorder
import csv
from utils import log
from communication import ProgressBarMsg, popup, question


            
class ExportStd(QObject):
    """
    /***************************************************************************
     Import FSE Class
            
            Convert FSE layer (csv) to carhab layer format (sqlite).
     **************************************************************************/
     """
     
     
    finished_worker = pyqtSignal(object)
    
    def __init__(self, folder):
        """ Constructor. """
        super(ExportStd, self).__init__()
        self._folder = folder
        self._layers = {}
        self._csv_files = {}
        self._validation_code = 2 # 2 : valid, 1: non critical errors, 0: critical errors
        self._valid = True
        self.import_killed = False
#    
    def create(self):
        if not os.path.exists(self._folder):
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
            pgbar.update(100)
            pgbar.remove()
        popup("Export terminé.")

    def _build(self):
        std_names = [d.get('std_name') for tbl, d in DB_STRUCTURE if d.get('std_name')]
        self._csv_files = {os.path.splitext(f)[0]:os.path.join(self.folder, f) for f in os.listdir(self.folder)
            if os.path.splitext(f)[1] == '.csv' and os.path.splitext(f)[0] in std_names}
        self._layers = {os.path.splitext(f)[0]:os.path.join(self.folder, f) for f in os.listdir(self.folder)
            if os.path.splitext(f)[1] == '.shp' and os.path.splitext(f)[0] in std_names}
    
    def worker_error(self, exception_string):
        log('Worker thread raised an exception:\n{0}'.format(exception_string))
        
    def worker_finished(self, success, code):
        # clean up the worker and thread
        self.c_thread.quit()
        self.c_thread.wait()
        self.c_thread.deleteLater()
        # remove widget from message bar
        self.pgbar.remove()
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
        else:
            if code == 2:
                self._valid = True
            elif code == 1:
                if question('Erreurs détéctées lors de la validation !',
                        'Consulter le rapport pour plus de détail %s\nContinuer ?'
                        % (os.path.join(pluginDirectory, 'rapport_erreurs_import.csv'))):
                    self._valid = True
                else:
                    self._valid = False
            elif code == 0:
                popup('Erreurs détéctées lors de la validation. Import non effectué.'
                    'Consulter le rapport pour plus de détail %s'
                    % (os.path.join(pluginDirectory, 'rapport_erreurs_import.csv')))
                self._valid = False
            self.finished_worker.emit(self)
            
    def check_validity(self):
        self.pgbar = ProgressBarMsg('Validation des données...')
        self.pgbar.add_to_iface()
        # start the worker in a new thread
        worker = Validation(self.layers, self.csv_files)
        thread = QThread()
        self.pgbar.aborted.connect(worker.kill)
        worker.moveToThread(thread)
        worker.finished.connect(self.worker_finished)
        worker.error.connect(self.worker_error)
#        worker._report_error.connect(self._report_error)
        worker.progress.connect(self.pgbar.update)
        thread.started.connect(worker.run)
        thread.start()
#        worker.run()
        self.c_thread = thread
        self.worker = worker
                
class Validation(QObject):
    
    finished = pyqtSignal(bool, int)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    _report_error = pyqtSignal(dict)
    
    def __init__(self, layers, csv_files):
        super(Validation, self).__init__()
        
        self.layers = layers
        self.csv_files = csv_files
        
        # To let aborting thread from outside
        self.killed = False
        self.no_report = True
    
    def _report_error(self, error_obj):
        with open(os.path.join(pluginDirectory, 'rapport_erreurs_import.csv'), 'ab') as report:
            fieldnames = ['type', 'table', 'colonne', 'valeur', 'erreur', 'action']
            writer = csv.DictWriter(report, fieldnames=fieldnames, delimiter=b';')
            if self.no_report:
                writer.writeheader()
                self.no_report = False
            writer.writerow(error_obj)
   
    def run(self ):
        try:
            try:
                if os.path.exists(os.path.join(pluginDirectory, 'rapport_erreurs_import.csv')):
                    os.remove(os.path.join(pluginDirectory, 'rapport_erreurs_import.csv'))
            except WindowsError, err:
                popup(str(err))
                raise WindowsError, err
            self._validation_code = 2
            type_error = {'CRITICAL':0,'WARNING':1}
            missing_files = [d.get('std_name') for tbl, d in DB_STRUCTURE if d.get('std_name')
                if not d.get('std_name') in self.csv_files and not d.get('std_name') in self.layers]
            for table in missing_files:
                err_msg = b'Fichier manquant'
                act_msg = 'Import annulé'.encode('utf-8')
                error = {'type': 'CRITICAL', 'table': table, 'colonne': None,'valeur': None,'erreur': err_msg, 'action': act_msg}
                self._report_error(error)
#                self._report_error.emit(error)
                if self._validation_code > type_error.get(error.get('type')):
                    self._validation_code = type_error.get(error.get('type'))
            self.progress.emit(10)
            uvc_values = []
            syntax_uvc = []
            syntax_sf = []
            sf_uvc = []
            sf_ids = []
            uvc_ids = []
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
                        mandatory_cols = [field_info.get('std_name') for field_n , field_info in tbl_info.get('fields')
                            if field_info.get('std_name') and field_info.get('mandatory')]
                        col_types = {field_info.get('std_name'): field_info.get('type') for field_n, field_info in tbl_info.get('fields')
                            if field_info.get('std_name')}
                        missing_fields = [field for field in std_names if not field in header]
                        for field in missing_fields:
                            err_msg = 'Champ manquant'
                            act_msg = b'Import annulé'
                            error = {'type': 'CRITICAL', 'table': file_name, 'colonne': field,'valeur': None,'erreur': err_msg, 'action': act_msg}
                            self._report_error(error)
#                            self._report_error.emit(error)
                            if self._validation_code > type_error.get(error.get('type')):
                                self._validation_code = type_error.get(error.get('type'))

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
                        err_msg = b"Valeurs égales dans champ avec unicité requise"
                        act_msg = b'Import annulé'
                        error = {'type': 'CRITICAL', 'table': file_name, 'colonne': col,'valeur': None,'erreur': err_msg, 'action': act_msg}
                        self._report_error(error)
#                        self._report_error.emit(error)
                        if self._validation_code > type_error.get(error.get('type')):
                            self._validation_code = type_error.get(error.get('type'))
                for col in mandatory_cols:
                    if data.get(col) and '' in data.get(col):
                        err_msg = "Valeur(s) manquante(s) dans champ obligatoire"
                        act_msg = b'Import annulé'
                        error = {'type': 'CRITICAL', 'table': file_name, 'colonne': col,'valeur': None,'erreur': err_msg, 'action': act_msg}
                        self._report_error(error)
#                        self._report_error.emit(error)
                        if self._validation_code > type_error.get(error.get('type')):
                            self._validation_code = type_error.get(error.get('type'))
                for col, values in data.items():
                    for val in values:
                        if val and col_types.get(col):
                            if 'INTEGER' in col_types.get(col):
                                try:
                                    if not float(val) == int(float(val)):
                                        raise ValueError
                                except ValueError:
                                    err_msg = "Type incorrect : entier requis"
                                    act_msg = b'Import annulé'
                                    error = {'type': 'CRITICAL', 'table': file_name, 'colonne': col,'valeur': val,'erreur': err_msg, 'action': act_msg}
                                    self._report_error(error)
#                                    self._report_error.emit(error)
                                    if self._validation_code > type_error.get(error.get('type')):
                                        self._validation_code = type_error.get(error.get('type'))
                            elif 'REAL' in col_types.get(col):
                                try:
                                    float(val)
                                except ValueError:
                                    err_msg = b"Type incorrect : réel requis"
                                    act_msg = b'Import annulé'
                                    error = {'type': 'CRITICAL', 'table': file_name, 'colonne': col,'valeur': val,'erreur': err_msg, 'action': act_msg}
                                    self._report_error(error)
#                                    self._report_error.emit(error)
                                    if self._validation_code > type_error.get(error.get('type')):
                                        self._validation_code = type_error.get(error.get('type'))

                    if col == 'uvc' and file_name in ['St_SIG_polygon','St_SIG_polyline','St_SIG_point']:
                        uvc_values += data.get(col)
                self.progress.emit(10 + int(75/len(self.csv_files.items() + self.layers.items())))

                if file_name == 'St_UniteCarto_Description':
                    if data.get('identifiantUniteCartographiee'):
                        uvc_ids = data.get('identifiantUniteCartographiee')
                if file_name == 'St_CompoSigmaFacies':
                    if data.get('identifiantCompoSigmaFacies'):
                        sf_ids = data.get('identifiantCompoSigmaFacies')
                    if data.get('identifiantUniteCartographiee'):
                        sf_uvc = data.get('identifiantUniteCartographiee')
                if file_name == 'St_CompoReelleSyntaxons':
                    if data.get('identifiantUniteCartographiee'):
                        syntax_sf = data.get('identifiantCompoSigmaFacies')
                    if data.get('identifiantUniteCartographiee'):
                        syntax_uvc = data.get('identifiantUniteCartographiee')
            geom_tables = 'St_SIG_polygon / St_SIG_polyline / St_SIG_point'
            if len(set(uvc_values)) < len(uvc_values):
                err_msg = b'Plusieurs entités géométriques pointent vers la même UVC (vérifier que "uvc" est unique dans les trois tables géométriques'
                act_msg = b'Import annulé'
                error = {'type': 'CRITICAL', 'table': geom_tables, 'colonne': 'uvc','valeur': None,'erreur': err_msg, 'action': act_msg}
                self._report_error(error)
#                self._report_error.emit(error)
                if self._validation_code > type_error.get(error.get('type')):
                    self._validation_code = type_error.get(error.get('type'))

            self.progress.emit(80)
            for s in syntax_uvc:
                if s not in uvc_ids:
                    err_msg = b'Valeur de lien non présente dans la table parente ("St_UniteCarto_Description"."identifiantUniteCartographiee")'
                    act_msg = b'Import annulé'
                    error = {'type': 'CRITICAL', 'table': 'St_CompoReelleSyntaxons', 'colonne': 'identifiantUniteCartographiee','valeur': s,'erreur': err_msg, 'action': act_msg}
                    self._report_error(error)
#                    self._report_error.emit(error)
                    if self._validation_code > type_error.get(error.get('type')):
                        self._validation_code = type_error.get(error.get('type'))

            self.progress.emit(85)
            for s in syntax_sf:
                if s not in sf_ids:
                    err_msg = b'Valeur de lien non présente dans la table parente ("St_CompoSigmaFacies"."identifiantCompoSigmaFacies")'
                    act_msg = b'Import annulé'
                    error = {'type': 'CRITICAL', 'table': 'St_CompoReelleSyntaxons', 'colonne': 'identifiantCompoSigmaFacies','valeur': s,'erreur': err_msg, 'action': act_msg}
                    self._report_error(error)
#                    self._report_error.emit(error)
                    if self._validation_code > type_error.get(error.get('type')):
                        self._validation_code = type_error.get(error.get('type'))

            self.progress.emit(90)
            for s in sf_uvc:
                if s not in uvc_ids:
                    err_msg = b'Valeur de lien non présente dans la table parente ("St_UniteCarto_Description"."identifiantUniteCartographiee")'
                    act_msg = b'Import annulé'
                    error = {'type': 'CRITICAL', 'table': 'St_CompoSigmaFacies', 'colonne': 'identifiantUniteCartographiee','valeur': s,'erreur': err_msg, 'action': act_msg}
                    self._report_error(error)
#                    self._report_error.emit(error)
                    if self._validation_code > type_error.get(error.get('type')):
                        self._validation_code = type_error.get(error.get('type'))

            self.progress.emit(95)
            for s in uvc_values:
                if str(int(s)) not in uvc_ids:
                    err_msg = b'Valeur de lien non présente dans la table parente ("St_UniteCarto_Description"."identifiantUniteCartographiee")'
                    act_msg = b'Import annulé'
                    error = {'type': 'CRITICAL', 'table': geom_tables, 'colonne': 'uvc','valeur': s,'erreur': err_msg, 'action': act_msg}
                    self._report_error(error)
#                    self._report_error.emit(error)
                    if self._validation_code > type_error.get(error.get('type')):
                        self._validation_code = type_error.get(error.get('type'))
            if self.killed is False:
                self.progress.emit(100)
                self.finished.emit(True, self._validation_code)
        except:
            import traceback
            self.error.emit(traceback.format_exc())
            self.finished.emit(False, 0)
            
    def kill(self):
        self.killed = True
    
