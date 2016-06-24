# -*- coding: utf-8 -*-
from config import *

class Recorder:
    """ Class managing record actions"""
    
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.description = Config.DB_STRUCTURE[table]   # fields description
                                                                           
    def input(self, obj):
        " Record input implementation"

        fields ="("           # init string for fields
        values = "("          # init string for values
        
        for desc in self.description:
            f = desc[0]
            if f in obj.keys():
                val = obj[f]
                if not val == None:
                    fields = fields + f + ","
                    if f =='the_geom':
                        values = values + unicode(val) + ","
                    else:
                        values = values + "'" + unicode(val) + "',"

        fields = fields[:-1] + ")"      # delete last comas
        values = values[:-1] + ")"       # and add parenthesis
        
        req ="INSERT INTO %s %s VALUES %s" % (self.table, fields, values)
        self.db.execute(req)

    def update(self, recordId, obj):
        " Record update implementation"

        req = "UPDATE %s SET " % (self.table)
        values = []
        for f, v in obj.items():
            req = req + "%s = ?," % (f)
            print type(v)
#            if v:
#                v = unicode(v)
            values.append(v)
        req = req[:-1]
        req = req + " WHERE id = ?;"
        values.append(recordId)
        values = tuple(values)
        print values
        self.db.execute(req, values)
                                                                           
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
        return None

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
        return None
    
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
            return row
        return None