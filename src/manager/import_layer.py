# -*- coding: utf-8 -*-
import os.path
import sys

from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsApplication
from qgis.utils import iface

from PyQt4.uic import loadUi

from import_file import Import

from utils_job import popup, execFileDialog, pluginDirectory


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

        selectedFileName = execFileDialog()
        if selectedFileName:
            self.importLayer(selectedFileName)
    
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
        self.progressBar = loadUi( os.path.join(pluginDirectory, "progress_bar.ui"))
        iface.messageBar().pushWidget(self.progressBar)
        if differenceLayerPath and self.layercountfeat > 0:
            QgsApplication.processEvents()
            self.worker = Import(differenceLayerPath)
            self.worker.progress.connect(self.updateProgressBar)
            self.worker.finished.connect(self.closeImport)
            self.worker.start()
            QgsApplication.processEvents()
        else:
            msg = 'Aucune entité importée : emprise de la couche sélectionnée déjà peuplée.'
            popup(msg)
            iface.messageBar().popWidget()
        
            self.canvas.currentLayer().updateExtents()
            self.canvas.setExtent(self.canvas.currentLayer().extent())
            self.canvas.refresh()
    
    def closeImport(self, success, invalidGeometries):
        self.worker.deleteLater()
        self.worker.quit()
        self.worker.wait()
        
        self.progressBar.setValue(100)
        iface.messageBar().popWidget()
        
        self.canvas.currentLayer().updateExtents()
        self.canvas.setExtent(self.canvas.currentLayer().extent())
        self.canvas.refresh()