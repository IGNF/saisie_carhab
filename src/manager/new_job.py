# -*- coding: utf-8 -*-
import os.path
import shutil

from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI

from PyQt4.QtGui import QDateEdit, QDialogButtonBox, QComboBox
from PyQt4.QtCore import QDate
from PyQt4.uic import loadUi

from semantic_model import Job, JobModel

from carhab_layer_registry import CarhabLayer, CarhabLayerRegistry

from utils_job import pluginDirectory, execFileDialog

class NewJob(object):
    """
    /***************************************************************************
     NewLayer Class
            
            Do the stuff creating a work layer in spatialite format.
     ***************************************************************************/
     """
    def __init__(self):
        """ Constructor."""
        
        # Load Qt UI dialog widget from dir path
        self.newJobDialog = loadUi( os.path.join(pluginDirectory, "new_job.ui"))
        # Set current date into form
        self.newJobDialog.findChild(QDateEdit,'date_edit_creation_job').setDate(QDate.currentDate()) 
        # Connect UI components to actions
        self.newJobDialog.findChild(QDialogButtonBox,'btn_box_job').accepted.connect(self.setDestinationFile)

    def run(self):
        '''Specific stuff at tool activating.'''
        
        # Show the dialog
        self.newJobDialog.show()
        
    def setDestinationFile(self):
        
        selectedFileName = execFileDialog('*.sqlite', 'Enregistrer sous...', 'save')
        if selectedFileName:
            self.createJob(selectedFileName)

    def createJob(self, jobName):
        print QgsMapLayerRegistry.instance().mapLayers()
        carhabLayer = CarhabLayer(jobName) 
        CarhabLayerRegistry.instance().removeCarhabLayer(carhabLayer)
        
        if os.path.exists(jobName):
            os.remove(jobName)
        
        emptyDb = os.path.join(pluginDirectory, 'empty.sqlite')
        shutil.copy(emptyDb, jobName)
        
        CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
                
        job = Job()
        
        job.name = os.path.basename(jobName)
        job.organism = self.newJobDialog.findChild(QComboBox,'cb_box_orga').currentText()
        job.author = self.newJobDialog.findChild(QComboBox,'cb_box_pers').currentText()
        job.date = self.newJobDialog.findChild(QDateEdit,'date_edit_creation_job').date()
        JobModel().insert(job)
