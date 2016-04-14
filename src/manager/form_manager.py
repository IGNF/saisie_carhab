# -*- coding: utf-8 -*-
from os import path, listdir
import csv
from utils_job import pluginDirectory, popup, question, set_list_from_csv
from qgis.utils import iface
from PyQt4.QtCore import Qt, QDate, QSettings
from PyQt4.uic import loadUi
from PyQt4.QtGui import QGroupBox, QPushButton, QComboBox, QLineEdit,\
    QTextEdit, QWidget, QCheckBox, QDateEdit, QCompleter, QDockWidget,\
    QTableWidget, QTableWidgetItem
from carhab_layer_manager import CarhabLayerRegistry
from db_manager import DbManager
from recorder import Recorder
from config import Config
from carhab_layer_manager import Singleton
from form_uvc import Ui_uvc

@Singleton
class FormManager:
    def __init__(self):
        self.uvc_ui = loadUi(path.join(pluginDirectory, 'form_uvc.ui'))
        self.sf_ui = loadUi(path.join(pluginDirectory, 'form_sigmaf.ui'))
        self.syntax_ui = loadUi(path.join(pluginDirectory, 'form_syntaxon.ui'))
#        self.ui = loadUi(path.join(pluginDirectory, 'form_uvc.ui'))
#        sel_features = []
#        cur_lyr = iface.mapCanvas().currentLayer()
#        print cur_lyr
#        if cur_lyr:
#            sel_features = iface.mapCanvas().currentLayer().selectedFeatures()
#        if len(sel_features):
#            self.feature = sel_features[0]
    
    def get_obj(self):
        db_path = CarhabLayerRegistry.instance().getCurrentCarhabLayer().dbPath
        db = DbManager(db_path)
        r = Recorder(db, 'uvc')
        uvc_id = self.get_selected_feature()['uvc']
        return r.select('id', uvc_id)[0]
    
    def open_uvc(self):
        print 'open uvc'
        uvc_form = Form(self.uvc_ui)
        add_btn = uvc_form.ui.findChild(QPushButton, 'add')
        edt_btn = uvc_form.ui.findChild(QPushButton, 'edit')
        del_btn = uvc_form.ui.findChild(QPushButton, 'delt')
        valid_btn = uvc_form.ui.findChild(QPushButton, 'valid_btn')
        try:
            add_btn.clicked.disconnect()
        except:
            pass
        try:
            valid_btn.clicked.disconnect()
        except:
            pass
        try:
            iface.mapCanvas().currentLayer().selectionChanged.disconnect(self.change_feature)
        except:
            pass
        try:
            uvc_form.ui.visibilityChanged.disconnect()
        except:
            pass

