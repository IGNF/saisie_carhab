# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from qgis.utils import iface
from qgis.core import QgsGeometry
from qgis.gui import QgsMapTool, QgsRubberBand


from communication import question, popup
from db_manager import Db, Recorder
from work_layer import WorkLayerRegistry
from form_manager import FormManager

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
        for f in features:
            if QgsGeometry().fromPoint(point).intersects(f.geometry()):
                rb = QgsRubberBand(self.canvas, True)
                color = QColor(255, 71, 25, 170)
                rb.setColor(color)
                rb.setToGeometry(f.geometry(), None)
                feat = f
        if feat:
            q = True
            lgd_empty = True
            for sel_feat in sel_features:
                if sel_feat['lgd_compl'] != 0:
                    lgd_empty = False
                    break
            if not lgd_empty:
                q = question('Continuer ? ', \
                        'Risque d\'écrasement de données pour les ' \
                        'entités sélectionnées')
            if q:
                self.duplicate(sel_features, feat)
                popup('Duplication(s) réalisée(s)')
            self.canvas.scene().removeItem(rb)
                
    def duplicate(self, features, tpl_feat):
        cur_carhab_lyr = WorkLayerRegistry.instance().current_work_layer()
        db = Db(cur_carhab_lyr.dbPath)
        r = Recorder(db, 'uvc')
        uvc = {}
        unchanged = ['surface', 'calc_surf', 'id']
        for feature in features:
            for row in r.select('id', tpl_feat['uvc']):
                uvc = row
                uvc = {f:v for f,v in row.items() if not f in unchanged}
                uvc['id'] = feature['uvc']
            r2 = Recorder(db, 'sigmaf')
            sfs = []
            for sf in r2.select('uvc', tpl_feat['uvc']):
                sf['uvc'] = feature['uvc']
                sfs.append(sf)
            r3 = Recorder(db, 'composyntaxon')
            for row in r2.select('uvc', feature['uvc']):
                r2.delete_row(row['id'])
            for sf in sfs:
                old_sf_id = sf['id']
                sf.pop('id', None)
                r2.input(sf)
                sf_id = r2.get_last_id()
                for row in r3.select('sigmaf', old_sf_id):
                    synt = row
                    synt.pop('id', None)
                    synt['sigmaf'] = sf_id
                    synt['uvc'] = feature['uvc']
                    r3.input(synt)
            r.update(uvc['id'], uvc)
        db.commit()
        iface.mapCanvas().currentLayer().triggerRepaint()
        db.close()
        
class Eraser(object):
    def __init__(self):
        pass
      
    def erase(self):
        try:
            FormManager.instance().uvc_form.upd_flag = False
            FormManager.instance().uvc_form._cancel()
        except:
            pass
        msg = 'Êtes-vous sûr de vouloir effacer toute la saisie réalisée '
        msg += 'pour chacune des entités sélectionnées ?'
        if question('Continuer ?', msg):
            cur_carhab_lyr = WorkLayerRegistry.instance().current_work_layer()
            db = Db(cur_carhab_lyr.dbPath)
            r = Recorder(db, 'uvc')
            cur_lyr = iface.mapCanvas().currentLayer()
            sel_features = cur_lyr.selectedFeatures()
            for f in sel_features:
                uvc_id = f['uvc']
                uvc_to_erase = r.select('id', uvc_id)[0]
                r_sf = Recorder(db, 'sigmaf')
                sf_to_del_lst = r_sf.select('uvc', uvc_id)
                for sf in sf_to_del_lst:
                    r_sf.delete_row(sf.get('id'))
                uvc = {}
                
                for field, value in uvc_to_erase.items():
                    unchanged = ['surface', 'calc_surf', 'larg_lin', 'id']
                    uvc[field] = None if field not in unchanged else value
                r.update(uvc_id, uvc)
            db.commit()
            db.close()
            popup('Effacement terminé')
            iface.mapCanvas().currentLayer().triggerRepaint()