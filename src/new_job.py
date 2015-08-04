# -*- coding: utf-8 -*-
from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI
from PyQt4.uic import *
from PyQt4.QtGui import QMessageBox ,QDateEdit, QPushButton, QLineEdit, QFileDialog, QDialogButtonBox, QComboBox, QDialog
from PyQt4.QtCore import Qt, SIGNAL, QDate
from custom_maptool import CustomMapTool
import os.path
from db import Db, Session
from geo_model import Polygon, PolygonModel
from semantic_model import Job, JobModel, Uvc, UvcModel
from itertools import count
from import_file import Import
from qgis.utils import iface
import time

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
        dialog = QFileDialog(None,'Enregistrer sous...')
        dialog.setAcceptMode(1)
        dialog.setFilter('*.sqlite')
        dialog.setDefaultSuffix('sqlite')
        dialog.setReadOnly(False)
        #dialog.setText('Enregistrer sous...')
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
            self.createJob(fileName)
    
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

    def createJob(self, jobName):
        print QgsMapLayerRegistry.instance().mapLayers()
        for layerName, layer in QgsMapLayerRegistry.instance().mapLayers().items():
            dbPath = QgsDataSourceURI(layer.dataProvider().dataSourceUri()).database()
            if dbPath == jobName:
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
        if os.path.exists(jobName):
            Db(jobName).deleteDb()
        Db(jobName)
        
        job = Job()
        job.name = self.extractNameFromPath(jobName)
        job.organism = self.newJobDialog.findChild(QComboBox,'cb_box_orga').currentText()
        job.author = self.newJobDialog.findChild(QComboBox,'cb_box_pers').currentText()
        job.date = self.newJobDialog.findChild(QDateEdit,'date_edit_creation_job').date()
        JobModel().insert(job)

        for tableToLoad in ('point', 'polyline', 'polygon'):
            self.loadLayerTable(tableToLoad)

    def popup(self, msg):
        '''Display a popup.
        
            :param msg: The message to display.
            :type msg: str
        '''
        
        msgBox = QMessageBox()
        msgBox.setText(msg.decode('utf-8'))
        msgBox.exec_()