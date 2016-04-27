# -*- coding: utf-8 -*-
from qgis.utils import iface
from utils_job import pluginDirectory, findButtonByActionName
from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2,\
    QgsCategorizedSymbolRendererV2
from db_manager import DbManager
from carhab_layer_manager import CarhabLayerRegistry
from recorder import Recorder

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
    
    def check(self):
        cur_crhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_crhab_lyr.dbPath)
        mandat_uvc_fields = ['aut_crea',
                             'orga_crea',
                             'mode_carac',
                             'mode_obser',
                             'echelle']
        r = Recorder(db, 'uvc')
        uvc_list = r.select_all()
        layer = iface.mapCanvas().currentLayer()
        for uvc in uvc_list:
            full_att = 0
            full_sf = 0
            full_indic = 0
            count_filled = 0
            for mf in mandat_uvc_fields:
                if uvc[mf]:
                    count_filled += 1
            if count_filled == 5:
                full_att = 2
            elif count_filled == 0:
                full_att = 0
            else:
                full_att = 1
            r = Recorder(db, 'sigmaf')
            sf_list = r.select_all()
            for sf in sf_list:
                if sf['uvc'] == uvc['id']:
                    full_sf = 2
                    break
            if full_att == 0 and full_sf == 0:
                full_indic = 0
            elif full_sf == 2 and full_att == 2:
                full_indic = 2
            else: 
                full_indic = 1
            if layer.geometryType() == 0:
                r = Recorder(db, 'point')
            if layer.geometryType() == 1:
                r = Recorder(db, 'polyline')
            if layer.geometryType() == 2:
                r = Recorder(db, 'polygon')
            geom_res = r.select('uvc', uvc['id'])
            if len(geom_res) > 0:
                geom_id = geom_res[0]['id']
                r.update(geom_id, {'lgd_compl': full_indic})
        db.commit()
        db.close()
            
    def run(self):
        '''Specific stuff at tool activating.'''
        layer = iface.mapCanvas().currentLayer()
        if not layer:
            return
        if findButtonByActionName('Afficher avancement de la saisie').isChecked():
            self.check()
            # define a lookup: value -> (color, label)
            completion = {
                0: ('#ddd', 'Aucune saisie'.decode('utf-8')),
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
            print styleName
            layer.loadNamedStyle(styleName.decode('utf-8'))
        
        layer.triggerRepaint()
        