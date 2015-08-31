# -*- coding: utf-8 -*-
from pyspatialite import dbapi2 as db
import sqlite3
from PyQt4.Qt import QDate

from carhab_layer_registry import CarhabLayerRegistry

class Job(object):
    def __init__(self):
        self.name = None
        self.author = None
        self.organism = None
        self.date = QDate.currentDate()
        print 'self date'
        print type(self.date)


class JobModel(object):
    def __init__(self):
        pass
    
    def insert(self, job):
        conn = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        # creating a Cursor
        cur = conn.cursor()
        print type(job.date)
        sql = "INSERT INTO job (name, aut_crea, orga_crea, date_crea) "
        sql += "VALUES ('%s', '%s', '%s', '%s')" % (job.name, job.author, job.organism, job.date.toString('yyyy-MM-dd'))
        cur.execute(sql)
        conn.commit()
        conn.close()

class Uvc(object):
    def __init__(self):
        self.id = None
        self.codeSourceOperateur = None
        self.auteurCreation = None
        self.organismeCreation = None
        self.dateCreation = None
        self.modeDetermination = None
        self.observationVegetation = None
        self.auteurMaj = None
        self.dateMaj = None
        self.echelle = -1
        self.representationCartographique = -1
        self.largeurLineaire = -1.0
        self.surface = -1.0
        self.calculSurface = None
        self.remarque = None

class UvcModel(object):

    def __init__(self):
        self.connection = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)

    def incrementId(self):
        cur = self.connection.cursor()
        for row in cur.execute("SELECT max(id) FROM unite_vegetation_cartographiee"):
            if row[0]:
                return row[0] + 1
            else:
                return 1

    def insertStatement(self, uvc):
        sql = ("INSERT INTO unite_vegetation_cartographiee ("
                    "cd_src_op,"
                    "aut_crea ,"
                    "orga_crea ,"
                    "date_crea ,"
                    "mode_deter ,"
                    "obs_veget ,"
                    "aut_maj ,"
                    "date_maj ,"
                    "echelle ,"
                    "repr_carto ,"
                    "larg_lin ,"
                    "surface ,"
                    "calc_surf ,"
                    "rmq )"
                "VALUES ("
                    "'"+str(uvc.codeSourceOperateur)+ "', "
                    "'"+str(uvc.auteurCreation)+ "', "
                    "'"+str(uvc.organismeCreation)+ "', "
                    
                    "'"+str(uvc.dateCreation)+ "', "
                    #"'"+uvc.dateCreation.toString('yyyy-MM-dd')+ "', "
                    "'"+str(uvc.modeDetermination)+ "', "
                    "'"+str(uvc.observationVegetation)+ "', "
                    "'"+str(uvc.auteurMaj)+ "', "
                    "'"+str(uvc.dateMaj)+ "', "
                    #"'"+str(uvc.dateMaj) if not uvc.dateMaj else uvc.dateMaj.toString('yyyy-MM-dd')+ "', "
                    "'"+str(uvc.echelle)+ "', "
                    "'"+str(uvc.representationCartographique)+ "', "
                    "'"+str(uvc.largeurLineaire)+ "', "
                    "'"+str(uvc.surface)+ "', "
                    "'"+str(uvc.calculSurface)+ "', "
                    "'"+str(uvc.remarque)+"'"
                ")")
        return sql

    def insert(self, uvc):
        conn = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        # creating a Cursor
        cur = conn.cursor()
        sql = self.insertStatement(uvc)
        cur.execute(sql)
        conn.commit()
        conn.close()
        
    def getLastStatement(self):
        sql = "SELECT max(id) FROM unite_vegetation_cartographiee"
        return sql
    
    def update(self, uvc):
        conn = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        cur = conn.cursor()
        print type(uvc.dateCreation)
        sql = ("UPDATE unite_vegetation_cartographiee SET "
                    "cd_src_op = '"+str(uvc.codeSourceOperateur)+ "', "
                    "mode_deter  = '"+str(uvc.modeDetermination)+ "', "
                    "obs_veget  = '"+str(uvc.observationVegetation)+ "', "
                    "aut_maj  = '"+str(uvc.auteurMaj)+ "', "
                    #"date_maj  = '"+uvc.dateMaj.toString('yyyy-MM-dd')+ "', "
                    "echelle  = '"+str(uvc.echelle)+ "', "
                    "repr_carto  = '"+str(uvc.representationCartographique)+ "', "
                    "larg_lin  = '"+str(uvc.largeurLineaire)+ "', "
                    "surface  = '"+str(uvc.surface)+ "', "
                    "calc_surf  = '"+str(uvc.calculSurface)+ "', "
                    "rmq  = '"+str(uvc.remarque)+"' "
                "WHERE id = "+ str(uvc.id))
        print sql
        cur.execute(sql)
        conn.commit()
        conn.close()
        
    def get(self, uvcId):
        conn = sqlite3.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM unite_vegetation_cartographiee WHERE id = " + str(uvcId)
        cur.execute(sql)
        results = cur.fetchone()
        conn.commit()
        conn.close()
        
        if results:
            
            uvc = Uvc()
            uvc.id = uvcId
            uvc.codeSourceOperateur = results['cd_src_op'] if results['cd_src_op'] != 'None' else None
            uvc.auteurCreation = results['aut_crea'] if results['aut_crea'] != 'None' else None
            uvc.organismeCreation = results['orga_crea'] if results['orga_crea'] != 'None' else None
            uvc.dateCreation = results['date_crea'] if results['date_crea'] != 'None' else None
            uvc.modeDetermination = results['mode_deter'] if results['mode_deter'] != 'None' else None
            uvc.observationVegetation = results['obs_veget'] if results['obs_veget'] != 'None' else None
            uvc.auteurMaj = results['aut_maj'] if results['aut_maj'] != 'None' else None
            uvc.dateMaj = results['date_maj'] if results['date_maj'] != 'None' else None
            uvc.echelle = results['echelle'] if results['echelle'] != -1 else None
            uvc.representationCartographique = results['repr_carto'] if results['repr_carto'] != -1 else None
            uvc.largeurLineaire = results['larg_lin'] if results['larg_lin'] != -1.0 else None
            uvc.surface = results['surface'] if results['surface'] != -1.0 else None
            uvc.calculSurface = results['calc_surf'] if results['calc_surf'] != 'None' else None
            uvc.remarque = results['rmq'] if results['rmq'] != 'None' else None
            
            return uvc
        return None
    
