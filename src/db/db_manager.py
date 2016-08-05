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
    
    def in_transaction(self):
        return self.cursor.rowcount
    
    def createTables(self, dicTables):
        "Creation of tables described into the dictionary <dicTables>."
        
        for table in dicTables:            # scan dictionary
            req = "CREATE TABLE %s (" % table
            dicGeom = {}
            for descr in dicTables[table]:
                fieldName = descr[0]
                fieldType = descr[1]
                if fieldType in ['POLYGON', 'LINESTRING', 'POINT']:
                    dicGeom[fieldName] = fieldType
                else:
                    req = req + "%s %s, " % (fieldName, fieldType)
            req = req[:-2] + ")"
            self.execute(req)
            
            if dicGeom: # Add geometry column
                for fieldName, fieldType in dicGeom.items():
                    req =  "SELECT AddGeometryColumn('%s', '%s', 2154, '%s', 'XY');" % (table,
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
            