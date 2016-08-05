# -*- coding: utf-8 -*-


from __future__ import unicode_literals

from config import *

class Recorder:
    """ Class managing record actions"""
    
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.description = Config.DB_STRUCTURE[table]   # fields description
    
    def _tuple_to_str(self, tpl):
        return ("%s,"*len(tpl) % (tpl))[:-1]
    
    def input(self, obj):
        " Record input implementation"
        fields = tuple([f for f in obj.keys() if f is not 'the_geom'])
        values = tuple([v for (f,v) in obj.items() if f is not 'the_geom'])
        if 'the_geom' in obj.keys(): # specific to let spatialite evaluate value
            val_param = self._tuple_to_str(values)
            values = None # case without placeholder in SQL query
        else:
            val_param = ('?,'*len(values))[:-1]
        req = "INSERT INTO %s (%s) VALUES (%s)"\
                % (self.table, 
                   self._tuple_to_str(fields),
                   val_param)
        return self.db.execute(req, values)
        
    def update(self, recordId, obj):
        " Record update implementation"
        
        fields = tuple([f for f in obj.keys()])
        values = tuple([v for v in obj.values()] + [recordId])
        setters_str = ("%s = ?,"*len(fields) % (fields))[:-1]
        req = "UPDATE %s SET %s WHERE id = ?" % (self.table, setters_str)
        return self.db.execute(req, values)
                                                                           
    def select_by_id(self, id):
        " Select a data by its ID"
        
        req = "SELECT * FROM %s WHERE id = %s;" % (self.table, id)
        self.db.execute(req)
        result = {}
        for row in self.db.lastQueryResult():
            i = 0
            for value in row:
                result[self.description[i][0]] = value
                i += 1
            return result

    def select(self, column, value):
        if isinstance(value, int):
            value = str(value)
        else:
            value = "'" + str(value) + "'"
        req = "SELECT * FROM %s WHERE %s = %s;" % (self.table,
                                                    column,
                                                    value)
        self.db.execute(req)
        results = []
        for row in self.db.lastQueryResult():
            result = {}
            i = 0
            for value in row:
                result[self.description[i][0]] = value
                i += 1
            results.append(result)
        return results

    def select_value(self, column, value, field):
        
        req = "SELECT %s FROM %s WHERE %s = '%s';" % (field,
                                                    self.table,
                                                    column,
                                                    str(value))
        self.db.execute(req)
        for row in self.db.lastQueryResult():
            return row[0]
    
    def select_all(self):
        req = "SELECT * FROM %s;" % (self.table)
        self.db.execute(req)
        results = []
        for row in self.db.lastQueryResult():
            result = {}
            i = 0
            for value in row:
                result[self.description[i][0]] = value
                i += 1
            results.append(result)
        return results
    
    def delete_row(self, id):
        req = "DELETE FROM %s WHERE id = %s;" % (self.table, id)
        self.db.execute(req)
        
    def get_last_id(self):
        req = "SELECT MAX(id) FROM %s;" % (self.table)
        self.db.execute(req)
        for row in self.db.lastQueryResult():
            return row[0]