class SigmaFacies(object):
    def __init__(self):
        self.id = None
        self.nom = None
        self.uvc = None
        self.typeComplexe = None
        self.typeSerie = None
        self.confianceComplexe = None
        self.confianceSerie = None
        self.expression = None
        self.typicite = None
        self.remarque = None
        
class SigmaFaciesModel(object):

    def __init__(self):
        self.connection = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        
    def insertStatement(self, sigmaF):
        sql = ("INSERT INTO composition_sigma_facies ("
                    "nom ,"
                    "typ_cplx ,"
                    "typ_serie ,"
                    "cfce_serie ,"
                    "cfce_cplx ,"
                    "expression ,"
                    "typicite ,"
                    "rmq )"
                "VALUES ("
                    "'"+str(sigmaF.nom)+ "', "
                    "'"+str(sigmaF.typeComplexe)+ "', "
                    "'"+str(sigmaF.typeSerie)+ "', "
                    "'"+str(sigmaF.confianceSerie)+ "', "
                    "'"+str(sigmaF.confianceComplexe)+ "', "
                    "'"+str(sigmaF.expression)+ "', "
                    "'"+str(sigmaF.typicite)+ "', "
                    "'"+str(sigmaF.remarque)+"'"
                ")")
        return sql

    def insert(self, sigmaF):
        conn = db.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        # creating a Cursor
        cur = conn.cursor()
        sql = self.insertStatement(sigmaF)
        cur.execute(sql)
        conn.commit()
        conn.close()
        
    def get(self, sigmaFId):
        conn = sqlite3.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM composition_sigma_facies WHERE id = " + str(sigmaFId)
        cur.execute(sql)
        results = cur.fetchone()
        conn.close()
        
        if results:
            
            sigmaF = SigmaFacies()
            sigmaF.id = sigmaFId
            sigmaF.nom = results['nom'] if results['nom'] != 'None' else None
            sigmaF.uvc = results['uvc'] if results['uvc'] != 'None' else None
            sigmaF.typeComplexe = results['typ_cplx'] if results['typ_cplx'] != 'None' else None
            sigmaF.typeSerie = results['typ_serie'] if results['typ_serie'] != 'None' else None
            sigmaF.confianceComplexe = results['mode_deter'] if results['mode_deter'] != 'None' else None
            sigmaF.confianceSerie = results['cfce_serie'] if results['cfce_serie'] != 'None' else None
            sigmaF.expression = results['expression'] if results['expression'] != 'None' else None
            sigmaF.typicite = results['typicite'] if results['typicite'] != 'None' else None
            sigmaF.remarque = results['rmq'] if results['rmq'] != 'None' else None
            
            return sigmaF
        return None
    
    def getAll(self):
        conn = sqlite3.connect(CarhabLayerRegistry.instance().currentLayer.dbPath)
        conn.row_factory = sqlite3.Row
        # creating a Cursor
        cur = conn.cursor()
        sql = "SELECT * FROM composition_sigma_facies"
        cur.execute(sql)
        results = cur.fetchall()
        conn.close()
        
        if results:
            sigmaFList = []
            for result in results:
                
                sigmaF = SigmaFacies()
                
                sigmaF.id = result['id']
                sigmaF.nom = result['nom'] if result['nom'] != 'None' else None
                sigmaF.uvc = result['uvc'] if result['uvc'] != 'None' else None
                sigmaF.typeComplexe = result['typ_cplx'] if result['typ_cplx'] != 'None' else None
                sigmaF.typeSerie = result['typ_serie'] if result['typ_serie'] != 'None' else None
                sigmaF.confianceComplexe = result['cfce_cplx'] if result['cfce_cplx'] != 'None' else None
                sigmaF.confianceSerie = result['cfce_serie'] if result['cfce_serie'] != 'None' else None
                sigmaF.expression = result['expression'] if result['expression'] != 'None' else None
                sigmaF.typicite = result['typicite'] if result['typicite'] != 'None' else None
                sigmaF.remarque = result['rmq'] if result['rmq'] != 'None' else None
                
                sigmaFList.append(sigmaF)
                
            return sigmaFList
        
        return None