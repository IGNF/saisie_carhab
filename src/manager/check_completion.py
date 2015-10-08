# -*- coding: utf-8 -*-
from qgis.utils import iface
from utils_job import pluginDirectory, findButtonByActionName
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

        layer = iface.mapCanvas().currentLayer()
        if not layer:
            return
        if findButtonByActionName('Afficher avancement de la saisie').isChecked():
            # define a lookup: value -> (color, label)
            completion = {
                0: ('#ddd', 'Aucune aisie'.decode('utf-8')),
                1: ('#7a7', 'Saisie partielle'.decode('utf-8')),
                2: ('#0c0', 'Saisie complète'.decode('utf-8'))
            }
            
            # create a category for each item
            categories = []
            for completion_code, (color, label) in completion.items():
                symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
                symbol.setColor(QColor(color))
                category = QgsRendererCategoryV2(completion_code, symbol, label)
                categories.append(category)
            
            # create the renderer and assign it to a layer
            expression = 'lgd_compl' # field name
            renderer = QgsCategorizedSymbolRendererV2(expression, categories)
            styleName = pluginDirectory + "/" + layer.name() + '.qml'
            layer.saveNamedStyle(styleName)
            layer.setRendererV2(renderer)
    
        else:
            styleName = pluginDirectory + "/" + layer.name() + '.qml'
            layer.loadNamedStyle(styleName.decode('utf-8'))
        
        layer.triggerRepaint()
        