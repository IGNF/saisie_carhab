# -*- coding: utf-8 -*-
import os.path
import shutil

from qgis.gui import *

from carhab_layer_manager import CarhabLayer, CarhabLayerRegistry

from utils_job import pluginDirectory, execFileDialog

class JobManager(object):
    """
    /***************************************************************************
     NewLayer Class
            
            Do the stuff managing (creating, opening, ...)
             a work layer in spatialite format.
     ***************************************************************************/
     """
    def __init__(self):
        """ Constructor."""
        
        pass

    def createJob(self):
        '''Create new job.'''
        
        selectedFileName = execFileDialog('*.sqlite', 'Enregistrer sous...', 'save')
        if selectedFileName:
            carhabLayer = CarhabLayer(selectedFileName)
            CarhabLayerRegistry.instance().removeCarhabLayer(carhabLayer)
            
            if os.path.exists(selectedFileName):
                os.remove(selectedFileName)
            emptyDb = os.path.join(pluginDirectory, 'empty.sqlite')
            shutil.copy(emptyDb, selectedFileName)
            
            carhabLayer = CarhabLayer(selectedFileName)
            CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
            
    def openJob(self):
        '''Open an existing job.'''
        
        selectedFileName = execFileDialog('*.sqlite')
        if selectedFileName:
            carhabLayer = CarhabLayer(selectedFileName)
            CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
        