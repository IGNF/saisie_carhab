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
        
        self.countpb = 0
        self.pbLock = False

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
        dialog = QFileDialog(None,'Sélectionner un fichier...'.decode('utf-8'))
        dialog.setFilter('*.shp')
        dialog.setFileMode(1)
        dialog.setOption(QFileDialog.ReadOnly, True)

        if dialog.exec_():
            shpFileName = dialog.selectedFiles()[0]
            self.importLayer(shpFileName)
    
    def importLayer(self, importFilePath):
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
        self.progressBar = loadUi( os.path.join(os.path.dirname(__file__), "progress_bar.ui"))
        self.iface.messageBar().pushWidget(self.progressBar)
        if differenceLayerPath and self.layercountfeat > 0:
            QgsApplication.processEvents()
            self.worker = Import(differenceLayerPath)
            self.worker.progress.connect(self.updateProgressBar)
            self.worker.finished.connect(self.closeImport)
            self.worker.start()
            QgsApplication.processEvents()
        else:
            NewJob(self.iface).popup('Selectionner un fichier source non vide')
            self.run()
    
    def closeImport(self, success, invalidGeometries):
        self.worker.deleteLater()
        self.worker.quit()
        self.worker.wait()
        
        self.progressBar.setValue(100)
        NewJob(self.iface).popup('Import terminé')
        self.iface.messageBar().popWidget()
        
        self.canvas.currentLayer().updateExtents()
        self.canvas.setExtent(self.canvas.currentLayer().extent())
        self.canvas.refresh()