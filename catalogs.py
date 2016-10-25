# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv

from os import path

from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui import QPushButton, QLineEdit
from PyQt4.uic import loadUi

from functools import partial

from qgis.utils import iface

from communication import pluginDirectory, file_dlg, popup
from utils import decode
from config import CATALOG_STRUCTURE


class Catalog(object):
    """ Class managing catalogs opening action"""
    
    def __init__(self):
        self.ui = loadUi(path.join(pluginDirectory, 'form_catalogs.ui'))
        self.catalog = {
            'serie': None,
            'sigmaf': None,
            'serie_sigmaf': None,
            'syntaxon': None,
            'sigmaf_syntaxon': None,
        }
    
    def run(self):
        self.ui.setWindowModality(2)
        iface.addDockWidget(Qt.AllDockWidgetAreas, self.ui)
        btn = [self.ui.findChild(QPushButton, c + '_btn') for c in self.catalog]
        line_edt = [self.ui.findChild(QLineEdit, c) for c in self.catalog]
        for l in line_edt:
            s = QSettings()
            cat = s.value('catalogs')
            if cat:
                l.setText(cat.get(l.objectName()))
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
            
    def select_file(self, catalog_name):
        catalog_path = file_dlg('*.csv')
        self.catalog[catalog_name] = catalog_path
        if catalog_path:
            line_edt = self.ui.findChild(QLineEdit, catalog_name)
            line_edt.setText(catalog_path)
    
    def check_data(self):
        msg = ''
        for cat_name, cat_path in self.catalog.items():
            fl_name = path.basename(cat_path)
            if not path.exists(cat_path) and not path.isfile(cat_path):
                msg += 'Chemin de fichier invalide pour {}.\n'.format(fl_name)
                continue
            with open(cat_path, 'rb') as cat_file:
                reader = csv.reader(cat_file, delimiter=b';')
                headers = reader.next()
                file_ctnt = []
                for row in reader:
                    file_ctnt.append(row)
            if len(headers) < 2:
                msg += 'Délimiteur ";" requis dans {}.\n'.format(fl_name)
                continue
            if CATALOG_STRUCTURE.get('data').get(cat_name):
                for field in CATALOG_STRUCTURE.get('data').get(cat_name):
                    if not field in headers:
                        msg += 'Champ "{}" manquant dans le fichier "{}".\n'\
                            .format(field, fl_name)
            else:
                cds = [i[2] for i in CATALOG_STRUCTURE.get('links').get(cat_name)]
                for cd in cds:
                    if not cd in headers:
                        msg += 'Champ "{}" manquant dans le fichier "{}".\n'\
                            .format(cd, fl_name)
            i = 2
            for row in file_ctnt:
                diff = len(row) - len(headers)
                if diff > 0:
                    msg += '{} colonne(s) en trop dans {} à la ligne {}.\n'\
                        .format(unicode(diff), cat_name, unicode(i))
                elif diff < 0:
                    msg += '{} colonne(s) manquante(s) dans {} à la ligne {}.\n'\
                        .format(unicode(-diff), fl_name, unicode(i))
                i += 1
                    
            
        if msg:
            popup(msg)
            return False
        else:
            return True
        
    def valid(self):
        msg = ''
        for cat_name in self.catalog:
            disp_path_wdgt = self.ui.findChild(QLineEdit, cat_name)
            if disp_path_wdgt.text():
                self.catalog[cat_name] = disp_path_wdgt.text()
            else:
                msg += cat_name + '\n'
        if msg:
            popup('Catalogues non renseignés :\n\n' + msg)
            return
        elif self.check_data():
            s = QSettings()
            s.setValue('catalogs', self.catalog)
            iface.removeDockWidget(self.ui)
        

class CatalogReader(object):
    """ Class managing catalogs reading actions"""
    
    def __init__(self, catalog):
        cat_file = catalog if catalog.endswith('.csv') else catalog + '.csv'
        self.cat_name = cat_file[:-4]
        self.cat = None
        s = QSettings()
        catalog_paths = s.value('catalogs')
        if catalog_paths:
            for cat_name, cat_path in catalog_paths.items():
                if cat_name == self.cat_name:
                    self.cat = cat_path
        if not self.cat:
            if path.exists(path.join(pluginDirectory, cat_file)):
                self.cat = path.join(pluginDirectory, cat_file)
#    
#    def get_csv_content(csf_file_name):
#        # create dict
#        items = []
#        csv_path = path.join(pluginDirectory, csf_file_name)
#        with open(csv_path, 'rb') as csvfile:
#            reader = csv.reader(csvfile, delimiter=';')
#            for row in reader:
#                items.append(tuple(row))
#        return items
#
#    def set_list_from_csv(csvFileName, castType='string', column=0):
#        csv_path = path.join(pluginDirectory, csvFileName)
#        if not path.isfile(csv_path):
#            return ['no csv...']
#        # Create list
#        items = []
#        with open(csv_path, 'rb') as csvfile:
#            reader = csv.reader(csvfile, delimiter=';')
#            for row in reader:
#                items.append(row[column])
#
#        if castType == "int":     
#            return items
#        else:
#            return sorted(set(items))

    def get_all_rows(self):
        with open (self.cat, 'rb') as cat_file:
            reader = csv.DictReader(cat_file, delimiter=b';')
            return [{decode(k): decode(v) for (k,v) in row.iteritems()}\
                        for row in reader]

    def get_from(self, criter, value):
        return [row for row in self.get_all_rows() if row.get(criter) == value]

    def get_syntaxons_from_sf(self, cd):
        if not self.get_from("LB_CODE", cd):
            return None
        cat_read = CatalogReader('sigmaf_syntaxon')
        synt_cat_read = CatalogReader('syntaxon')
        links = cat_read.get_from('LB_CODE_GSF', cd)
        cd_syntax_list = [row.get('LB_CODE_SYNTAXON') for row in links]
        syntax_list = []
        for cd_syntax in cd_syntax_list:
            syntax = synt_cat_read.get_from('LB_CODE', cd_syntax)[0]
            obj = {}
            obj['cd_syntax'] = syntax.get('LB_CODE')
            obj['lb_syntax'] = syntax.get('LB_HAB_FR_COMPLET')
            syntax_list.append(obj)
        return syntax_list