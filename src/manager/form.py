# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path

from PyQt4.QtCore import Qt, QDate, QSettings, pyqtSignal, QObject
from PyQt4.QtGui import QPushButton, QComboBox, QLineEdit, QSpinBox, QTextEdit,\
    QDoubleSpinBox, QWidget, QCheckBox, QDateEdit, QDockWidget
from PyQt4.uic import loadUi

from functools import partial

from qgis.utils import iface

from utils_job import pluginDirectory
from config import Config
from catalog_reader import CatalogReader

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
            self.relation.unchanged = True
        self.canceled.emit()
        
    def _valid(self):
        obj = self.get_form_obj()
        for f in obj.items():
            form_name = self.ui.objectName()
            form_struct = Config.FORM_STRUCTURE
            cach_flds = form_struct.get(form_name).get("cache")
            if cach_flds and form_name in form_struct and f[0] in cach_flds:
                s = QSettings()
                s.setValue('cache_val/' + f[0], f[1])
        feat_id = str(self.feat_id) if self.feat_id else None
        self.valid_clicked.emit(self.ui.objectName(), obj, feat_id)
        
    
#    Constructor:
    
    def __init__(self, ui_file, feat_id,\
                    relations_manager=None,
                    mode=Qt.AllDockWidgetAreas):
        """ Constructor. """
        QObject.__init__(self)
        ui_file = ui_file if ui_file.endswith('.ui') else ui_file + '.ui'
        self.ui = loadUi(path.join(pluginDirectory, ui_file))
        self.feat_id = feat_id
        self.mode = mode
        self.relation = relations_manager
        self.upd_flag = False
        
        if relations_manager:
            self._insert_relations_widget(relations_manager.ui)
        
        self._fill_cbox()
        valid_b = self.ui.findChild(QPushButton, 'valid_btn')
        cancel_b = self.ui.findChild(QPushButton, 'cancel_btn')
        valid_b.clicked.connect(self._valid)
        cancel_b.clicked.connect(self._cancel)


#    Private methods:
    
    def _cbx_itm_selected(self, cbox):
        cd = cbox.itemData(cbox.currentIndex())
        form_name = self.ui.objectName()
        form_struct = Config.FORM_STRUCTURE
        nested_cbox = form_struct.get(form_name).get("nested_cbox")
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
        linked_cboxes = form_struct.get(form_name).get("linked")
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
        form_struct = Config.FORM_STRUCTURE
        cbox_lst = form_struct.get(form_name).get("cbox")
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
        form_struct = Config.FORM_STRUCTURE
        if form_name in form_struct:
            cbox_lst = form_struct.get(form_name).get("cbox")
            for name, csv, lb_col, cd_col in cbox_lst:
                if name == cbox_name:
                    return csv, lb_col, cd_col
   
    def _get_cbox_parent(self, cbox_name):
        form_name = self.ui.objectName()
        form_struct = Config.FORM_STRUCTURE
        if form_name in form_struct:
            nested_cbox = form_struct.get(form_name).get("nested_cbox")
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
        for tbl, desc in Config.DB_STRUCTURE:
            if tbl == self.ui.objectName():
                db_fields = [f[0] for f in desc.get('fields')]
        return db_fields
    
    def get_field_name(self, field):
        f_prop = field.property('db_field_mapping')
        return f_prop if f_prop else field.objectName()
    
    def get_form_fields(self):
        db_fields = self.get_db_fields()
        form_fields = [f for f in self.ui.findChildren(QWidget)\
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
                cur_lyr = iface.mapCanvas().currentLayer()
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
        if self.relation and not self.relation.unchanged:
            fingerprint += 'rel_changed'
        return fingerprint
            
            
        
