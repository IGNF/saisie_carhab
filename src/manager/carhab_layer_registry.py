from datetime import datetime, date, time

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, QgsCoordinateReferenceSystem
from qgis.utils import iface

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

          
        def loadLayerTable(self, dbPath, tableName):
            
            uri = QgsDataSourceURI()
            uri.setDatabase(dbPath)
            schema = ''
            geom_column = 'the_geom'
            uri.setDataSource(schema, tableName, geom_column)
            display_name = tableName
            
            layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
            layer.setCrs(QgsCoordinateReferenceSystem(2154,  QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            iface.mapCanvas().setExtent(layer.extent())
            return layer
            
        def addCarhabLayer(self, carhabLayer):
            
            self.layerMap[carhabLayer.id] = carhabLayer;
            for tableToLoad in ('point', 'polyline', 'polygon'):
                self.loadLayerTable(carhabLayer.dbPath, tableToLoad)
                
            self.currentLayer = carhabLayer
    
        def removeCarhabLayer(self, carhabLayer):
            for layerName, layer in QgsMapLayerRegistry.instance().mapLayers().items():
                dbPath = QgsDataSourceURI(layer.dataProvider().dataSourceUri()).database()
                if dbPath == carhabLayer.dbPath:
                    QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            
            #del self.layerMap[carhabLayer.id]

