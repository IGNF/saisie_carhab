# -*- coding: utf-8 -*-
from qgis.utils import iface
from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2, QgsSingleSymbolRendererV2, QgsSimpleMarkerSymbolLayerV2, QgsApplication
        
class CheckCompletion(object):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self):
        """ Constructor. """
        
        
        pass
        
    def run(self):
        '''Specific stuff at tool activating.'''
        
        print 'run check completion'
        layer = iface.mapCanvas().currentLayer()
        # define a lookup: value -> (color, label)
        completion = {
            0: ('#f00', 'Aucune saisie'.decode('utf-8')),
            1: ('#f90', 'Saisie incomplète'.decode('utf-8')),
            2: ('#0f0', 'Saisie complète'.decode('utf-8'))
        }
        
        # create a category for each item in animals
        categories = []
        for completion_code, (color, label) in completion.items():
            symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
            symbol.setColor(QColor(color))
            category = QgsRendererCategoryV2(completion_code, symbol, label)
            categories.append(category)
        
        # create the renderer and assign it to a layer
        expression = 'lgd_compl' # field name
        renderer = QgsCategorizedSymbolRendererV2(expression, categories)
        layer.setRendererV2(renderer)
        layer.triggerRepaint()
        QgsApplication.processEvents()
        print categories