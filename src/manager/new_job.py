# -*- coding: utf-8 -*-
import os.path
import shutil

from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI

from PyQt4.QtGui import QDateEdit, QDialogButtonBox, QComboBox
from PyQt4.QtCore import QDate, QSettings
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
        
        pass

    def run(self):
        '''Specific stuff at tool activating.'''
        
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
        
        carhabLayer = CarhabLayer(jobName)
        CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
        
        s = QSettings()
        
        job = Job()
        
        job.name = os.path.splitext(os.path.basename(jobName))[0]
        job.author = s.value("saisieCarhab/username", "")
        job.organism = s.value("saisieCarhab/userorga", "")
        job.date = s.value("saisieCarhab/date", QDate.currentDate())
        
        JobModel().insert(job)
