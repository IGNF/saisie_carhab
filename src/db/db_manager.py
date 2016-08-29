# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyspatialite import dbapi2 as db
from os.path import dirname
import sys


#from carhab_layer_manager import Singleton
#
#@Singleton
class DbManager:
    """ Implementation and interfacing of a spatialite DB """
    
    def __init__(self, dbPath):
        " Etablishing connection, cursor creation and initialising DB stuff"
        self.dbpath = dbPath
        try:
            self.conn = db.connect(dbPath)
            self.conn.isolation_level = None
        except Exception, err:
            print 'DB connection failed :\n'\
                  'Detected error :\n%s' % err
            self.echec =1
        else:
            self.cursor = self.conn.cursor()   # cursor creation
            self.echec =0
    
    def createTables(self, tables_lst):
        "Creation of tables described into the dictionary <dicTables>."
        
        for tbl, tbl_descr in tables_lst:            # scan dictionary
            req = "CREATE TABLE %s (" % tbl
            dict_geom = {}
            for field, descr in tbl_descr.get('fields'):
                if descr.get('type') in ['POLYGON', 'LINESTRING', 'POINT']:
                    dict_geom[field] = descr.get('type')
                else:
                    req = req + "%s %s, " % (field, descr.get('type'))
            req = req[:-2] + ")"
            self.execute(req)
            
            if dict_geom: # Add geometry column
                for fieldName, fieldType in dict_geom.items():
                    req =  "SELECT AddGeometryColumn('%s', '%s', 2154, '%s', 'XY');" % (tbl,
                                                                                        fieldName,
                                                                                        fieldType)
                    self.execute(req)
    
    def execute(self, req, values=None):
        " Query <req> execution, with errors detection"
        try:
            params = (req, values) if values else (req,)
            self.cursor.execute(*params)
        except Exception, err:
            saveout = sys.stdout
            fsock = open(dirname(__file__) + r'\out.log', 'a')
            sys.stdout = fsock
            # Display the query and the system error message :
            msg = "Bad SQL query :\n%s\nvalues : %s\nDetected error :\n%s"\
                    % (req, values, err)
            print msg.encode('utf8')
            sys.stdout = saveout
            fsock.close()
            return err
        else:
            return 1
        
    def executeScript(self, scriptPath):
        " SQL script execution, with errors detection"
        
        try:
            # Open and execute SQL script
            sqlScript = open(scriptPath)
            self.cursor.executescript(sqlScript.read())
        except Exception, err:
            # Display the query and the system error message :
            msg = "Bad SQL query :\n%s\nDetected error :\n%s" %(scriptPath, err)
            print msg.encode('utf8')
            return 0
        else:
            return 1
        
    def lastQueryResult(self):
        " Returns last query result (tuple of tuples)"
        return self.cursor.fetchall()

    def commit(self):
        if self.conn:
            self.conn.commit()         # transfer cursor -> disk

    def close(self):
        if self.conn:
            self.conn.close()
            