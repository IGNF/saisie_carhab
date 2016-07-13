# -*- coding: utf-8 -*-

from os import path

from PyQt4.QtCore import Qt, QDate, QSettings, pyqtSignal, QObject
from PyQt4.QtGui import QPushButton, QComboBox, QLineEdit,\
    QTextEdit, QWidget, QCheckBox, QDateEdit, QCompleter
from PyQt4.uic import loadUi

from qgis.utils import iface

from utils_job import pluginDirectory, set_list_from_csv, get_csv_content
from config import Config

class Form(QObject):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     **************************************************************************/
     """
    
#    Signals:
    
    valid_clicked = pyqtSignal(str, object, str)
    submitted = pyqtSignal()


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
            
        valid = self.ui.findChild(QPushButton, 'valid_btn')
        valid.clicked.connect(lambda:self.valid())
            
#        self.ui.setAttribute(55, True)
#        self.ui.visibilityChanged.connect(self.close)
    

#    Private methods:

    def _insert_relations_widget(self, relations_widget):
        wdgt_content = self.ui.findChild(QWidget, 'wdgt_content')
        wdgt_layout = wdgt_content.layout()
        wdgt_layout.addWidget(relations_widget)
        wdgt_content.setLayout(wdgt_layout)
        
        
#    Public methods:
    
    def open(self):
        if self.mode == Qt.AllDockWidgetAreas:
            self.ui.setWindowModality(2)
        iface.addDockWidget(self.mode, self.ui)

    def close(self):
        iface.removeDockWidget(self.ui)
    
    def valid(self):
        obj = self.get_form_obj(self.feat_id)
        for f in obj.items():
            form_name = self.ui.objectName()
            form_struct = Config.FORM_STRUCTURE
            if form_name in form_struct and f[0] in form_struct[form_name]:
                s = QSettings()
                s.setValue('cache_val/' + f[0], f[1])
        feat_id = str(self.feat_id) if self.feat_id else None
        self.valid_clicked.emit(self.ui.objectName(), obj, feat_id)
        self.close()
    
    def get_field_value(self, widget):
        if isinstance(widget, QComboBox) and widget.currentText():
            if widget.objectName() == 'cd_syntax' or widget.objectName() == 'code_hic':
                return widget.itemData(widget.currentIndex())
            else:
                return widget.currentText()
        elif isinstance(widget, QLineEdit) and widget.text():
            return widget.text()
        elif isinstance(widget, QTextEdit) and widget.toPlainText():
            return widget.toPlainText()
        elif isinstance(widget, QCheckBox) and widget.isChecked():
            return widget.isChecked()
        elif isinstance(widget, QDateEdit) and widget.date():
            return widget.date().toString('yyyy-MM-dd')
        
    def fill_author(self, orga_val):
        aut_wdgt = self.ui.findChild(QComboBox, 'aut_crea')
        aut_wdgt.clear()
        aut_content = get_csv_content('aut_crea.csv')
        aut_list = []
        for orga, aut in aut_content:
            if orga == orga_val:
                aut_list.append(aut.decode('utf8'))
        aut_wdgt.addItems(sorted(set(aut_list)))

    def fill_obser(self, carac_val):
        obser_wdgt = self.ui.findChild(QComboBox, 'mode_obser')
        obser_wdgt.clear()
        obser_content = get_csv_content('mode_obser.csv')
        obser_list = []
        for carac, obser in obser_content:
            if carac == carac_val:
                obser_list.append(obser.decode('utf8'))
        obser_wdgt.addItems(sorted(set(obser_list)))
    
    def set_field_value(self, widget, value):
        if isinstance(widget, QComboBox):
            # Populate combo box from corresponding csv
            widget.clear()
            widget.completer().setCompletionMode(QCompleter.PopupCompletion)
            item_list = []
            if widget.objectName() == 'orga_crea':
                item_list = set_list_from_csv('aut_crea.csv')
                widget.editTextChanged.connect(self.fill_author)
            elif widget.objectName() == 'aut_crea':
                pass
            elif self.ui.objectName() == 'uvc' and widget.objectName() == 'mode_carac':
                item_list = set_list_from_csv('mode_obser.csv')
                widget.editTextChanged.connect(self.fill_obser)
            elif widget.objectName() == 'mode_obser':
                pass
            elif widget.objectName() == 'cd_syntax':
                pvf_content = get_csv_content('syntaxon.csv')
                for row in pvf_content:
                    widget.addItem(row[1].decode('utf8'), row[0])
                    if value == row[0]:
                        value = row[1].decode('utf8')
            elif widget.objectName() == 'code_hic':
                hic_content = get_csv_content('HIC.csv')
                for row in hic_content:
                    widget.addItem(row[2].decode('utf8'), row[0])
                    if value == row[0]:
                        value = row[2].decode('utf8')
            else:
                item_list = set_list_from_csv(widget.objectName() + '.csv')
            widget.addItems(item_list)
            widget.setEditText(unicode(value)) if value else widget.setEditText(None)
            
        elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
            if value:
                widget.setText(unicode(value))
            else:
                widget.setText(None)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(True)
            if not value:
                widget.setChecked(False)
        elif isinstance(widget, QDateEdit):
            if value:
                widget.setDate(QDate.fromString(value, 'yyyy-MM-dd'))
            else:
                widget.setDate(QDate.currentDate())
            
    def fill_linked_to_sf(self, sf_obj):
        print 'sf_obj :'
        print sf_obj
        cd_serie_wdgt = self.ui.findChild(QComboBox, 'code_serie')
        lb_serie_wdgt = self.ui.findChild(QComboBox, 'lb_serie')
        cd_serie_wdgt.setEditText(sf_obj['cd_serie'].decode('utf8'))
        lb_serie_wdgt.setEditText(sf_obj['lb_serie'].decode('utf8'))
        
        
                
    def fill_code_sigma(self, lb_val):
        cd_wdgt = self.ui.findChild(QComboBox, 'code_sigma')
        cd_wdgt.clear()
        cd_content = get_csv_content('sigmaf.csv')
        for cd, lb in cd_content:
            if lb == lb_val:
                full_sf = CatalogReader('sigmaf').get_obj_from_code(cd)
                self.fill_linked_to_sf(full_sf)
                cd_wdgt.setEditText(cd.decode('utf8'))
                return
            
    def fill_lb_sigma(self, cd_val):
        full_sf = CatalogReader('sigmaf').get_obj_from_code(cd_val)
        self.fill_linked_to_sf(full_sf)
        lb_wdgt = self.ui.findChild(QComboBox, 'lb_sigma')
        lb_wdgt.clear()
        lb_content = get_csv_content('sigmaf.csv')
        for cd, lb in lb_content:
            if cd == cd_val:
                lb_wdgt.setEditText(lb.decode('utf8'))
                return
                
    def fill_sf_cat(self, chk_box_state):
        print 'fill_sf_cat'
        if chk_box_state:
            cat = CatalogReader('sigmaf')
            sigmaf_list = cat.get_all_rows()
            cd_list, lb_list = [sf[0] for sf in sigmaf_list], [sf[1] for sf in sigmaf_list]
            cd_wdgt, lb_wdgt  = self.ui.findChild(QComboBox, 'code_sigma'), self.ui.findChild(QComboBox, 'lb_sigma')
            cd_wdgt.clear()
            lb_wdgt.clear()
            cd_wdgt.addItems(cd_list)
            lb_wdgt.addItems(lb_list)
            cd_wdgt.editTextChanged.connect(self.fill_lb_sigma)
            lb_wdgt.editTextChanged.connect(self.fill_code_sigma)
        else:
            print 'decochee'
        
        
    def fill(self, obj):
        print 'fill'
        form_fields = self.ui.findChildren(QWidget)
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field = self.ui.findChild(QWidget,db_field[0])
            self.set_field_value(field, None)
        for form_field in form_fields:
            if form_field.objectName() == 'sf_catalog':
                print 'match sf_catalog !!'
                form_field.stateChanged.connect(self.fill_sf_cat)
            db_value = obj.get(form_field.objectName())
            s = QSettings()
            s_value = s.value('cache_val/' + form_field.objectName())
            if s_value:
                self.set_field_value(form_field, s_value)
            if db_value:
                self.set_field_value(form_field, db_value)
            

    def get_form_obj(self, parent_id):
        obj = {}
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field_name = db_field[0]
            if not field_name == 'id':
                obj[field_name] = None
                if field_name == 'uvc':
                    obj['uvc'] = iface.mapCanvas().currentLayer().selectedFeatures()[0]['uvc']
                elif field_name == 'sigmaf':
                    obj['sigmaf'] = parent_id
                for form_field in self.ui.findChildren(QWidget):
                    if form_field.isVisible() and form_field.objectName() == field_name:
                        obj[field_name] = self.get_field_value(form_field)
        return obj