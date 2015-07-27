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

class ImportLayer(object):
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
        self.openJobDialog = loadUi( os.path.join(pluginDirectory, "import_features.ui"))
        
        # Connect UI components to actions
        self.openJobDialog.findChild(QPushButton,'psh_btn_import_lyr').clicked.connect(self.selectFile)
        self.openJobDialog.findChild(QDialogButtonBox,'btn_box_import_lyr').accepted.connect(self.importLayer)

    def run(self):
        '''Specific stuff at tool activating.'''
        
        # Show the dialog
        self.openJobDialog.show()
        
    def selectFile(self):
        
        self.openJobDialog.findChild(QLineEdit,'line_edit_import_lyr').setText(QFileDialog.getOpenFileName(self.openJobDialog,
                                                                                                            "Open File",
                                                                                                            "",
                                                                                                            "Shapefiles (*.shp)"))
    def importLayer(self):
        importFilePath = self.openJobDialog.findChild(QLineEdit, 'line_edit_import_lyr').text()
        if importFilePath:
            NewJob(self.iface).importFeaturesFromFile(importFilePath)
        else:
            NewJob(self.iface).popup('Selectionner un fichier source')
            self.run()