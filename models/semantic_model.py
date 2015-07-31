from pyspatialite import dbapi2 as db
from db import Session, Db
from PyQt4.Qt import QDate

class Job(object):
    def __init__(self):
        self.name = None
        self.author = None
        self.organism = None
        self.date = QDate.currentDate()


class JobModel(object):
    def __init__(self):
        pass
    
    def insert(self, job):
        conn = db.connect(Session().dbPath)
        # creating a Cursor
        cur = conn.cursor()
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
        self.echelle = None
        self.representationCartographique = None
        self.largeurLineaire = None
        self.surface = None
        self.calculSurface = None
        self.remarque = None

class UvcModel(object):

    def __init__(self):
        self.connection = db.connect(Session().dbPath)

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
                    "'"+str(uvc.modeDetermination)+ "', "
                    "'"+str(uvc.observationVegetation)+ "', "
                    "'"+str(uvc.auteurMaj)+ "', "
                    "'"+str(uvc.dateMaj)+ "', "
                    "'"+str(uvc.echelle)+ "', "
                    "'"+str(uvc.representationCartographique)+ "', "
                    "'"+str(uvc.largeurLineaire)+ "', "
                    "'"+str(uvc.surface)+ "', "
                    "'"+str(uvc.calculSurface)+ "', "
                    "'"+str(uvc.remarque)+"'"
                ")")
        return sql

    def insert(self, uvc):
        conn = db.connect(Session().dbPath)
        # creating a Cursor
        cur = conn.cursor()
        sql = self.insertStatement(uvc)
        cur.execute(sql)
        conn.commit()
        conn.close()
        
    def getLastStatement(self):
        sql = "SELECT max(id) FROM unite_vegetation_cartographiee"
        return sql