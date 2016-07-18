# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, pyqtSignal, QObject, QSettings
from PyQt4.QtGui import QLineEdit

from qgis.utils import iface

from utils_job import no_carhab_lyr_msg, no_vector_lyr_msg,\
    one_only_selected_feat_msg, close_form_required_lyr_msg
from check_completion import CheckCompletion
from carhab_layer_manager import CarhabLayerRegistry
from db_manager import DbManager
from recorder import Recorder
from relations_manager import RelationsManager
from form import Form

class FormManager(QObject):
    
#    Signals:
    
    submitted = pyqtSignal(bool, str, object)
    
    
#    Slots:
    
    def change_feature(self, selected, deselected, clearAndSelect):
        close_form_required_lyr_msg()
        cur_lyr = iface.mapCanvas().currentLayer()
        cur_lyr.selectionChanged.disconnect(self.change_feature)
        cur_lyr.setSelectedFeatures([self.cur_feat.id()])
        cur_lyr.selectionChanged.connect(self.change_feature)
    
    def on_record_submitted(self, upd, table_name, obj):
        CheckCompletion().check()
        iface.mapCanvas().currentLayer().triggerRepaint()
        if table_name == 'sigmaf':
            self.rel_sf.upd_item(obj) if upd else self.rel_sf.add_item(obj)
        elif table_name == 'composyntaxon':
            self.rel_syn.upd_item(obj) if upd else self.rel_syn.add_item(obj)
    
        
#    Constructor:
    
    def __init__(self):
        QObject.__init__(self)
        self.cur_feat = None
        self.uvc_form = None
        self.sf_form = None
        self.syntax_form = None
        self.rel_sf = None
        self.rel_syn = None
    
    
#    Private methods:

    def _get_selected_feature(self):
        cur_lyr = iface.mapCanvas().currentLayer()
        if not cur_lyr:
            return 0
        features = cur_lyr.selectedFeatures()
        feat = features[0] if len(features) == 1 else 1
        return feat

    def _check_state(self):
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        if not cur_carhab_lyr:
            no_carhab_lyr_msg()
            return False
        if self._get_selected_feature() == 0:
            no_vector_lyr_msg()
            return False
        if self._get_selected_feature() == 1:
            one_only_selected_feat_msg()
            return False
        return True
    
    def _open_form(self, tbl_name, form):
        if form.relation:
            r = self.get_recorder(form.relation.child_table)
            child_items = r.select(tbl_name, form.feat_id)
            form.relation.fill_table(child_items)

        db_obj = self.get_record(tbl_name, form.feat_id)
        form.fill(db_obj)
        form.valid_clicked.connect(self.submit)

        form.open()
    
    
#    Public methods:
    
    def run(self):
        if self._check_state():
            try:
                self.submitted.disconnect()
            except:
                pass
            self.submitted.connect(self.on_record_submitted)
            
            self.cur_feat = self._get_selected_feature()
            uvc_id = self.cur_feat['uvc']

            disp_fields = ['id', 'code_serie', 'lb_serie', 'typ_facies']
            self.rel_sf = RelationsManager('sigmaf', disp_fields)
            self.rel_sf.add_clicked.connect(self.open_sf)
            self.rel_sf.edit_clicked.connect(self.open_sf)
            self.rel_sf.del_clicked.connect(self.del_record)
            
            form_position = Qt.RightDockWidgetArea
            self.uvc_form = Form('form_uvc', uvc_id, self.rel_sf, form_position)
            
            cur_geom_typ = self.cur_feat.geometry().type()
            surface_field = self.uvc_form.ui.findChild(QLineEdit, 'surface')
            lin_len_field = self.uvc_form.ui.findChild(QLineEdit, 'larg_lin')
            if cur_geom_typ == 0:
                lin_len_field.setEnabled(False)
                surface_field.setReadOnly(False)
            elif cur_geom_typ == 1:
                lin_len_field.setEnabled(True)
                surface_field.setReadOnly(True)
            else:
                lin_len_field.setEnabled(False)
                surface_field.setReadOnly(True)
            
            self._open_form('uvc', self.uvc_form)
            
    #        iface.mapCanvas().currentLayer().selectionChanged.connect(self.change_feature)
    
    def open_sf(self, table_name, id=None):
        s = QSettings()
        s.setValue('current_info/sigmaf', id)
        disp_fields = ['cd_syntax', u'libellé syntaxon']
        if not id:
            db = self.get_db()
            r = Recorder(db, 'sigmaf')
            s.setValue('current_info/sigmaf', r.get_last_id() + 1)
        self.rel_syn = RelationsManager('composyntaxon', disp_fields)
        self.rel_syn.add_clicked.connect(self.open_syntaxon)
        self.rel_syn.edit_clicked.connect(self.open_syntaxon)
        self.rel_syn.del_clicked.connect(self.del_record)
        
        self.sf_form = Form('form_sigmaf', id, self.rel_syn)
        self._open_form('sigmaf', self.sf_form)
        
    def open_syntaxon(self, table_name, id=None):
        self.syntax_form = Form('form_syntaxon', id)
        self._open_form('composyntaxon', self.syntax_form)


#    Db methods :
    
    def get_db(self):
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        return db
    
    def get_recorder(self, tbl):
        db = self.get_db()
        r = Recorder(db, tbl)
        return r
    
    def get_record(self, tbl, id):
        r = self.get_recorder(tbl)
        db_obj = {}
        for row in r.select('id', id):
            db_obj = row
        return db_obj
    
    def del_record(self, table_name, id):
        db = self.get_db()
        r = Recorder(db, table_name)
        r.delete_row(id)
        db.commit()
        db.close()
    
    def submit(self, table_name, form_obj, id):
        db = self.get_db()
        r = Recorder(db, table_name)
        updated = True
        if id:
            r.update(id, form_obj)
        else:
            r.input(form_obj)
            updated = False
            form_obj['id'] = r.get_last_id()
        db.commit()
        db.close()
        self.submitted.emit(updated, table_name, form_obj)