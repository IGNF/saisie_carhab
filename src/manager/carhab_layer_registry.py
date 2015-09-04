# -*- coding: utf-8 -*-
import os.path
from datetime import datetime

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, QgsCoordinateReferenceSystem, QgsProject, QgsRendererV2Registry, QgsApplication, QgsSingleSymbolRendererV2
from qgis.utils import iface

from PyQt4.QtGui import QLabel, QListWidgetItem, QListWidget
from PyQt4.QtCore import Qt, QSize
from PyQt4.uic import loadUi

from utils_job import pluginDirectory
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
        
        def getName(self):
            return os.path.splitext(os.path.basename(self.dbPath))[0]
        
        def getQgisLayers(self):
            qgisLayers = []
            for layerName, layer in QgsMapLayerRegistry.instance().mapLayers().items():
                if layer.customProperty("carhabLayer", "") == self.id:
                    qgisLayers.append(layer)
            return qgisLayers
        
@Singleton
class CarhabLayerRegistry:

        def __init__(self):
            print 'CarhabLayerRegistry created !'
            self.layerMap = {}
            self.currentLayer = None
            self.carhabLayersListUi = loadUi(os.path.join(pluginDirectory, 'carhab_layers_list.ui'))
            #QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.manageCarhabLayerRemove)
          
        def loadLayerTable(self, carhabLayer, tableName):
            
            # Retrieve layer from provider.
            uri = QgsDataSourceURI()
            uri.setDatabase(carhabLayer.dbPath)
            
            schema = ''
            geom_column = 'the_geom'
            uri.setDataSource(schema, tableName, geom_column)
            
            display_name = carhabLayer.getName()+'_'+tableName
            
            layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
            layer.setCrs(QgsCoordinateReferenceSystem(2154,  QgsCoordinateReferenceSystem.EpsgCrsId))
            
            # "Bind" layer to carhab layer.
            if self.getCarhabLayerFromDbPath(carhabLayer.dbPath):
                layer.setCustomProperty('carhabLayer', carhabLayer.id)
            
            # Add layer to map (False to add to group)
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            
            iface.mapCanvas().setExtent(layer.extent())
            
            return layer
            
        def displayCompletionLegend(self, active):
            if active :
                check_completion = CheckCompletion()
                check_completion.run()
        
        def getCarhabLayerFromDbPath(self, dbPath):
            for id, carhabLayer in self.layerMap.items():
                if carhabLayer.dbPath == dbPath:
                    return carhabLayer
            return None
        
        def getCarhabLayerFromName(self, carhabLayerName):
            for id, carhabLayer in self.layerMap.items():
                if carhabLayer.getName() == carhabLayerName:
                    return carhabLayer
            return None

        def getCarhabLayerListItem(self, carhabLayerName):
            carhabLyrList = self.carhabLayersListUi.findChild(QListWidget, 'listWidget')
            for index in xrange(carhabLyrList.count()):
                wdgtItem = self.carhabLayersListUi.findChild(QListWidget, 'listWidget').item(index)
                for label in carhabLyrList.itemWidget(wdgtItem).findChildren(QLabel):
                    if label.text() == carhabLayerName:
                        return wdgtItem
            return None
        
        def addCarhabLayer(self, carhabLayer):
            
            self.layerMap[carhabLayer.id] = carhabLayer
            
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup('carhab_'+carhabLayer.getName())
            
            for tableToLoad in ('point', 'polyline', 'polygon'):
                group.addLayer(self.loadLayerTable(carhabLayer, tableToLoad))
                #self.loadLayerTable(carhabLayer.dbPath, tableToLoad)
            
            self.currentLayer = carhabLayer
            
            # Create row corresponding to carhab layer into carhab layer list.
            carhabLayerWdgt = loadUi(os.path.join(pluginDirectory, 'carhab_layer_item.ui'))
            carhabLayerWdgt.findChild(QLabel, 'job_name_label').setText(carhabLayer.getName())
            
            carhabLayerItem = QListWidgetItem()
            carhabLayerItem.setSizeHint(QSize(100,60))
            
            self.carhabLayersListUi.findChild(QListWidget, 'listWidget').addItem(carhabLayerItem)
            self.carhabLayersListUi.findChild(QListWidget, 'listWidget').setItemWidget(carhabLayerItem, carhabLayerWdgt)
            
            # Show the carhab layer list
            iface.addDockWidget(Qt.LeftDockWidgetArea, self.carhabLayersListUi)
        
        def removeCarhabLayer(self, carhabLayer):
            for layerName, layer in QgsMapLayerRegistry.instance().mapLayers().items():
                if layer.customProperty("carhabLayer", "") == carhabLayer.id:
                    QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            
            if self.getCarhabLayerListItem(carhabLayer.getName()):
                carhabLyrList = self.carhabLayersListUi.findChild(QListWidget, 'listWidget')
                carhabLyrList.takeItem(carhabLyrList.row(self.getCarhabLayerListItem(carhabLayer.getName())))
            self.layerMap.pop(carhabLayer.id, None)
