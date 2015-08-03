# -*- coding: utf-8 -*-
from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI
from PyQt4.uic import *
from PyQt4.QtGui import QMessageBox ,QDateEdit, QPushButton, QLineEdit, QFileDialog, QDialogButtonBox, QComboBox
from PyQt4.QtCore import Qt, SIGNAL, QDate
from custom_maptool import CustomMapTool
import os.path
from db import Db, Session
from geo_model import Polygon, PolygonModel
from semantic_model import Job, JobModel, Uvc, UvcModel
from itertools import count

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
        self.newJobDialog.findChild(QPushButton,'psh_btn_src_lyr').clicked.connect(self.selectSourceFile)
        self.newJobDialog.findChild(QPushButton,'psh_btn_dest_lyr').clicked.connect(self.setDestinationFile)
        self.newJobDialog.findChild(QDialogButtonBox,'btn_box_job').accepted.connect(self.createJob)

    def run(self):
        '''Specific stuff at tool activating.'''
        
        # Show the dialog
        self.newJobDialog.show()

    def selectSourceFile(self):
        self.newJobDialog.findChild(QLineEdit,'line_edit_src_lyr').setText(QFileDialog.getOpenFileName())
    
    def setDestinationFile(self):
        dialog = QFileDialog()
        dialog.setReadOnly(False)
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
            fileExtension = '.sqlite'
            if not fileName[-7:] == fileExtension :
                fileName = fileName + fileExtension

            self.newJobDialog.findChild(QLineEdit,'line_edit_dest_lyr').setText(fileName)
    
    def checkJob(self):
        self.jobName = self.newJobDialog.findChild(QLineEdit,'line_edit_dest_lyr').text()

        if os.path.exists(self.jobName):
            msg = 'La couche '+str(self.jobName)+' existe déjà.'
            self.popup(msg.decode('utf8'))
            return False

        if not self.jobName:
            msg = 'Veuillez sélectionner un fichier'
            self.popup(msg)
            return False
        return True
    
    def loadLayerTable(self, tableName):
        
        uri = QgsDataSourceURI()
        uri.setDatabase(Session().dbPath)
        schema = ''
        geom_column = 'the_geom'
        uri.setDataSource(schema, tableName, geom_column)
        display_name = tableName
        
        layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        self.canvas.setExtent(layer.extent())
        return layer
        

    def extractNameFromPath(self, path):
        ''' Extract file name without extension. '''
        
        return path.split('/')[len(path.split('/')) - 1].split('.')[0]

    def createJob(self):
        if self.checkJob():
            Db(self.jobName)

            sourceLayerPath = self.newJobDialog.findChild(QLineEdit,'line_edit_src_lyr').text()
            ''' if sourceLayerPath: # If a source layer has been specified
                errors = PolygonModel().importFeaturesFromFile(sourceLayerPath)
                if len(errors) > 0:
                    NewJob(self.iface).popup('Des géométries de la couche source sont invalides. Des entités n\'ont donc pas été importées : '+str(errors))
            '''
            job = Job()
            job.name = self.extractNameFromPath(self.jobName)
            job.organism = self.newJobDialog.findChild(QComboBox,'cb_box_orga').currentText()
            job.author = self.newJobDialog.findChild(QComboBox,'cb_box_pers').currentText()
            job.date = self.newJobDialog.findChild(QDateEdit,'date_edit_creation_job').date()
            JobModel().insert(job)

            for tableToLoad in ('point', 'polyline', 'polygon'):
                self.loadLayerTable(tableToLoad)
        else:
            self.newJobDialog.show()

    def popup(self, msg):
        '''Display a popup.
        
            :param msg: The message to display.
            :type msg: str
        '''
        
        msgBox = QMessageBox()
        msgBox.setText(msg.decode('utf-8'))
        msgBox.exec_()