# -*- coding: utf-8 -*-
from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI
from PyQt4.uic import *
from PyQt4.QtGui import QMessageBox ,QDateEdit, QPushButton, QLineEdit, QFileDialog, QDialogButtonBox, QComboBox, QDialog
from PyQt4.QtCore import Qt, SIGNAL, QDate
from custom_maptool import CustomMapTool
import os.path
from geo_model import Polygon, PolygonModel
from semantic_model import Job, JobModel, Uvc, UvcModel
from itertools import count
from import_file import Import
from qgis.utils import iface
import time
import shutil
from import_layer import ImportLayer

from carhab_layer_registry import *

class NewJob(object):
    """
    /***************************************************************************
     NewLayer Class
            
            Do the stuff creating a work layer in spatialite format.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """
        Constructor :
    
        :param iface: Interface of QGIS.
        :type iface: QgisInterface
        """
        
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # Load Qt UI dialog widget from dir path
        pluginDirectory = os.path.dirname(__file__)
        self.newJobDialog = loadUi( os.path.join(pluginDirectory, "new_job.ui"))
        
        self.newJobDialog.findChild(QDateEdit,'date_edit_creation_job').setDate(QDate.currentDate()) # Set current date into form
        
        # Connect UI components to actions
        self.newJobDialog.findChild(QDialogButtonBox,'btn_box_job').accepted.connect(self.setDestinationFile)

    def run(self):
        '''Specific stuff at tool activating.'''
        
        # Show the dialog
        self.newJobDialog.show()
        
    def setDestinationFile(self):
        
        selectedFileName = ImportLayer(self.iface).execFileDialog('*.sqlite', 'Enregistrer sous...', 'save')
        if selectedFileName:
            self.createJob(selectedFileName)
        

    def extractNameFromPath(self, path):
        ''' Extract file name without extension. '''
        
        return path.split('/')[len(path.split('/')) - 1].split('.')[0]

    def createJob(self, jobName):
        print QgsMapLayerRegistry.instance().mapLayers()
        carhabLayer = CarhabLayer(jobName) 
        CarhabLayerRegistry.instance().removeCarhabLayer(carhabLayer)
        
        if os.path.exists(jobName):
            os.remove(jobName)
        
        plugin_dir = os.path.dirname( os.path.abspath( __file__ ) )
        emptyDb = os.path.join(plugin_dir, 'empty.sqlite')
        shutil.copy(emptyDb, jobName)
        
        CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
                
        job = Job()
        job.name = self.extractNameFromPath(jobName)
        job.organism = self.newJobDialog.findChild(QComboBox,'cb_box_orga').currentText()
        job.author = self.newJobDialog.findChild(QComboBox,'cb_box_pers').currentText()
        job.date = self.newJobDialog.findChild(QDateEdit,'date_edit_creation_job').date()
        JobModel().insert(job)
        

    def popup(self, msg):
        '''Display a popup.
        
            :param msg: The message to display.
            :type msg: str
        '''
        
        msgBox = QMessageBox()
        msgBox.setText(msg.decode('utf-8'))
        msgBox.exec_()