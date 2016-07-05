# -*- coding: utf-8 -*-
from pyspatialite import dbapi2 as db
from os.path import dirname
import sys

class DbManager:
    """ Implementation and interfacing of a spatialite DB """
    
    def __init__(self, dbPath):
        " Etablishing connection, cursor creation and initialising DB stuff"
        self.dbpath = dbPath
        try:
            self.conn = db.connect(dbPath)
        except Exception, err:
            print 'DB connection failed :\n'\
                  'Detected error :\n%s' % err
            self.echec =1
        else:
            self.cursor = self.conn.cursor()   # cursor creation
            self.echec =0

    def createTables(self, dicTables):
        "Creation of tables described into the dictionary <dicTables>."
        
        for table in dicTables:            # scan dictionary
            req = "CREATE TABLE %s (" % table
            dicGeom = {}
            for descr in dicTables[table]:
                fieldName = descr[0]
                fieldType = descr[1]
                if fieldType == 'POLYGON' or fieldType == 'LINESTRING' or fieldType == 'POINT':
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
            if (values):
                self.cursor.execute(req, values)
            else:
                self.cursor.execute(req)
        except Exception, err:
            saveout = sys.stdout
            fsock = open(dirname(__file__) + r'\out.log', 'a')
            sys.stdout = fsock
            # Display the query and the system error message :
            print "Bad SQL query :\n%s\nDetected error :\n%s"\
                   % (req, err)
            sys.stdout = saveout
            fsock.close()
            return 0
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
            print "Bad SQL query :\n%s\nDetected error :\n%s"\
                   % (scriptPath, err)
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
            
