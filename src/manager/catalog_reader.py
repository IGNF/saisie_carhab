# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv

from os import path

from PyQt4.QtCore import QSettings

from utils_job import pluginDirectory, popup, encode, decode
from catalog import Catalog

class CatalogReader:
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