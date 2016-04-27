# -*- coding: utf-8 -*-
import os.path
import sys

# Prepare processing framework 
sys.path.append(':/plugins/processing')
from processing.core.Processing import Processing
Processing.initialize()
from processing.tools import *

from qgis.gui import QgsMessageBarItem
from qgis.core import QgsVectorLayer, QgsApplication,QgsCoordinateReferenceSystem
from qgis.utils import iface

from PyQt4.QtCore import QThread, QSettings
from PyQt4.uic import loadUi

from import_file import Import

from utils_job import popup, execFileDialog, pluginDirectory, no_vector_lyr_msg

class ImportLayer(object):
    """
    /***************************************************************************
     ImportLayer Class
            
            Do the stuff import features from shapefile to carhab layer.
     ***************************************************************************/
     """

    def __init__(self):
        """Constructor."""
        
        self.canvas = iface.mapCanvas()
        self.progressBar = None
        self.lockProgressBar = False

    def addProgressBar(self):
        
        self.progressBar = loadUi(os.path.join(pluginDirectory, "progress_bar.ui"))
        
        self.msgBarItem = QgsMessageBarItem('', 'Import des entités'.decode('utf-8'), self.progressBar)
        iface.messageBar().pushItem(self.msgBarItem)
        
        self.progressBar.destroyed.connect(self.removeProgressBar)

    def updateProgressBar(self, progressValue):
        
        QgsApplication.processEvents()
        if self.progressBar and not self.lockProgressBar:
            self.lockProgressBar = True
            
            self.progressBar.setValue(progressValue)
            self.progressValue = progressValue
            
            self.lockProgressBar = False
    
    def removeProgressBar(self, msgBarItem):
        
        self.progressBar = None
        
        if self.progressValue != 100: # To recognize an abortement by user of import.
            QgsApplication.processEvents()
            self.worker.stop = True
    
    def makeDifference(self, importLayer):
        
        # Launch difference processing.
        processingResult = general.runalg("qgis:difference", importLayer, iface.mapCanvas().currentLayer(), None)
        # Get the tmp shp path corresponding to the difference processing result layer
        differenceLayerPath = processingResult['OUTPUT']
        
        return self.createQgisVectorLayer(differenceLayerPath)

    def closeImport(self, success, code):
        if not success:
            if code == 0:
                popup('Erreur inconnue : aucune entité ajoutée.')
            elif code == 1:
                popup('Pas de couche carhab initialisée : aucune entité ajoutée.')
            elif code == 2:
                popup('Import avorté : aucune entité ajoutée')
        if self.progressBar:
            self.progressBar.setValue(100)
            self.progressValue = 100
            iface.messageBar().popWidget(self.msgBarItem)
        self.canvas.currentLayer().updateExtents()
        self.canvas.setExtent(self.canvas.currentLayer().extent())
        self.canvas.refresh()
        
    def makeImport(self, diffLayer):
        
        self.addProgressBar()
        
        self.thread = QThread()
        self.worker = Import(diffLayer)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.updateProgressBar)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.closeImport)
        self.thread.start()

    def createQgisVectorLayer(self, layerFilePath):
        settings = QSettings()
        oldProjValue = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")
        qgisLayer = QgsVectorLayer(layerFilePath, 'geometry', "ogr")
        qgisLayer.setCrs(QgsCoordinateReferenceSystem(2154, QgsCoordinateReferenceSystem.EpsgCrsId))
        
        settings.setValue("/Projections/defaultBehaviour", oldProjValue)
        
        return qgisLayer

    def run(self):
        '''Specific stuff at tool activating.'''
        
        if not iface.mapCanvas().currentLayer():
            no_vector_lyr_msg()
            return
        
        # Retrieve shapefile selected by the user
        selectedFileName = execFileDialog()
        
        if selectedFileName:
            
            # Set corresponding layer.
            importLayer = self.createQgisVectorLayer(selectedFileName)
            # Carhab layer should not overlaps itself. Calculate difference between layers.
            diffLayer = self.makeDifference(importLayer)

            if diffLayer:
                if diffLayer.featureCount() == 0:
                    popup(('Emprise de la couche à importer déjà peuplée '
                           'dans la couche Carhab : aucune entité ajoutée.'))
                else:
                    # Import only difference between layers.
                    self.makeImport(diffLayer)
            else:
                popup(('Erreur inconnue : aucune entité ajoutée.'))