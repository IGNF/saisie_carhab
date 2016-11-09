# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path

from PyQt4.QtCore import pyqtSignal, QObject, Qt, QDate, QSettings
from PyQt4.QtGui import QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QTextEdit,\
    QDoubleSpinBox, QWidget, QCheckBox, QDateEdit, QDockWidget, QCompleter, QStringListModel
from PyQt4.uic import loadUi

from functools import partial
from qgis.utils import iface
from communication import pluginDirectory, popup, no_work_lyr_msg, no_vector_lyr_msg,\
    one_only_selected_feat_msg, close_form_required_lyr_msg,\
    warning_input_lost_msg, question
from config import DB_STRUCTURE, FORM_STRUCTURE
from catalogs import CatalogReader, Catalog

from work_layer import WorkLayerRegistry
from utils import Singleton
from db_manager import Db, Recorder

class RelationsManager(QObject):
    
#    Signals:
    
    add_clicked = pyqtSignal(str)
    edit_clicked= pyqtSignal(str, str)
    del_clicked = pyqtSignal(str, str)
    
    
#    Slots:
    
    def add_related(self):
        self.add_clicked.emit(self.child_table)
    
    def edit_related(self):
        sel_item_id = self._get_selected_item_id()
        if sel_item_id:
            self.edit_clicked.emit(self.child_table, sel_item_id)
        
    def del_related(self):
        sel_item_id = self._get_selected_item_id()
        self.del_clicked.emit(self.child_table, sel_item_id)
        self._tbl_wdgt.removeRow(self._tbl_wdgt.currentRow())
        self._tbl_wdgt.resizeColumnsToContents()
        self._tbl_wdgt.sizeHint()
        self.unchanged = False

#    Constructor:
    
    def __init__(self, child_table, displayed_fields):
        QObject.__init__(self)
        self.child_table = child_table
        
        self.ui = loadUi(path.join(pluginDirectory, 'relations_widget.ui'))
        self._tbl_wdgt = self.ui.findChild(QTableWidget, 'rel_tbl')
        
        btns = ['add', 'edit', 'delt']
        add, edit, delt = [self.ui.findChild(QPushButton, b) for b in btns]
        add.clicked.connect(self.add_related)
        edit.clicked.connect(self.edit_related)
        delt.clicked.connect(self.del_related)
        
        displayed_fields = displayed_fields\
            if 'id' in [i for i in displayed_fields]\
            else ['id'] + displayed_fields
        
        title = None
        label_fields = []
        for tbl_name, tbl_desc in DB_STRUCTURE:
            if tbl_name == child_table:
                title = tbl_desc.get('label')
                for field, field_desc in tbl_desc.get('fields'):
                    if field in displayed_fields:
                        if field_desc.get('label'):
                            label_fields.append(field_desc.get('label'))
                        else:
                            label_fields.append(field)
                break
        self.displayed_fields = zip(displayed_fields, label_fields)
        self.ui.setTitle(title) if title else child_table
        self.init_table()
    
        
#   Private methods:
    
    def _get_selected_item_id(self):
        sel_item = self._tbl_wdgt.item(self._tbl_wdgt.currentRow(), 0)
        msg = 'Sélectionner une ligne dans le tableau'
        return sel_item.text() if sel_item else popup(msg)
        return False
    
    def _set_item(self, num_row, item):
        colinc = 0
        for field in self.displayed_fields:
            value = unicode(item.get(field[0])) if item.get(field[0]) else None
            cell_item = QTableWidgetItem(value)
            self._tbl_wdgt.setItem(num_row, colinc, cell_item)
            colinc += 1
        self._tbl_wdgt.resizeColumnsToContents()
        self._tbl_wdgt.sizeHint()
    
    
