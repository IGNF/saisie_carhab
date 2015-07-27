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
        
        # Load Qt UI dialog widget from dir path
        pluginDirectory = os.path.dirname(__file__)
        self.openJobDialog = loadUi( os.path.join(pluginDirectory, "open_job.ui"))
        
        # Connect UI components to actions
        self.openJobDialog.findChild(QPushButton,'psh_btn_open_job').clicked.connect(self.selectJob)
        self.openJobDialog.findChild(QDialogButtonBox,'btn_box_open_job').accepted.connect(self.loadMapLayers)

    def run(self):
        '''Specific stuff at tool activating.'''
        
        # Show the dialog
        self.openJobDialog.show()
        
    def selectJob(self):
        
        self.openJobDialog.findChild(QLineEdit,'line_edit_open_job').setText(QFileDialog.getOpenFileName(self.openJobDialog,
                                                                                                            "Open File",
                                                                                                            "",
                                                                                                            "Sqlite (*.sqlite)"))
        
    def loadMapLayers(self):
        
        Db(self.openJobDialog.findChild(QLineEdit, 'line_edit_open_job').text())
        lyrs = []
        for tableToImport in ('point', 'polyline', 'polygon'):
            lyrs.append(NewJob(self.iface).loadLayerTable(tableToImport))