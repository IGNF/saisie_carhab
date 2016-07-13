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
        with open (self.cat) as cat_file:
            reader = csv.reader(cat_file, delimiter=';')
            for row in reader:
                result.append(row)
        return result
    
    def get_from(self, criteria, value):
        result = []
        with open (self.cat) as cat_file:
            reader = csv.reader(cat_file, delimiter=';')
            for row in reader:
                if row[criteria].decode('utf8') == value:
                    result.append((row[0], row[1]))
        return result
    
    def get_rows_from_code(self, cd):
        return self.get_from(0, cd)
    
    def get_rows_from_label(self, lb):
        return self.get_from(1, lb)
    
    def get_obj_from_code(self, cd):
        if not self.get_rows_from_code(cd):
            return None
        result = {}
        result['code_sigma'], result['lb_sigma'] = cd, self.get_rows_from_code(cd)[0][1]
        cat_reader = CatalogReader('serie_sigmaf')
        lnkd_serie = cat_reader.get_rows_from_label(cd)[0]
        if lnkd_serie:
            serie_cat_reader = CatalogReader('serie')
            serie = serie_cat_reader.get_rows_from_code(lnkd_serie[0])[0]
            result['cd_serie'], result['lb_serie'] = serie[0], serie[1]
        else:
            result['cd_serie'], result['lb_serie'] = None, None
        if self.cat_name == 'sigmaf':
            cat_read = CatalogReader('sigmaf_syntaxon')
            synt_cat_read = CatalogReader('syntaxon')
            links = cat_read.get_rows_from_code(cd)
            cd_syntax_list = [row[1] for row in links]
            syntax_list = []
            for cd_syntax in cd_syntax_list:
                syntax = synt_cat_read.get_rows_from_code(cd_syntax)[0]
                syntax_obj = {}
                syntax_obj['cd_syntax'] = syntax[0]
                syntax_obj['lb_syntax'] = syntax[1]
                syntax_list.append(syntax_obj)
            result['composyntaxon'] = syntax_list
        return result