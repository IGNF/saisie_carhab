# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os.path
import shutil

from qgis.gui import *

from work_layer import WorkLayer, WorkLayerRegistry

from communication import pluginDirectory, file_dlg

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

    def create_job(self):
        '''Create new job.'''
        
        file_path = file_dlg('*.sqlite', 'Enregistrer sous...', 'save')
        if file_path:
            wk_lyr_to_del = [wl for wl in WorkLayerRegistry.instance().work_layers.values() if wl.db_path == file_path]
            if len(wk_lyr_to_del) > 0:
                WorkLayerRegistry.instance().remove_work_layer(wk_lyr_to_del[0])
            empty_db = os.path.join(pluginDirectory, 'empty.sqlite')
            shutil.copy(empty_db, file_path)
            work_lyr = WorkLayer(file_path)
            WorkLayerRegistry.instance().add_work_lyr(work_lyr)
            return work_lyr
            
    def openJob(self):
        '''Open an existing job.'''
        
        selectedFileName = file_dlg('*.sqlite')
        if selectedFileName:
            carhabLayer = WorkLayer(selectedFileName)
            WorkLayerRegistry.instance().addWorkLayer(carhabLayer)
        