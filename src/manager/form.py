# -*- coding: utf-8 -*-

from os import path

from PyQt4.QtCore import Qt, QDate, QSettings, pyqtSignal, QObject
from PyQt4.QtGui import QPushButton, QComboBox, QLineEdit,\
    QTextEdit, QWidget, QCheckBox, QDateEdit, QCompleter, QDockWidget
from PyQt4.uic import loadUi

from functools import partial

from qgis.utils import iface

from utils_job import pluginDirectory, set_list_from_csv, get_csv_content
from config import Config
from catalog_reader import CatalogReader

#class NestedCbox(object):
#    def __init__(self, wdgt_name, cbox_parent, cbox_child, lst_parent, lst_child, lst_links):
#        self.wdgt_name = 
#        self.cbox_parent = cbox_parent
#        self.cbox_chils = cbox_child
#        self.lst_parent


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
        self.close()


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
        
    def _upd_cbox_child(self,cbox_parent,cbox_child,lst_child,links):
        cbox_child.clear()
        nested_id = cbox_parent.itemData(cbox_parent.currentIndex())
        childs_lnk = CatalogReader(links).get_from('code_parent', nested_id)
        childs = [ch.get('code_child') for ch in childs_lnk]
        for id_child in childs:
            for cd, lb in lst_child:
                if cd == id_child:
                    cbox_child.addItem(lb.decode('utf-8'), cd)
        
    def _link_to_cbox(self, cbox1, cbox2):
        if not cbox2.currentIndex() == cbox1.currentIndex():
            cbox2.setCurrentIndex(cbox1.currentIndex())
        
    def _fill_cbox(self):
        form_name = self.ui.objectName()
        form_struct = Config.FORM_STRUCTURE
        if form_name in form_struct:
            cbox_to_fill = form_struct.get(form_name).get("cbox")
            if cbox_to_fill:
                for cbox_name, csv_name, csv_column in cbox_to_fill:
                    cbox = self.ui.findChild(QComboBox, cbox_name)
                    if not cbox == None:
                        lst = CatalogReader(csv_name).get_all_rows()
                        for item in lst:
                            lb = item.get(csv_column if csv_column else 'label')
                            cbox.addItem(str(lb).decode('utf-8'), item.get("code"))
                    
            nested_cbox = form_struct.get(form_name).get("nested_cbox")
            if nested_cbox:
                for cbox_child_name, cbox_parent_name, links in nested_cbox:
                    cbox_child = self.ui.findChild(QComboBox, cbox_child_name)
                    cbox_parent = self.ui.findChild(QComboBox, cbox_parent_name)
                    if cbox_child and cbox_parent:
                        cboxes = form_struct.get(form_name).get("cbox")
                        for cbox_name, csv_name, csv_column in cboxes:
                            if cbox_name == cbox_child_name:
                                lst_child = CatalogReader(csv_name).get_column_as_list(csv_column)
                        p = partial(self._upd_cbox_child,\
                            cbox_parent, cbox_child, lst_child, links)
                        cbox_parent.activated.connect(p)
                        cbox_parent.currentIndexChanged.connect(p)
            
            linked_cboxes = form_struct.get(form_name).get("linked")
            if linked_cboxes:
                for cbox1_name, cbox2_name in linked_cboxes:
                    cbox1 = self.ui.findChild(QComboBox, cbox1_name)
                    cbox2 = self.ui.findChild(QComboBox, cbox2_name)
                    if cbox1 and cbox2:
                        p1 = partial(self._link_to_cbox, cbox1, cbox2)
                        p2 = partial(self._link_to_cbox, cbox2, cbox1)
                        cbox1.currentIndexChanged.connect(p1)
                        cbox2.currentIndexChanged.connect(p2)
            

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

    def set_field_value(self, widget, value):
        if isinstance(widget, QComboBox):
            widget.setEditText(unicode(value)) if value else widget.setEditText(None)
        elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
            widget.setText(unicode(value)) if value else widget.setText(None)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(True) if value == 'true' else widget.setChecked(False)
        elif isinstance(widget, QDateEdit):
            widget.setDate(QDate.fromString(value, 'yyyy-MM-dd')) if value else widget.setDate(QDate.currentDate())
        
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
            field_name = db_field[0]
            if not field_name == 'id':
                obj[field_name] = None
                if field_name == 'uvc':
                    obj['uvc'] = iface.mapCanvas().currentLayer().selectedFeatures()[0]['uvc']
                elif field_name == 'sigmaf':
                    obj['sigmaf'] = s.value('current_info/sigmaf')
                elif field_name == 'catalog':
                    obj['catalog'] = s.value('current_info/' + self.ui.objectName() + '/' + 'catalog')
                for form_field in self.ui.findChildren(QWidget):
                    if form_field.isVisible() and form_field.objectName() == field_name:
                        obj[field_name] = self.get_field_value(form_field)
        return obj