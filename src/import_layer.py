# -*- coding: utf-8 -*-
from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, QgsApplication
from PyQt4.uic import *
from PyQt4.QtGui import QMessageBox ,QDateEdit, QPushButton, QLineEdit, QFileDialog, QDialogButtonBox, QComboBox
from PyQt4.QtCore import Qt, SIGNAL, QDate, QThread
import os.path
from db import Db, Session
from geo_model import PolygonModel
from semantic_model import Job, JobModel
from new_job import NewJob
import sys
import functools
from import_file import Import

class ImportLayer(object):
    """
    /***************************************************************************
     Fusion Class
            
            Do the stuff merging features.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """
        Constructor.
    
        :param iface: Interface of QGIS.
        :type iface: QgisInterface
        """
        
        self.iface = iface
        self.canvas = iface.mapCanvas()
        
        # Load Qt UI dialog widget from dir path
        self.pluginDirectory = os.path.dirname(__file__)
        self.openJobDialog = loadUi( os.path.join(self.pluginDirectory, "import_features.ui"))
        
        # Connect UI components to actions
        self.openJobDialog.findChild(QPushButton,'psh_btn_import_lyr').clicked.connect(self.selectFile)
        self.openJobDialog.findChild(QDialogButtonBox,'btn_box_import_lyr').accepted.connect(self.importLayer)
        self.countpb = 0
        self.pbLock = False
        #self.canvas.currentLayer().featureAdded.connect(self.checkValidity)

    def updateProgressBar(self):
        #print 'upd pb'
        if not self.pbLock:
            self.pbLock = True
            self.countpb = self.countpb + 1
            pbval = int(100*self.countpb/self.layercountfeat)
            self.progressBar.setValue(pbval)
            self.pbLock = False
        
        
    def run(self):
        '''Specific stuff at tool activating.'''
        
        # Show the dialog
        self.openJobDialog.show()
        
        
    def selectFile(self):
        
        self.openJobDialog.findChild(QLineEdit,'line_edit_import_lyr').setText(QFileDialog.getOpenFileName(self.openJobDialog,
                                                                                                            "Open File",
                                                                                                            "",
                                                                                                            "Shapefiles (*.shp)"))
        
    
    
    def importLayer(self):
        print 'import'
        # TODO : should be into model part
        # Connect to database
        #dbUri = QgsDataSourceURI(self.canvas.currentLayer().dataProvider().dataSourceUri())
        print 'instance dburi'
        #Db(dbUri.database())
        print 'instance Db'
        importFilePath = self.openJobDialog.findChild(QLineEdit, 'line_edit_import_lyr').text()
        importLayer = QgsVectorLayer(importFilePath, 'geometry', "ogr")
        
        ''' Carhab layer should not overlaps itself. We import only difference between layers '''
        # Prepare processing framework 
        sys.path.append(':/plugins/processing')
        from processing.core.Processing import Processing
        Processing.initialize()
        from processing.tools import *
        
        # Launch difference processing.
        processingResult = general.runalg("qgis:difference", importLayer, self.canvas.currentLayer(), None)
        # Get the tmp shp path corresponding to the difference processing result layer
        differenceLayerPath = processingResult['OUTPUT']
        #print differenceLayerPath
        layer = QgsVectorLayer(differenceLayerPath, 'geometry', "ogr")
        self.layercountfeat = layer.featureCount()
        self.progressBar = loadUi( os.path.join(self.pluginDirectory, "progress_bar.ui"))
        self.iface.messageBar().pushWidget(self.progressBar)
        if differenceLayerPath and self.layercountfeat > 0:
            QgsApplication.processEvents()
            self.worker = Import(differenceLayerPath)
            self.worker.progress.connect(self.updateProgressBar)
            self.worker.finished.connect(self.closeImport)
            #self.worker.run()
            self.worker.start()
            QgsApplication.processEvents()
            
            #print 'before thread instance'
            '''thread = self.thread = QThread()
            #print 'before worker instance'

            worker = self.worker = Import(differenceLayerPath)
            #print 'before movetothread instance'

            worker.moveToThread(thread)
            #print 'before connectr start'

            thread.started.connect(worker.run)
            #print 'before connect progress'

            worker.progress.connect(self.updateProgressBar)
            #print 'before connect finished for closeimport'

            #worker.finished.connect(self.closeImport)
            #print 'before connect finished for closeimport'
            
            worker.finished.connect(worker.deleteLater)
            #print 'before connect finished for worker deletelater'
            
            thread.finished.connect(thread.deleteLater)
            #print 'before connect finished for thread deletelater'
            
            worker.finished.connect(thread.quit)
            #print 'before starting thread'
            
            QgsApplication.processEvents()
            
            thread.start()'''
            #print 'after starting thread'
            
            #print 'thred started'
            #worker.importFeaturesFromFile()
            #errors = polygModel.importFeaturesFromFile(differenceLayerPath)
            #if len(errors) > 0:
            #    NewJob(self.iface).popup('Des géométries de la couche source sont invalides. Des entités n\'ont donc pas été importées : '+str(errors))
        else:
            NewJob(self.iface).popup('Selectionner un fichier source non vide')
            self.run()
        #self.canvas.setExtent(self.canvas.currentLayer())
    
    #def runThread(self):
    #    return lambda : PolygonModel().importFeaturesFromFile(self.differenceLayerPath)
    
    def closeImport(self, success, invalidGeometries):
        print 'thread termine'
        print invalidGeometries
        print success
        
		#QgsApplication.processEvents()
        self.worker.deleteLater()
        self.worker.quit()
        self.worker.wait()
            
    def checkValidity(self, feature):
        for f in self.canvas.currentLayer().getFeatures():
            print feature.geometry().overlaps(f.geometry())