#        if form.ui.isVisible():
#            print 'visible'
#            form.ui.close()
        uvc_form.open()
        db_obj = self.get_obj()
        if db_obj:
            uvc_form.fill(db_obj)

        if add_btn:
            add_btn.clicked.connect(lambda:self.open_sf())
        if edt_btn:
            edt_btn.clicked.connect(lambda:self.upd_sf(uvc_form))
        if del_btn:
            del_btn.clicked.connect(lambda:self.del_sf(uvc_form))
        valid_btn.clicked.connect(lambda:self.valid_form(uvc_form))
        iface.mapCanvas().currentLayer().selectionChanged.connect(self.change_feature)
        uvc_form.ui.visibilityChanged.connect(lambda:self.close_form(uvc_form))
        self.fill_tbl_wdgt(uvc_form)
        
    def fill_tbl_wdgt(self, form):
        try:
            form.ui.visibilityChanged.connect(lambda:self.fill_tbl_wdgt(form))
        except:
            pass
        tbl_wdgt = form.ui.findChild(QGroupBox, 'sigmaf').findChildren(QTableWidget)[0]
        tbl_wdgt.clearContents()
        tbl_wdgt.setRowCount(0)
        tbl_wdgt.setSelectionBehavior(1) # Select full row as click
        tbl_wdgt.setSelectionMode(1)         # and one row only
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, 'sigmaf')
        uvc_id = self.get_selected_feature()['uvc']
        sf_tab = r.select('uvc', uvc_id)
        i = 0
        for row in sf_tab:
            tbl_wdgt.insertRow(i)
            it_name = QTableWidgetItem(row['code_serie'])
            it_pct = QTableWidgetItem(str(row['pct_recouv']))
            tbl_wdgt.setItem(i, 0, it_name)
            tbl_wdgt.setItem(i, 1, it_pct)
            i += 1

    def valid_form(self, form):
        form.ui.visibilityChanged.connect(lambda:self.fill_tbl_wdgt(form))
        form.valid()
    
    def valid_input_form(self, form):
        form.ui.visibilityChanged.connect(lambda:self.fill_tbl_wdgt(form))
        form.valid_input()
    
    def valid_upd_form(self, form, sf):
        form.valid_upd(sf)
    
    def open_sf(self, mode='input', sf=None):
        sf_form = Form(self.sf_ui, 'win')
        valid_btn = sf_form.ui.findChild(QPushButton, 'valid_btn')
        add_btn = sf_form.ui.findChild(QPushButton, 'add')
        edt_btn = uvc_form.ui.findChild(QPushButton, 'edit')
        del_btn = uvc_form.ui.findChild(QPushButton, 'delt')
        
        try:
            add_btn.clicked.disconnect()
        except:
            pass
        try:
            valid_btn.clicked.disconnect()
        except:
            pass
        
        if add_btn:
            add_btn.clicked.connect(lambda:self.open_syntaxon(sf))
        if edt_btn:
            edt_btn.clicked.connect(lambda:self.upd_synt(sf_form))
        if del_btn:
            del_btn.clicked.connect(lambda:self.del_syn(sf_form))
        if mode == 'input':
            valid_btn.clicked.connect(lambda:self.valid_input_form(sf_form))
        if mode == 'update':
            sf_form.fill(sf)
            valid_btn.clicked.connect(lambda:self.valid_upd_form(sf_form, sf))
        sf_form.open()
    
    def upd_sf(self, form):
        tbl_wdgt = form.ui.findChild(QGroupBox, 'sigmaf').findChildren(QTableWidget)[0]
        name_sf = tbl_wdgt.item(tbl_wdgt.currentRow(), 0).text()
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, 'sigmaf')
        res_tab = r.select('code_serie', name_sf)
        for sf_to_upd in res_tab:
            self.open_sf('update', sf_to_upd)
            return
    
    def del_sf(self, form):
        print 'delete'
        tbl_wdgt = form.ui.findChild(QGroupBox, 'sigmaf').findChildren(QTableWidget)[0]
        name_sf = tbl_wdgt.item(tbl_wdgt.currentRow(), 0).text()
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, 'sigmaf')
        res_tab = r.select('code_serie', name_sf)
        for sf_to_del in res_tab:
            r.delete_row(sf_to_del['id'])
        tbl_wdgt.removeRow(tbl_wdgt.currentRow())
    
    def open_syntaxon(self, parent, mode='input', syntax=None):
        syntax_form = Form(self.syntax_ui, 'win')
        valid_btn = syntax_form.ui.findChild(QPushButton, 'valid_btn')
        try:
            valid_btn.clicked.disconnect()
        except:
            pass
        
        if mode == 'input':
            valid_btn.clicked.connect(lambda:self.valid_input_form(syntax_form, parent_id))
        if mode == 'update':
            syntax_form.fill(syntax)
            valid_btn.clicked.connect(lambda:self.valid_upd_form(syntax_form, syntax))
        
        syntax_form.open()
    
    def upd_sf(self, form):
        tbl_wdgt = form.ui.findChild(QGroupBox, 'sigmaf').findChildren(QTableWidget)[0]
        name_sf = tbl_wdgt.item(tbl_wdgt.currentRow(), 0).text()
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, 'sigmaf')
        res_tab = r.select('code_serie', name_sf)
        for sf_to_upd in res_tab:
            self.open_sf('update', sf_to_upd)
            return
    
    def del_sf(self, form):
        print 'delete'
        tbl_wdgt = form.ui.findChild(QGroupBox, 'sigmaf').findChildren(QTableWidget)[0]
        name_sf = tbl_wdgt.item(tbl_wdgt.currentRow(), 0).text()
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, 'sigmaf')
        res_tab = r.select('code_serie', name_sf)
        for sf_to_del in res_tab:
            r.delete_row(sf_to_del['id'])
        tbl_wdgt.removeRow(tbl_wdgt.currentRow())
            
    def get_selected_feature(self):
        cur_lyr = iface.mapCanvas().currentLayer()
        features = cur_lyr.selectedFeatures()
        if features:
            for feat in features:
                return feat
        return None
    
    def close_form(self, form):
        if not form.ui.isVisible():
            iface.mapCanvas().currentLayer().selectionChanged.disconnect(self.change_feature)
            form.ui.visibilityChanged.disconnect()

    def change_feature(self, selected, deselected, clearAndSelect):
        q = question('Changement d\'UVC !', \
            'La saisie sur l\'UVC en cours va être perdue. Continuer ?')
        if q:
            self.open_uvc()
        else:
            iface.mapCanvas().currentLayer().selectionChanged.disconnect(self.change_feature)
            iface.mapCanvas().currentLayer().setSelectedFeatures(deselected)
            iface.mapCanvas().currentLayer().selectionChanged.connect(self.change_feature)

