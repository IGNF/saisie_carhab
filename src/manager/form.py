# -*- coding: utf-8 -*-

from os import path

from PyQt4.QtCore import Qt, QDate, QSettings, pyqtSignal, QObject
from PyQt4.QtGui import QPushButton, QComboBox, QLineEdit, QSpinBox, \
    QTextEdit, QWidget, QCheckBox, QDateEdit, QCompleter, QDockWidget
from PyQt4.uic import loadUi

from functools import partial

from qgis.utils import iface

from utils_job import pluginDirectory, set_list_from_csv, get_csv_content
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
#        self.close()
        
    
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
                    lnk_cb.setCurrentIndex(cbox.currentIndex())
    
    def _fltr_cbox(self, cbox_name, codes):
        cbox = self.ui.findChild(QComboBox, cbox_name)
        cbox.clear()
        form_name = self.ui.objectName()
        form_struct = Config.FORM_STRUCTURE
        cbox_lst = form_struct.get(form_name).get("cbox")
        for cb_name, csv_name, lb_column, cd_column in cbox_lst:
            if cb_name == cbox_name:
                lst = CatalogReader(csv_name).get_all_rows()
                for item, code in ((i,c) for i in lst for c in codes):
                    cd = item.get(cd_column)
                    if cd == code:
                        lb = item.get(lb_column).decode('utf8')
                        cbox.addItem(lb, cd)
        
    def _fill_cbox(self):
        form_name = self.ui.objectName()
        form_struct = Config.FORM_STRUCTURE
        if form_name in form_struct:
            cbox_lst = form_struct.get(form_name).get("cbox")
            if cbox_lst:
                for cbox_name, csv_name, lb_column, cd_column in cbox_lst:
                    cbox = self.ui.findChild(QComboBox, cbox_name)
                    if not cbox == None:
                        lst = CatalogReader(csv_name).get_all_rows()
                        if lst:
                            for item in lst:
                                lb = item.get(lb_column).decode('utf8')
                                cd = item.get(cd_column)
                                cbox.addItem(lb, cd)
                        p = partial(self._cbx_itm_selected, cbox)
                        cbox.currentIndexChanged.connect(p)
                        cbox.activated.connect(p)

    def _insert_relations_widget(self, relations_widget):
        wdgt_content = self.ui.findChild(QWidget, 'wdgt_content')
        wdgt_layout = wdgt_content.layout()
        wdgt_layout.addWidget(relations_widget)
        wdgt_content.setLayout(wdgt_layout)
        
        
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
            return widget.isChecked()
        elif isinstance(widget, QDateEdit) and widget.date():
            return widget.date().toString('yyyy-MM-dd')
        elif isinstance(widget, QSpinBox) and widget.value():
            return widget.value()

    def set_field_value(self, widget, value):
        if isinstance(widget, QComboBox):
            widget.setEditText(unicode(value)) if value\
                else widget.setEditText(None)
        elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
            widget.setText(unicode(value)) if value else widget.setText(None)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(True) if value == 'true'\
                else widget.setChecked(False)
        elif isinstance(widget, QDateEdit):
            widget.setDate(QDate.fromString(value, 'yyyy-MM-dd')) if value\
                else widget.setDate(QDate.currentDate())
        elif isinstance(widget, QSpinBox):
            widget.setValue(value) if value\
                else widget.setValue(0)
        
    def fill_form(self, obj):
        for db_field in Config.DB_STRUCTURE.get(self.ui.objectName()):
            field = self.ui.findChild(QWidget,db_field[0])
            if field:
                self.set_field_value(field, None)
                db_value = obj.get(field.objectName())
                s = QSettings()
                s_value = s.value('cache_val/' + field.objectName())
                if s_value:
                    self.set_field_value(field, s_value)
                if db_value:
                    self.set_field_value(field, db_value)

    def get_form_obj(self):
        obj = {}
        s = QSettings()
        for db_field in Config.DB_STRUCTURE.get(self.ui.objectName()):
            fld_name = db_field[0]
            if not fld_name == 'id':
                obj[fld_name] = None
                if fld_name == 'uvc':
                    cur_lyr = iface.mapCanvas().currentLayer()
                    obj['uvc'] = cur_lyr.selectedFeatures()[0]['uvc']
                elif fld_name == 'sigmaf':
                    obj['sigmaf'] = s.value('current_info/sigmaf')
                elif fld_name == 'catalog':
                    ui_n = self.ui.objectName()
                    cat_path = 'current_info/' + ui_n + '/' + 'catalog'
                    obj['catalog'] = s.value(cat_path)
                for frm_fld in self.ui.findChildren(QWidget):
                    if frm_fld.isVisible() and frm_fld.objectName() == fld_name:
                        obj[fld_name] = self.get_field_value(frm_fld)
        return obj