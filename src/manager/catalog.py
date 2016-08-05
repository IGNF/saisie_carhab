# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv

from os import path

from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui import QPushButton, QLineEdit
from PyQt4.uic import loadUi

from functools import partial

from qgis.utils import iface

from utils_job import pluginDirectory, execFileDialog, popup
from config import Config


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
        catalog_path = execFileDialog('*.csv')
        self.catalog[catalog_name] = catalog_path
        if catalog_path:
            line_edt = self.ui.findChild(QLineEdit, catalog_name)
            line_edt.setText(catalog_path)
    
    def check_data(self):
        catalog_struct = Config.CATALOG_STRUCTURE
        msg = ''
        for cat_name, cat_path in self.catalog.items():
            fl_name = path.basename(cat_path)
            if not path.exists(cat_path) and not path.isfile(cat_path):
                msg += 'Chemin de fichier invalide pour {}.\n'.format(fl_name)
                continue
            with open(cat_path, 'rb') as cat_file:
                reader = csv.reader(cat_file, delimiter=b';')
                headers = reader.next()
            if len(headers) < 2:
                msg += 'Délimiteur ";" requis dans {}.\n'.format(fl_name)
                continue
            if catalog_struct.get('data').get(cat_name):
                for field in catalog_struct.get('data').get(cat_name):
                    if not field in headers:
                        msg += 'Champ "{}" manquant dans le fichier "{}".\n'\
                            .format(field, fl_name)
            else:
                cds = [i[2] for i in catalog_struct.get('links').get(cat_name)]
                for cd in cds:
                    if not cd in headers:
                        msg += 'Champ "{}" manquant dans le fichier "{}".\n'\
                            .format(cd, fl_name)
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
            popup('Champs manquants :\n\n' + msg)
            return
        elif self.check_data():
            s = QSettings()
            s.setValue('catalogs', self.catalog)
            iface.removeDockWidget(self.ui)
        