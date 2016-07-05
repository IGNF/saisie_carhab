# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from qgis.utils import iface
from qgis.core import QgsGeometry
from qgis.gui import QgsMapTool, QgsRubberBand


from utils_job import question, no_carhab_lyr_msg, no_vector_lyr_msg,\
    no_selected_feat_msg, selection_out_of_lyr_msg
from db_manager import DbManager
from recorder import Recorder
from carhab_layer_manager import CarhabLayerRegistry

class Duplicate(QgsMapTool):
    def __init__(self, canvas):
        self.canvas = canvas
        # Declare inheritance to QgsMapTool class.
        super(QgsMapTool, self).__init__(canvas)

    def canvasPressEvent(self, event):
        '''Override slot fired when mouse is pressed.'''
        features = self.canvas.currentLayer().getFeatures()
        sel_features = self.canvas.currentLayer().selectedFeatures()
        point = self.toMapCoordinates(QPoint(event.pos().x(), event.pos().y()))
        i = 1
        for f in features:
            print str(i)
            i = i + 1
            if QgsGeometry().fromPoint(point).intersects(f.geometry()):
                rb = QgsRubberBand(self.canvas, True)
                color = QColor(255, 71, 25, 170)
                rb.setColor(color)
                rb.setToGeometry(f.geometry(), None)
                feat = f
                break
        if feat:
#            q = question('Continuer ? ', \
#                    'Risque d\'écrasement de données pour les ' \
#                    'entités sélectionnées')
#            if q:
            self.duplicate(sel_features, feat)
            self.canvas.scene().removeItem(rb)
                
    def duplicate(self, features, tpl_feat):
        print 'dupl'
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, 'uvc')
        uvc = {}
        for row in r.select('id', tpl_feat['uvc']):
            uvc = row
            uvc['id'] = features[0]['uvc']
        r2 = Recorder(db, 'sigmaf')
        sfs = []
        for row in r2.select('uvc', tpl_feat['uvc']):
            print row
            sf = row
            sf['uvc'] = uvc['id']
            sfs.append(sf)
        r3 = Recorder(db, 'composyntaxon')
        for sf in sfs:
            old_sf_id = sf['id']
            sf.pop('id', None)
            r2.input(sf)
            sf_id = r2.get_last_id()
            for row in r3.select('sigmaf', old_sf_id):
                synt = row
                synt.pop('id', None)
                synt['sigmaf'] = sf_id[0]
                r3.input(synt)
        r.update(uvc['id'], uvc)
        db.commit()
        db.close()