#    Public methods
    
    def init_table(self):
        if self._tbl_wdgt and self.child_table:
            self._tbl_wdgt.setRowCount(0)
            self._tbl_wdgt.setColumnCount(len(self.displayed_fields))
            self._tbl_wdgt.verticalHeader().hide()
            self._tbl_wdgt.setHorizontalHeaderLabels([i[1] for i in self.displayed_fields])
            self._tbl_wdgt.setSelectionBehavior(1) # Select full row as click
            self._tbl_wdgt.setSelectionMode(1)         # and one row only
            self._tbl_wdgt.resizeColumnsToContents()
        else:
            #@TODO: create exception
            pass
        
    def fill_table(self, items):
        self.init_table()
        for item in items:
            self.add_item(item)
        self.unchanged = True
        
    def get_items(self):
        result = []
        for row in range(self._tbl_wdgt.rowCount()):
            result.append(self._tbl_wdgt.item(row, 0).text())
        return result
    
    def add_item(self, item):
        num_row = self._tbl_wdgt.rowCount()
        self._tbl_wdgt.insertRow(num_row)
        self._set_item(num_row, item)
        self.unchanged = False
            
    def upd_item(self, item):
        num_row = self._tbl_wdgt.currentRow()
        self._set_item(num_row, item)
        self.unchanged = False



