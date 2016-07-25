# -*- coding: utf-8 -*-

import csv

from os import path

from utils_job import pluginDirectory

class CatalogReader:
    """ Class managing catalogs reading actions"""
    
    def __init__(self, catalog):
        cat_file = catalog if catalog.endswith('.csv') else catalog + '.csv'
        self.cat_name = cat_file[:-4]
        self.cat = path.join(pluginDirectory, cat_file)
    
    def get_all_rows(self):
        result = []
        with open (self.cat, "rb") as cat_file:
            reader = csv.DictReader(cat_file, delimiter=';')
            for row in reader:
                result.append(row)
        return result
    
    def get_from(self, criteria, value):
        result = []
        with open (self.cat) as cat_file:
            reader = csv.DictReader(cat_file, delimiter=';')
            for row in reader:
                if row.get(criteria).decode('utf8') == value:
                    result.append(row)
        return result
    
    def get_column_as_list(self, column_name):
        with open (self.cat, "rb") as cat_file:
            reader = csv.DictReader(cat_file, delimiter=';')
            cd_col  = []
            lb_col = []
            for row in reader:
                cd_col.append(row.get('code'))
                lb_col.append(row.get(column_name))
        result = zip(cd_col, lb_col)
        return result
    
    def get_rows_from_code(self, cd):
        return self.get_from('code', cd)
    
    def get_rows_from_label(self, lb):
        return self.get_from('label', lb)
    
    
    
    def get_syntaxons_from_sf(self, cd):
        if not self.get_rows_from_code(cd):
            return None
        
        cat_read = CatalogReader('sigmaf_syntaxon')
        synt_cat_read = CatalogReader('syntaxon')
        links = cat_read.get_from('code_child', cd)
        cd_syntax_list = [row.get('code_parent') for row in links]
        syntax_list = []
        for cd_syntax in cd_syntax_list:
            syntax = synt_cat_read.get_from('code', cd_syntax)[0]
            syntax_obj = {}
            syntax_obj['cd_syntax'] = syntax.get('code')
            syntax_obj['lb_syntax'] = syntax.get('label').decode('utf8')
            syntax_list.append(syntax_obj)
        return syntax_list