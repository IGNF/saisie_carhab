# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, pyqtSignal, QObject, QSettings
from PyQt4.QtGui import QLineEdit, QComboBox

from qgis.utils import iface

from utils_job import no_carhab_lyr_msg, no_vector_lyr_msg,\
    one_only_selected_feat_msg, close_form_required_lyr_msg,\
    warning_input_lost_msg, question
from check_completion import CheckCompletion
from carhab_layer_manager import CarhabLayerRegistry
from db_manager import DbManager
from recorder import Recorder
from relations_manager import RelationsManager
from form import Form
from catalog_reader import CatalogReader

class FormManager(QObject):
    
#    Signals:
    
    submitted = pyqtSignal(bool, str, object)
    
    
#    Slots:
    
    def _block_change(self, selected, deselected, clearAndSelect):
        close_form_required_lyr_msg()
        cur_lyr = iface.mapCanvas().currentLayer()
        cur_lyr.selectionChanged.disconnect(self._block_change)
        cur_lyr.setSelectedFeatures([self.cur_feat.id()])
        cur_lyr.selectionChanged.connect(self._block_change)
    
    def _on_record_submitted(self, upd, table_name, obj):
        if table_name == 'sigmaf':
            self.rel_sf.upd_item(obj) if upd else self.rel_sf.add_item(obj)
        elif table_name == 'composyntaxon':
            self.rel_syn.upd_item(obj) if upd else self.rel_syn.add_item(obj)
        
    def _get_syntax(self, idx):
        self.sf_form.relation.init_table()
        code = self.sf_form.ui.findChild(QComboBox, 'code_sigma').itemData(idx)
        syntax_list = CatalogReader('sigmaf').get_syntaxons_from_sf(code)
        for syntax in syntax_list:
            uvc = iface.mapCanvas().currentLayer().selectedFeatures()[0]['uvc']
            syntax['uvc'] = uvc
            cur_sf = self.sf_form.feat_id
            if cur_sf:
                syntax['sigmaf'] = cur_sf
            else:
                s = QSettings()
                syntax['sigmaf'] = s.value('current_info/sigmaf')
            self.submit('composyntaxon', syntax, None)
        
        
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
        if self.uvc_form and self.uvc_form.ui.isVisible():
            return False
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
    
    def _exit_fill_form(self):
        cur_lyr = iface.mapCanvas().currentLayer()
        try:
            cur_lyr.selectionChanged.disconnect(self._block_change)
        except:
            pass
        try:
            self.submitted.disconnect(self._on_record_submitted)
        except:
            pass
        
    def _open_form(self, tbl_name, form):
        if form.relation:
            r = self.get_recorder(form.relation.child_table)
            child_items = r.select(tbl_name, form.feat_id)
            form.relation.fill_table(child_items)

        db_obj = self.get_record(tbl_name, form.feat_id)
        form.fill_form(db_obj)

        form.open()
    
    
#    Public methods:
    
    def run(self):
        try:
            self.submitted.disconnect(self._on_record_submitted)
        except:
            pass
        if self._check_state():
            self.submitted.connect(self._on_record_submitted)
            
            cur_lyr = iface.mapCanvas().currentLayer()
            cur_lyr.selectionChanged.connect(self._block_change)
            self.cur_feat = self._get_selected_feature()
            uvc_id = self.cur_feat['uvc']
            self.db = self.get_db()
            disp_fields = ['id',\
                'code_serie',\
                'lb_serie',\
                'typ_facies',\
                'pct_recouv']
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
            
            self.uvc_form.valid_clicked.connect(self.submit_uvc)
            self.uvc_form.canceled.connect(self.cancel_uvc_fill)
            self.uvc_form.closed.connect(self._exit_fill_form)
            self._open_form('uvc', self.uvc_form)
            
    
    def open_sf(self, table_name, id=None):
        self.db.execute('SAVEPOINT sigmaf;')
        s = QSettings()
        s.setValue('current_info/sigmaf', id)
        disp_fields = ['cd_syntax', 'lb_syntax', 'abon_domin']
        self.rel_syn = RelationsManager('composyntaxon', disp_fields)
        self.rel_syn.add_clicked.connect(self.open_syntaxon)
        self.rel_syn.edit_clicked.connect(self.open_syntaxon)
        self.rel_syn.del_clicked.connect(self.del_record)
        
        from_cat = False
        r = self.get_recorder('sigmaf')
        if id:
            cat_val = r.select('id', id)[0].get('catalog')
            from_cat = True if cat_val.lower() == 'true' else False
        else:
            last_sf_id = r.get_last_id() if r.get_last_id() else 0
            s.setValue('current_info/sigmaf', last_sf_id + 1)
            from_cat = question('Appel aux catalogues ?,',\
                'Sélectionner un sigma facies issu des catalogues ?')
            s.setValue('current_info/sigmaf/catalog', from_cat)
                
        self.sf_form = Form('form_sigmaf_cat', id, self.rel_syn) if from_cat\
            else Form('form_sigmaf', id, self.rel_syn)
        
        cd_sf_field = self.sf_form.ui.findChild(QComboBox, 'code_sigma')
        if cd_sf_field:
            cd_sf_field.currentIndexChanged.connect(self._get_syntax)
        self.sf_form.canceled.connect(self.rollback)
        self.sf_form.canceled.connect(self.cancel_sf_fill)
        self.sf_form.valid_clicked.connect(self.submit)
        self._open_form('sigmaf', self.sf_form)
        
    def open_syntaxon(self, table_name, id=None):
        self.syntax_form = Form('form_syntaxon', id)
        self.syntax_form.canceled.connect(self.cancel_syntaxon_fill)
        self.syntax_form.valid_clicked.connect(self.submit)
        self._open_form('composyntaxon', self.syntax_form)

    def cancel_uvc_fill(self):
        if warning_input_lost_msg():
            self.close_db()
            self.uvc_form.close()

    def cancel_sf_fill(self):
        self.rollback()
        self.sf_form.close()
        
    def cancel_syntaxon_fill(self):
        self.syntax_form.close()
            
#    Db methods :
    
    def get_db(self):
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        return db
    
    def close_db(self):
        self.db.close()
    
    def rollback(self):
        self.db.execute('ROLLBACK TO SAVEPOINT sigmaf;')
    
    def get_recorder(self, tbl):
        db = self.db
        r = Recorder(db, tbl)
        return r
    
    def get_record(self, tbl, id):
        r = self.get_recorder(tbl)
        db_obj = {}
        for row in r.select('id', id):
            db_obj = row
        return db_obj
    
    def del_record(self, table_name, id):
        db = self.db
        r = Recorder(db, table_name)
        r.delete_row(id)
    
    def submit(self, table_name, form_obj, id):
        db = self.db
        r = Recorder(db, table_name)
        updated = True
        if id:
            r.update(id, form_obj)
        else:
            r.input(form_obj)
            updated = False
            form_obj['id'] = r.get_last_id()
        self.submitted.emit(updated, table_name, form_obj)
        
    def submit_uvc(self, table_name, form_obj, id):
        self.submit(table_name, form_obj, id)
        self.db.commit()
        CheckCompletion().check(self.db)
        iface.mapCanvas().currentLayer().triggerRepaint()
        self.close_db()
        