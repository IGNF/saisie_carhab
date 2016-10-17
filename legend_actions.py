# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from qgis.utils import iface
from communication import pluginDirectory
from action import findButtonByActionName
from PyQt4.QtGui import QColor
from PyQt4.QtCore import QSettings
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2,\
    QgsCategorizedSymbolRendererV2

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
        
        s = QSettings()
        layer = iface.mapCanvas().currentLayer()
        if not layer:
            return
        if findButtonByActionName('Afficher avancement de la saisie').isChecked():
            
            # define a lookup: value -> (color, label)
            completion = {
                0: ('#ddd', 'Aucune saisie'),
                1: ('#7a7', 'Saisie partielle'),
                2: ('#0c0', 'Saisie complète')
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
            if not s.value('layer_lgd_style/' + layer.name()):
                layer.saveNamedStyle(styleName)
                layer.setRendererV2(renderer)
                s.setValue('layer_lgd_style/' + layer.name(), 1)
        else:
            styleName = pluginDirectory + "/" + layer.name() + '.qml'
            layer.loadNamedStyle(styleName)
            s.setValue('layer_lgd_style/' + layer.name() + '/', 0)
        layer.triggerRepaint()
        