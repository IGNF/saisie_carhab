# -*- coding: utf-8 -*-
import os.path
from datetime import datetime

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, QgsCoordinateReferenceSystem, QgsProject, QgsRendererV2Registry, QgsApplication, QgsSingleSymbolRendererV2
from qgis.utils import iface

from PyQt4.QtGui import QLabel, QListWidgetItem, QListWidget, QPushButton
from PyQt4.QtCore import Qt, QSize
from PyQt4.uic import loadUi

from utils_job import pluginDirectory, question
from check_completion import CheckCompletion

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

class CarhabLayer:
        def __init__(self, dbPath):
            print 'CarhabLayer created !'
            self.dbPath = dbPath
            id = ''
            dt = datetime.now()
            tt = dt.timetuple()
            for it in tt:
                id += str(it)
            self.id = id

@Singleton
class CarhabLayerRegistry:

        def __init__(self):
            print 'CarhabLayerRegistry created !'
            self.layerMap = {}
            self.currentLayer = None
            self.carhabLayersListUi = loadUi(os.path.join(pluginDirectory, 'carhab_layers_list.ui'))
            QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.manageCarhabLayerRemove)
          
        def loadLayerTable(self, dbPath, tableName):
            
            uri = QgsDataSourceURI()
            uri.setDatabase(dbPath)
            schema = ''
            geom_column = 'the_geom'
            uri.setDataSource(schema, tableName, geom_column)
            display_name = os.path.splitext(os.path.basename(dbPath))[0]+'_'+tableName
            
            layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
            layer.setCrs(QgsCoordinateReferenceSystem(2154,  QgsCoordinateReferenceSystem.EpsgCrsId))
            #QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            iface.mapCanvas().setExtent(layer.extent())
            return layer
            
        def displayCompletionLegend(self, active):
            if active :
                check_completion = CheckCompletion()
                check_completion.run()

        def addCarhabLayer(self, carhabLayer):
            self.layerMap[carhabLayer.id] = carhabLayer
            #root = QgsProject.instance().layerTreeRoot()
            #group = root.addGroup('carhab_'+os.path.splitext(os.path.basename(carhabLayer.dbPath))[0])
            for tableToLoad in ('point', 'polyline', 'polygon'):
                #group.addLayer(self.loadLayerTable(carhabLayer.dbPath, tableToLoad))
                self.loadLayerTable(carhabLayer.dbPath, tableToLoad)
                
            self.currentLayer = carhabLayer
            
            carhabLayerWdgt = loadUi(os.path.join(pluginDirectory, 'carhab_layer_item.ui'))
            carhabLayerWdgt.findChild(QLabel, 'label').setText(os.path.splitext(os.path.basename(carhabLayer.dbPath))[0])
            carhabLayerItem = QListWidgetItem()
            carhabLayerItem.setSizeHint(QSize(100,60))
            self.carhabLayersListUi.findChild(QListWidget, 'listWidget').addItem(carhabLayerItem)
            self.carhabLayersListUi.findChild(QListWidget, 'listWidget').setItemWidget(carhabLayerItem, carhabLayerWdgt)
            # Show the carhab layer list
            iface.addDockWidget(Qt.LeftDockWidgetArea, self.carhabLayersListUi)
            print 'before connect'
            print self.carhabLayersListUi.findChild(QPushButton, 'pushButton')
            
            self.carhabLayersListUi.findChild(QPushButton, 'pushButton').toggled.connect(self.displayCompletionLegend)
            
        def manageCarhabLayerRemove(self, layerId):
            title = 'Avertissement.'
            msg = ('Vous êtes sur le point de supprimer '
                      'l\'ensemble des couches contenues '
                      'dans la couche carhab. Continuer ?')
            if question(title, msg):
                pass
                
    
        def removeCarhabLayer(self, carhabLayer):
            for layerName, layer in QgsMapLayerRegistry.instance().mapLayers().items():
                dbPath = QgsDataSourceURI(layer.dataProvider().dataSourceUri()).database()
                if dbPath == carhabLayer.dbPath:
                    QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            
            del self.layerMap[carhabLayer.id]

