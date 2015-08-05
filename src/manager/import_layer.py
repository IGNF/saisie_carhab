# -*- coding: utf-8 -*-
import os.path
import sys

from qgis.gui import QgsMessageBar, QgsMessageBarItem
from qgis.core import QgsVectorLayer, QgsApplication
from qgis.utils import iface

from PyQt4.uic import loadUi

from import_file import Import

from utils_job import popup, execFileDialog, pluginDirectory
from PyQt4.QtGui import QApplication

# Prepare processing framework 
sys.path.append(':/plugins/processing')
from processing.core.Processing import Processing
Processing.initialize()
from processing.tools import *

class ImportLayer(object):
    """
    /***************************************************************************
     Fusion Class
            
            Do the stuff merging features.
     ***************************************************************************/
     """
    def __init__(self):
        """Constructor."""
        
        self.canvas = iface.mapCanvas()

    def removeProgressBar(self, msgBarItem):
        print 'before remove'
        if msgBarItem == self.msgBarItem:
            self.progressBar = None
            print 'remove pb'

    def updateProgressBar(self, progressValue):
        #print 'upd pb'
        #QgsApplication.processEvents()
        if self.progressBar :
            print self.progressBar
            print progressValue
            self.progressBar.setValue(progressValue)

    def run(self):
        '''Specific stuff at tool activating.'''

        selectedFileName = execFileDialog()
        if selectedFileName:
            self.importLayer(selectedFileName)
    
    def importLayer(self, importFilePath):
        importLayer = QgsVectorLayer(importFilePath, 'geometry', "ogr")
        
        ''' Carhab layer should not overlaps itself. We import only difference between layers '''
        # Launch difference processing.
        processingResult = general.runalg("qgis:difference", importLayer, self.canvas.currentLayer(), None)
        # Get the tmp shp path corresponding to the difference processing result layer
        differenceLayerPath = processingResult['OUTPUT']
        #print differenceLayerPath
        layer = QgsVectorLayer(differenceLayerPath, 'geometry', "ogr")
        self.progressBar = loadUi( os.path.join(pluginDirectory, "progress_bar.ui"))
        self.progressBarId = self.progressBar.winId()
        self.msgBarItem = QgsMessageBarItem('Import des entités'.decode('utf-8'), '', self.progressBar)
        iface.messageBar().pushItem(self.msgBarItem)
        
        
        
        iface.messageBar().widgetRemoved.connect(self.removeProgressBar)
        
        
        
        if differenceLayerPath and layer.featureCount() > 0:
            QgsApplication.processEvents()
            self.worker = Import(layer)
            self.worker.progress.connect(self.updateProgressBar)
            self.worker.finished.connect(self.closeImport)
            
            self.worker.start()
            #self.worker.run()
            
            QgsApplication.processEvents()
        else:
            msg = 'Aucune entité importée : emprise de la couche sélectionnée déjà peuplée.'
            popup(msg)
            iface.messageBar().popWidget(self.msgBarItem)
        
            self.canvas.currentLayer().updateExtents()
            self.canvas.setExtent(self.canvas.currentLayer().extent())
            self.canvas.refresh()
    
    def closeImport(self, success, invalidGeometries):
        self.worker.deleteLater()
        self.worker.quit()
        self.worker.wait()
        
        self.progressBar.setValue(100)
        iface.messageBar().popWidget(self.msgBarItem)
        
        self.canvas.currentLayer().updateExtents()
        self.canvas.setExtent(self.canvas.currentLayer().extent())
        self.canvas.refresh()