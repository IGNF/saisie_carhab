# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
            self.create_carhab_lyr(selectedFileName)
            
    def create_carhab_lyr(self, file_name):
        carhabLayer = CarhabLayer(file_name)
        CarhabLayerRegistry.instance().removeCarhabLayer(carhabLayer)

        if os.path.exists(file_name):
            os.remove(file_name)
        emptyDb = os.path.join(pluginDirectory, 'empty.sqlite')
        shutil.copy(emptyDb, file_name)

        carhabLayer = CarhabLayer(file_name)
        CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
            
    def openJob(self):
        '''Open an existing job.'''
        
        selectedFileName = execFileDialog('*.sqlite')
        if selectedFileName:
            carhabLayer = CarhabLayer(selectedFileName)
            CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
        