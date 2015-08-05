from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI
from PyQt4.uic import *
from PyQt4.QtGui import QMessageBox ,QDateEdit, QPushButton, QLineEdit, QFileDialog, QDialogButtonBox, QComboBox
from PyQt4.QtCore import Qt, SIGNAL, QDate
import os.path
from db import Db, Session
from geo_model import PolygonModel
from semantic_model import Job, JobModel
from new_job import NewJob
from carhab_layer_registry import *
from import_layer import ImportLayer

class OpenJob(object):
    """
    /***************************************************************************
     Fusion Class
            
            Do the stuff merging features.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """
        Constructor.
    
        :param iface: Interface of QGIS.
        :type iface: QgisInterface
        """
        
        self.iface = iface
        self.canvas = iface.mapCanvas()
        
       
    def run(self):
        '''Specific stuff at tool activating.'''
        
        selectedFileName = ImportLayer(self.iface).execFileDialog('*.sqlite')
        if selectedFileName:
            self.loadMapLayers(selectedFileName)

    def loadMapLayers(self, carhabFilePath):
        
        carhabLayer = CarhabLayer(carhabFilePath)
        CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)