class Form(object):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self, ui, mode='dock'):
        """ Constructor. """
        
        print 'init ' + ui.objectName()
        self.ui = ui
        self.mode = mode
    
    def open(self):
        if self.mode == 'dock':
            iface.addDockWidget(Qt.RightDockWidgetArea, self.ui)
        elif self.mode == 'win':
            self.ui.setWindowModality(2)
            iface.addDockWidget(Qt.AllDockWidgetAreas, self.ui)
            
    
    def close(self):
        self.ui.close()
    
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
            return widget.date().toString('yyyyMMdd')

    def fill(self, obj):
        print obj
        form_fields = self.ui.findChildren(QWidget)
#        print [f.objectName() for f in form_fields]
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field = self.ui.findChild(QWidget,db_field[0])
#            print field_name
            self.set_field_value(field, None)
        for form_field in form_fields:
            db_value = obj.get(form_field.objectName())
            if db_value:
                print db_value
                self.set_field_value(form_field, db_value)

    def set_field_value(self, widget, value):
        if isinstance(widget, QComboBox):
            # Populate combo box from corresponding csv
            widget.clear()
            widget.addItems(set_list_from_csv(widget.objectName() + '.csv'))
            widget.completer().setCompletionMode(QCompleter.PopupCompletion)
            if value:
                widget.setEditText(str(value))
            else:
                print widget.objectName()
                widget.setEditText(None)
        elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
            if value:
                widget.setText(str(value))
            else:
                widget.setText(None)
        elif isinstance(widget, QCheckBox):
            if value:
                widget.setChecked(True)
            else:
                widget.setChecked(False)
        elif isinstance(widget, QDateEdit):
            if value:
                widget.setDate(QDate.fromString(value, 'yyyyMMdd'))
            else:
                widget.setDate(QDate.currentDate())

    def valid(self):
        print 'valid : ' + str(self.ui.objectName())
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        uvc_id = iface.mapCanvas().currentLayer().selectedFeatures()[0]['uvc']
        obj = {}
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field_name = db_field[0]
            if not field_name == 'id':
                obj[field_name] = None
                for form_field in self.ui.findChildren(QWidget):
                    if form_field.objectName() == field_name:
                        obj[field_name] = self.get_field_value(form_field)
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, self.ui.objectName())
        r.update(uvc_id, obj)
        db.commit()
        db.close()
        iface.removeDockWidget(self.ui)
        
    def valid_upd(self, sf):
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        uvc_id = iface.mapCanvas().currentLayer().selectedFeatures()[0]['uvc']
        obj = {}
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field_name = db_field[0]
            if not field_name == 'id':
                obj[field_name] = None
                if field_name == 'uvc':
                    obj['uvc'] = uvc_id
                for form_field in self.ui.findChildren(QWidget):
                    if form_field.objectName() == field_name:
                        obj[field_name] = self.get_field_value(form_field)
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, self.ui.objectName())
        r.update(sf['id'], obj)
        db.commit()
        db.close()
        iface.removeDockWidget(self.ui)
        
    def valid_input(self, parent_id=None):
        print 'valid : ' + str(self.ui.objectName())
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        uvc_id = iface.mapCanvas().currentLayer().selectedFeatures()[0]['uvc']
        
        obj = {}
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field_name = db_field[0]
            if not field_name == 'id':
                obj[field_name] = None
                if field_name == 'uvc':
                    obj['uvc'] = uvc_id
                for form_field in self.ui.findChildren(QWidget):
                    if form_field.objectName() == field_name:
                        obj[field_name] = self.get_field_value(form_field)
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, self.ui.objectName())
        r.input(obj)
        db.commit()
        db.close()
        iface.removeDockWidget(self.ui)
        