class Form(QObject):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     **************************************************************************/
     """
    
#    Signals:
    
    valid_clicked = pyqtSignal(str, object, str)
    canceled = pyqtSignal()
    closed = pyqtSignal()
    
    
#    Slots:

    def _cancel(self):
        if not self.fingerprint() == self.fgpr_bfor_fill:
            self.upd_flag = True
        else:
            self.upd_flag = False
            for rel in self.relation:
                rel.unchanged = True
        self.canceled.emit()
        
#    def _cancel(self):
#        if not self.fingerprint() == self.fgpr_bfor_fill:
#            self.upd_flag = True
#        else:
#            self.upd_flag = False
#            if self.relation:
#                self.relation.unchanged = True
#        self.canceled.emit()
#        
    def _valid(self):
        obj = self.get_form_obj()
        for field, value in obj.items():
            form_name = self.ui.objectName()
            tbl_desc = [d for t,d in DB_STRUCTURE if t == form_name]
            cach_flds = [f for f,d in tbl_desc[0].get('fields') if d.get('cache')]
            if field in cach_flds:
                s = QSettings()
                s.setValue('cache_val/' + field, value)
        feat_id = str(self.feat_id) if self.feat_id else None
        self.valid_clicked.emit(self.ui.objectName(), obj, feat_id)
        
    
#    Constructor:
    
    def __init__(self, ui_file, feat_id,
                    relations_manager=[],
                    mode=Qt.AllDockWidgetAreas):
        """ Constructor. """
        QObject.__init__(self)
        ui_file = ui_file if ui_file.endswith('.ui') else ui_file + '.ui'
        self.ui = loadUi(path.join(pluginDirectory, ui_file))
        self.feat_id = feat_id
        self.mode = mode
#        self.relation = relations_manager
        self.relation = relations_manager
        self.upd_flag = False
        
        for rel in relations_manager:
            self._insert_relations_widget(rel.ui)
#        if relations_manager:
#            self._insert_relations_widget(relations_manager.ui)
        
        self._fill_cbox()
        valid_b = self.ui.findChild(QPushButton, 'valid_btn')
        cancel_b = self.ui.findChild(QPushButton, 'cancel_btn')
        valid_b.clicked.connect(self._valid)
        cancel_b.clicked.connect(self._cancel)


#    Private methods:
    
    def _cbx_itm_selected(self, cbox):
        cd = cbox.itemData(cbox.currentIndex())
        form_name = self.ui.objectName()
        nested_cbox = FORM_STRUCTURE.get(form_name).get("nested_cbox")
        if nested_cbox:
            for item in nested_cbox:
                if cbox.objectName() == item[0]:
                    parent_lnk_cd = item[1]
                    cbox_chld_name = item[2]
                    chld_lnk_cd = item[3]
                    lnk_lst = CatalogReader(item[4]).get_all_rows()
                    chld_lst = []
                    for lnk in lnk_lst:
                        if lnk.get(parent_lnk_cd) == cd:
                            chld_lst.append(lnk.get(chld_lnk_cd))
                    self._fltr_cbox(cbox_chld_name, chld_lst)
        linked_cboxes = FORM_STRUCTURE.get(form_name).get("linked")
        if linked_cboxes:
            for cb1, cb2 in linked_cboxes:
                lnk_cb_name = cb1 if cbox.objectName() == cb2\
                    else cb2 if cbox.objectName() == cb1 else None
                if lnk_cb_name:
                    lnk_cb = self.ui.findChild(QComboBox, lnk_cb_name)
                    sel_cd = cbox.itemData(cbox.currentIndex())
                    lnk_cb.setCurrentIndex(lnk_cb.findData(sel_cd))

    def _fltr_cbox(self, cbox_name, codes):
        cbox = self.ui.findChild(QComboBox, cbox_name)
        cur_text = cbox.currentText()
        cbox.clear()
        form_name = self.ui.objectName()
        cbox_lst = FORM_STRUCTURE.get(form_name).get("cbox")
        for cb_name, csv_name, lb_col, cd_col in cbox_lst:
            if cb_name == cbox_name:
                lst = CatalogReader(csv_name).get_all_rows()
                cbox_lst = [(i.get(lb_col), i.get(cd_col)) for i in lst]
                try:
                    cbox_lst = [(int(i), j) for (i,j) in cbox_lst]
                except Exception, err:
                    pass
                cbox_lst.sort()
                for (lb, cd), code in (((lb, cd),c) for (lb, cd) in cbox_lst for c in codes):
                    if cd == code:
                        cbox.addItem(unicode(lb), cd)
        if cur_text:
            cbox.setCurrentIndex(cbox.findText(cur_text))
    
    def _get_csv(self, cbox_name):
        form_name = self.ui.objectName()
        if form_name in FORM_STRUCTURE:
            cbox_lst = FORM_STRUCTURE.get(form_name).get("cbox")
            for name, csv, lb_col, cd_col in cbox_lst:
                if name == cbox_name:
                    return csv, lb_col, cd_col
   
    def _get_cbox_parent(self, cbox_name):
        form_name = self.ui.objectName()
        if form_name in FORM_STRUCTURE:
            nested_cbox = FORM_STRUCTURE.get(form_name).get("nested_cbox")
            for cb_par, fld_par, cb_child, fld_child, lnk_file in nested_cbox:
                if cb_child == cbox_name:
                    return cb_par, fld_par, fld_child, lnk_file

    def _fill_cbox(self):
        for cbox in self.ui.findChildren(QComboBox):
            csv, lb_col, cd_col = self._get_csv(cbox.objectName())
            full_lst = CatalogReader(csv).get_all_rows()
            lst = [(r.get(lb_col), r.get(cd_col)) for r in full_lst]
            related_cbox = self._get_cbox_parent(cbox.objectName())
            if related_cbox:
                cb_parent_name, fld_par, fld_child, lnk_file = related_cbox
                cb_parent = self.ui.findChild(QComboBox, cb_parent_name)
                if cb_parent is not None: # ?? doesn't work with "if cb_parent:"
                    cur_parent_data = cb_parent.itemData(cb_parent.currentIndex())
                    lnks = CatalogReader(lnk_file).get_from(fld_par, cur_parent_data)
                    codes_lst = [r.get(fld_child) for r in lnks]
                    lst = [(lb, cd) for (lb, cd) in lst if cd in codes_lst]
            
            if lst:
                try:
                    lst = [(int(i), j) for (i,j) in lst]
                except Exception, err:
                    pass
                lst.sort()
                for lb, cd in lst:
                    cbox.addItem(unicode(lb), cd)
            cbox.setCurrentIndex(-1)
            p = partial(self._cbx_itm_selected, cbox)
            cbox.currentIndexChanged.connect(p)
            cbox.activated.connect(p)

    def _insert_relations_widget(self, relations_widget):
        if self.ui.findChild(QWidget, 'relation_ctnr'):
            wdgt_content = self.ui.findChild(QWidget, 'relation_ctnr')
        else:
            wdgt_content = self.ui.findChild(QWidget, 'wdgt_content')
        wdgt_layout = wdgt_content.layout()
        wdgt_layout.addWidget(relations_widget)
        
#    Public methods:
    
    def open(self):
        if self.mode == Qt.AllDockWidgetAreas:
            self.ui.setWindowModality(2)
        self.ui.setFeatures(QDockWidget.DockWidgetFloatable)
        iface.addDockWidget(self.mode, self.ui)

    def close(self):
        iface.removeDockWidget(self.ui)
        self.closed.emit()        
        
    def get_field_value(self, widget):
        if isinstance(widget, QComboBox) and widget.currentText():
            return widget.currentText()
        elif isinstance(widget, QLineEdit) and widget.text():
            return widget.text()
        elif isinstance(widget, QTextEdit) and widget.toPlainText():
            return widget.toPlainText()
        elif isinstance(widget, QCheckBox) and widget.isChecked():
            return int(widget.isChecked())
        elif isinstance(widget, QDateEdit) and widget.date():
            return widget.date().toString('yyyy-MM-dd')
        elif isinstance(widget, QSpinBox) and widget.value():
            return widget.value()
        elif isinstance(widget, QDoubleSpinBox) and widget.value():
            return widget.value()

    def set_field_value(self, widget, value):
        if isinstance(widget, QComboBox):
            idx = widget.findText(unicode(value))
            if not idx == -1:
                widget.setCurrentIndex(idx)
            else:
                widget.setEditText(unicode(value)) if value\
                    else widget.setEditText(None)
        elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
            widget.setText(unicode(value)) if value else widget.setText(None)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(int(value)) if value \
                else widget.setChecked(False)
        elif isinstance(widget, QDateEdit):
            widget.setDate(QDate.fromString(value, 'yyyy-MM-dd')) if value\
                else widget.setDate(QDate.currentDate())
        elif isinstance(widget, QSpinBox):
            widget.setValue(value) if value\
                else widget.setValue(0)
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(value) if value\
                else widget.setValue(0.0)
        
    
    def get_db_fields(self):
        for tbl, desc in DB_STRUCTURE:
            if tbl == self.ui.objectName():
                db_fields = [f[0] for f in desc.get('fields')]
        return db_fields
    
    def get_field_name(self, field):
        f_prop = field.property('db_field_mapping')
        return f_prop if f_prop else field.objectName()
    
    def get_form_fields(self):
        db_fields = self.get_db_fields()
        form_fields = [f for f in self.ui.findChildren(QWidget)
            if not f.isHidden() and self.get_field_name(f) in db_fields]
        return form_fields
    
    def fill_form(self, obj):
        for form_field in self.get_form_fields():
            db_value = obj.get(self.get_field_name(form_field))
            s = QSettings()
            if db_value:
                value = db_value
            else:
                value = s.value('cache_val/' + self.get_field_name(form_field))
            self.set_field_value(form_field, value)
        self.fgpr_bfor_fill = self.fingerprint()
    
    def get_form_obj(self):
        obj = {}
        s = QSettings()
        obj = {self.get_field_name(f): self.get_field_value(f) for f in self.get_form_fields()}
        for dbf in self.get_db_fields():
            if dbf == 'uvc':
                cur_lyr = iface.activeLayer()
                obj['uvc'] = cur_lyr.selectedFeatures()[0]['uvc']
            elif dbf == 'sigmaf':
                obj['sigmaf'] = s.value('current_info/sigmaf')
            elif dbf == 'catalog':
                cat_path = 'current_info/' + self.ui.objectName() + '/' + 'catalog'
                if s.value(cat_path):
                    obj['catalog'] = s.value(cat_path)
        return obj
    
    def fingerprint(self):
        fingerprint = unicode(self.get_form_obj())
        for rel in self.relation:
            if not rel.unchanged:
                fingerprint += 'rel_changed'
                break
        return fingerprint
            
#    def fingerprint(self):
#        fingerprint = unicode(self.get_form_obj())
#        if self.relation and not self.relation.unchanged:
#            fingerprint += 'rel_changed'
#        return fingerprint
#            
            
@Singleton
class FormManager(QObject):
    
#    Signals:
    
    submitted = pyqtSignal(bool, str, object)
    
    
#    Slots:
    
    def _block_change(self, selected, deselected, clearAndSelect):
        close_form_required_lyr_msg()
        cur_lyr = iface.activeLayer()
        cur_lyr.selectionChanged.disconnect(self._block_change)
        cur_lyr.setSelectedFeatures([self.cur_feat.id()])
        cur_lyr.selectionChanged.connect(self._block_change)
    
    def _on_record_submitted(self, upd, table_name, obj):
        if table_name == 'sigmaf':
            self.rel_sf.upd_item(obj) if upd else self.rel_sf.add_item(obj)
        elif table_name == 'composyntaxon':
            self.rel_syn.upd_item(obj) if upd else self.rel_syn.add_item(obj)
        elif table_name == 'attributsadd':
            self.rel_sf.upd_item(obj) if upd else self.rel_sf2.add_item(obj)

    def _get_syntax(self, idx):
        if not idx == -1:
            for item in self.rel_syn.get_items():
                self.del_record('composyntaxon', item)
            self.rel_syn.init_table()
            code = self.sf_form.ui.findChild(QComboBox, 'code_sigma').itemData(idx)
            if code:
                syntax_list = CatalogReader('sigmaf').get_syntaxons_from_sf(code)
                for syntax in syntax_list:
                    uvc = iface.activeLayer().selectedFeatures()[0]['uvc']
                    syntax['uvc'] = uvc
                    cur_sf = self.sf_form.feat_id
                    if cur_sf:
                        syntax['sigmaf'] = cur_sf
                    else:
                        s = QSettings()
                        syntax['sigmaf'] = s.value('current_info/sigmaf')
                    self.submit('composyntaxon', syntax, None)
#        
#    def _get_syntax(self, idx):
#        if not idx == -1:
#            for item in self.sf_form.relation.get_items():
#                self.del_record('composyntaxon', item)
#            self.sf_form.relation.init_table()
#            code = self.sf_form.ui.findChild(QComboBox, 'code_sigma').itemData(idx)
#            if code:
#                syntax_list = CatalogReader('sigmaf').get_syntaxons_from_sf(code)
#                for syntax in syntax_list:
#                    uvc = iface.activeLayer().selectedFeatures()[0]['uvc']
#                    syntax['uvc'] = uvc
#                    cur_sf = self.sf_form.feat_id
#                    if cur_sf:
#                        syntax['sigmaf'] = cur_sf
#                    else:
#                        s = QSettings()
#                        syntax['sigmaf'] = s.value('current_info/sigmaf')
#                    self.submit('composyntaxon', syntax, None)
#    Constructor:
    
    def __init__(self):
        QObject.__init__(self)
        self.cur_feat = None
        self.uvc_form = None
        self.sf_form = None
        self.attr_form = None
        self.syntax_form = None
        self.rel_sf = None
        self.rel_sf2 = None
        self.rel_syn = None
    
#    Private methods:

    def _get_selected_feature(self):
        cur_lyr = iface.activeLayer()
        if not cur_lyr:
            return 0
        features = cur_lyr.selectedFeatures()
        feat = features[0] if len(features) == 1 else 1
        return feat

    def _check_state(self):
        if self.uvc_form and self.uvc_form.ui.isVisible():
            return False
        cur_carhab_lyr = WorkLayerRegistry.instance().current_work_layer()
        if not cur_carhab_lyr:
            no_work_lyr_msg()
            return False
        if self._get_selected_feature() == 0:
            no_vector_lyr_msg()
            return False
        if self._get_selected_feature() == 1:
            one_only_selected_feat_msg()
            return False
        return True
    
    def _exit_fill_form(self):
        cur_lyr = iface.activeLayer()
        try:
            cur_lyr.selectionChanged.disconnect(self._block_change)
        except:
            pass
        try:
            self.submitted.disconnect(self._on_record_submitted)
        except:
            pass

    def _open_form(self, tbl_name, form):
        for rel in form.relation:
            r = self.get_recorder(rel.child_table)
            child_items = r.select(tbl_name, form.feat_id)
            rel.fill_table(child_items)
        db_obj = self.get_record(tbl_name, form.feat_id)
        form.fill_form(db_obj)
        form.open()
    
#    def _open_form(self, tbl_name, form):
#        if form.relation:
#            r = self.get_recorder(form.relation.child_table)
#            child_items = r.select(tbl_name, form.feat_id)
#            form.relation.fill_table(child_items)
#        db_obj = self.get_record(tbl_name, form.feat_id)
#        form.fill_form(db_obj)
#        form.open()
#    
    
#    Public methods:
    
    def run(self):
        try:
            self.submitted.disconnect(self._on_record_submitted)
        except:
            pass
        if self._check_state():
            self.db = self.get_db()
            self.create_savepoint()
            self.submitted.connect(self._on_record_submitted)
            
            cur_lyr = iface.activeLayer()
            cur_lyr.selectionChanged.connect(self._block_change)
            self.cur_feat = self._get_selected_feature()
            uvc_id = self.cur_feat['uvc']
            disp_fields = [
                'code_serie',
                'lb_serie',
                'typ_facies',
                'pct_recouv'
            ]
            self.rel_sf = RelationsManager('sigmaf', disp_fields)
            self.rel_sf.add_clicked.connect(self.open_sf)
            self.rel_sf.edit_clicked.connect(self.open_sf)
            self.rel_sf.del_clicked.connect(self.del_record)
            
            disp_fields2 = [
                'lb_attr',
                'unite',
                'valeur'
            ]
            self.rel_sf2 = RelationsManager('attributsadd', disp_fields2)
            self.rel_sf2.add_clicked.connect(self.open_attr_add)
            self.rel_sf2.edit_clicked.connect(self.open_attr_add)
            self.rel_sf2.del_clicked.connect(self.del_record)
            
            pos = Qt.RightDockWidgetArea
            self.uvc_form = Form('form_uvc', uvc_id, [self.rel_sf, self.rel_sf2])#, pos)
#            self.uvc_form = Form('form_uvc', uvc_id, self.rel_sf)#, pos)
            
            cur_geom_typ = self.cur_feat.geometry().type()
            surface_field = self.uvc_form.ui.findChild(QWidget, 'surface')
            larg_lin_field = self.uvc_form.ui.findChild(QWidget, 'larg_lin')
            larg_lin_field.setEnabled(cur_geom_typ == 1)
            surface_field.setReadOnly(not cur_geom_typ == 0)
            
            self.uvc_form.valid_clicked.connect(self.submit_uvc)
            self.uvc_form.canceled.connect(self.cancel_uvc_fill)
            self.uvc_form.closed.connect(self._exit_fill_form)
            self._open_form('uvc', self.uvc_form)
    
    def open_sf(self, table_name, id=None):
        self.create_savepoint('sigmaf')
        s = QSettings()
        s.setValue('current_info/sigmaf', id)
        disp_fields = [
            'cd_syntax',
            'lb_syntax',
            'cd_ab_dom'
        ]
        self.rel_syn = RelationsManager('composyntaxon', disp_fields)
        self.rel_syn.add_clicked.connect(self.open_syntaxon)
        self.rel_syn.edit_clicked.connect(self.open_syntaxon)
        self.rel_syn.del_clicked.connect(self.del_record)
        
        from_cat = False
        r = self.get_recorder('sigmaf')
        if id:
            from_cat = r.select('id', id)[0].get('catalog')
        else:
            last_sf_id = r.get_last_id() if r.get_last_id() else 0
            s.setValue('current_info/sigmaf', last_sf_id + 1)
            from_cat = question('Appel aux catalogues ?,',\
                'Sélectionner un sigma facies issu des catalogues ?')
            s.setValue('current_info/sigmaf/catalog', int(from_cat))
        
        if not s.value('catalogs'):
            popup('Les référentiels ne sont pas renseignés')
            Catalog().run()
            return
        
        form_name = 'form_sigmaf_cat' if from_cat else 'form_sigmaf'
        self.sf_form = Form(form_name, id, [self.rel_syn])
        self.sf_form.canceled.connect(self.cancel_sf_fill)
        self.sf_form.valid_clicked.connect(self.submit_sf)
        self._open_form('sigmaf', self.sf_form)
        
        cd_sf_field = self.sf_form.ui.findChild(QComboBox, 'code_sigma')
        if cd_sf_field:
            cd_sf_field.currentIndexChanged.connect(self._get_syntax)
        
    def open_attr_add(self, table_name, id=None):
        self.attr_form = Form('form_attributs_add', id)
        self.attr_form.canceled.connect(self.cancel_attr_fill)
        self.attr_form.valid_clicked.connect(self.submit_attr)
        r = Recorder(self.db, table_name)
        attr_rows = r.select_all()
        for edit in self.attr_form.ui.findChildren(QLineEdit):
            completer = QCompleter()
            completer.setCaseSensitivity(0)
            edit.setCompleter(completer)
            model = QStringListModel()
            completer.setModel(model)
            model.setStringList([row.get(edit.objectName()) for row in attr_rows])
        self._open_form('attributsadd', self.attr_form)
    
    def open_syntaxon(self, table_name, id=None):
        self.syntax_form = Form('form_syntaxon', id)
        self.syntax_form.canceled.connect(self.cancel_syntaxon_fill)
        self.syntax_form.valid_clicked.connect(self.submit_syntax)
        self._open_form('composyntaxon', self.syntax_form)
    
    def submit_sf(self, table_name, form_obj, id):
        self.submit(table_name, form_obj, id)
        self.sf_form.close()
    
    def submit_attr(self, table_name, form_obj, id):
        self.submit(table_name, form_obj, id)
        self.attr_form.close()
    
    def submit_syntax(self, table_name, form_obj, id):
        self.submit(table_name, form_obj, id)
        self.syntax_form.close()
    
    def cancel_uvc_fill(self):
        if self.uvc_form.upd_flag:
            if not warning_input_lost_msg():
                return
        self.rollback()
        self.close_db()
        self.uvc_form.close()
            

    def cancel_sf_fill(self):
        self.rollback('sigmaf')
        self.sf_form.close()
        
    def cancel_syntaxon_fill(self):
        self.syntax_form.close()
            
    def cancel_attr_fill(self):
        self.attr_form.close()
            
#    Db methods :
    
    def get_db(self):
        cur_carhab_lyr = WorkLayerRegistry.instance().current_work_layer()
        db = Db(cur_carhab_lyr.db_path)
        return db
    
    def close_db(self):
        self.db.close()
    
    def create_savepoint(self, savepoint=None):
        req = 'SAVEPOINT ' + savepoint if savepoint else 'BEGIN'
        self.db.execute(req)
    
    def rollback(self, savepoint=None):
        req = 'ROLLBACK TO SAVEPOINT ' + savepoint if savepoint else 'ROLLBACK'
        self.db.execute(req)
    
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
            result_msg = r.update(id, form_obj)
            form_obj['id'] = id
        else:
            result_msg = r.input(form_obj)
            updated = False
            form_obj['id'] = r.get_last_id()
        self.submitted.emit(updated, table_name, form_obj)
        return result_msg
        
    def submit_uvc(self, table_name, form_obj, id):
        result_msg = self.submit(table_name, form_obj, id)
        if not result_msg == 1:
            popup(str(result_msg))
            return
        self.db.commit()
        iface.activeLayer().triggerRepaint()
        self.close_db()
        self.uvc_form.close()
