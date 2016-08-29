# -*- coding: utf-8 -*-


from __future__ import unicode_literals

from config import *

class Recorder:
    """ Class managing record actions"""
    
    def __init__(self, db, table):
        self.db = db
        self.table = table
    
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
    
    def _get_result(self, req):
        self.db.execute(req)
        fields = [cd[0] for cd in self.db.cursor.description] # list of fields
        results = []
        for row in self.db.lastQueryResult():
            result = {}
            i = 0
            for value in row:
                result[fields[i]] = value
                i += 1
            results.append(result)
        return results
    
    def select(self, column, value):
        if isinstance(value, int):
            value = unicode(value)
        else:
            value = "'" + unicode(value) + "'"
        req = "SELECT * FROM %s WHERE %s = %s;" % (self.table,
                                                    column,
                                                    value)
        return self._get_result(req)

    def select_all(self):
        req = "SELECT * FROM %s;" % (self.table)
        return self._get_result(req)
    
    def delete_row(self, id):
        req = "DELETE FROM %s WHERE id = %s;" % (self.table, id)
        self.db.execute(req)
        
    def get_last_id(self):
        req = "SELECT MAX(id) FROM %s;" % (self.table)
        self.db.execute(req)
        for row in self.db.lastQueryResult():
            return row[0]