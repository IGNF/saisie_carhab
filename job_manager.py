# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os.path
import shutil

from qgis.gui import *

from work_layer import WorkLayer, WorkLayerRegistry

from communication import pluginDirectory, file_dlg, popup

def create_job():
    '''Create new job.'''

    file_path = file_dlg('*.sqlite', 'Enregistrer sous...', 'save')
    if file_path:
        empty_db = os.path.join(pluginDirectory, 'empty.sqlite')
        shutil.copy(empty_db, file_path)
        work_lyr = WorkLayer(file_path)
        WorkLayerRegistry.instance().add_work_lyr(work_lyr)
        return work_lyr

def open_job():
    '''Open an existing job.'''
    file_path = file_dlg('*.sqlite')
    if file_path:
        if not WorkLayerRegistry.instance().work_lyr_exists(file_path):
            wk_lyr = [wl for wl in WorkLayerRegistry.instance().work_layers.values() if unicode(wl.db_path) == unicode(file_path)]
            wk_lyr = WorkLayer(file_path)
            WorkLayerRegistry.instance().add_work_lyr(wk_lyr)
        else:
            popup('Cette couche de travail est déjà ouverte.')
        