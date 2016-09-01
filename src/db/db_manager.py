# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyspatialite import dbapi2 as db
from os.path import dirname
import sys
import time

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
    
    def version(self):
        self.execute('PRAGMA user_version')
        return self.lastQueryResult()[0][0]
    
    def set_version(self, version):
        print version
        self.execute('PRAGMA user_version = %s' % (version))
    
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
            msg = "Bad SQL query :%s. values : %sDetected error :%s"\
                    % (req, values, err)
            self.log(msg)
            return err
        else:
            return 1
    
    def log(self, msg, level='CRITICAL'):
        now = time.strftime("%Y-%m-%dT%H:%M:%S "+level+ " : ")
        saveout = sys.stdout
        fsock = open(dirname(__file__) + r'\out.log', 'a')
        sys.stdout = fsock
        print now + msg.encode('utf8')
        sys.stdout = saveout
        fsock.close()
    
    def executeScript(self, scriptPath):
        " SQL script execution, with errors detection"
        
        try:
            # Open and execute SQL script
            sqlScript = open(scriptPath)
            self.cursor.executescript(sqlScript.read())
        except Exception, err:
            msg = "Bad SQL query :%s. Detected error :%s" %(scriptPath, err)
            self.log(msg)
            return err
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
            