# -*- coding: utf-8 -*-

import csv

from os import path

from PyQt4.QtCore import QSettings

from utils_job import pluginDirectory, popup
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
            for cat_path in catalog_paths.values():
                if path.basename(cat_path) == cat_file:
                    self.cat = cat_path
        if not self.cat:
            if path.exists(path.join(pluginDirectory, cat_file)):
                self.cat = path.join(pluginDirectory, cat_file)
    
    def get_all_rows(self):
        result = []
        if self.cat:
            with open (self.cat, "rb") as cat_file:
                reader = csv.DictReader(cat_file, delimiter=';')
                for row in reader:
                    result.append(row)
        return result
    
    def get_from(self, criteria, value):
        result = []
        if self.cat:
            with open (self.cat) as cat_file:
                reader = csv.DictReader(cat_file, delimiter=';')
                for row in reader:
                    if row.get(criteria).decode('utf8') == value:
                        result.append(row)
        return result
    
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
            obj['lb_syntax'] = syntax.get('LB_HAB_FR_COMPLET').decode('utf8')
            syntax_list.append(obj)
        return syntax_list