# -*- coding: utf-8 -*-
from os import path, listdir
import csv
from utils_job import pluginDirectory, popup, question, set_list_from_csv,\
    get_csv_content
from qgis.utils import iface
from PyQt4.QtCore import Qt, QDate, QSettings, pyqtSignal, QObject
from PyQt4.uic import loadUi
from PyQt4.QtGui import QGroupBox, QPushButton, QComboBox, QLineEdit,\
    QTextEdit, QWidget, QCheckBox, QDateEdit, QCompleter, QDockWidget,\
    QTableWidget, QTableWidgetItem
from db_manager import DbManager
from recorder import Recorder
from config import Config
from carhab_layer_manager import Singleton, CarhabLayerRegistry
from form_uvc import Ui_uvc

class RelationShipManager(object):
    def __init__(self, form_parent, displayed_fields):
        self.form_parent = form_parent
        self.displayed_fields = displayed_fields
    
    def get_tbl_wdgt(self):
        form_child_name = None
        grp_boxes = self.form_parent.ui.findChildren(QGroupBox)
        for grp_box in grp_boxes:
            if grp_box.objectName().split('_')[0] == 'rel':
                form_child_name = grp_box.objectName()
        if form_child_name:
            tbl_wdgt = self.form_parent.ui.findChild(QGroupBox, form_child_name).findChildren(QTableWidget)[0]
            return tbl_wdgt
        return None
    
    def get_child_tbl_name(self):
        if self.get_tbl_wdgt():
            return self.get_tbl_wdgt().parent().objectName().split('rel_')[1]
        return None
    
    def fill_displayer(self, parent_id):
        tbl_wdgt = self.get_tbl_wdgt()
        if tbl_wdgt:
            tbl_wdgt.clearContents()
            tbl_wdgt.setRowCount(0)
            tbl_wdgt.setColumnCount(len(self.displayed_fields))
            tbl_wdgt.setHorizontalHeaderLabels(self.displayed_fields)
            tbl_wdgt.setSelectionBehavior(1) # Select full row as click
            tbl_wdgt.setSelectionMode(1)         # and one row only
            child_tbl_name = self.get_child_tbl_name()
            if child_tbl_name:
                cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
                db = DbManager(cur_carhab_lyr.dbPath)
                r = Recorder(db, child_tbl_name)
                child_objects = r.select(self.form_parent.ui.objectName(), parent_id)
                i = 0
                for row in child_objects:
                    tbl_wdgt.insertRow(i)
                    j = 0
                    for field in self.displayed_fields:
                        cell_item = QTableWidgetItem(unicode(row[field]))
                        tbl_wdgt.setItem(i, j, cell_item)
                        j += 1
                    i += 1
                
    def get_selected_related(self):
        tbl_wdgt = self.get_tbl_wdgt()
        if tbl_wdgt:
            return tbl_wdgt.item(tbl_wdgt.currentRow(), 0).text()
        return None
    

@Singleton
class FormManager(QObject):
    
    sfsubmitted = pyqtSignal()
    synsubmitted = pyqtSignal()
    
    def __init__(self):
        QObject.__init__(self)
        self.uvc_ui = loadUi(path.join(pluginDirectory, 'form_uvc.ui'))
        self.sf_ui = loadUi(path.join(pluginDirectory, 'form_sigmaf.ui'))
        self.syntax_ui = loadUi(path.join(pluginDirectory, 'form_syntaxon.ui'))
        
    def get_obj(self, tbl, id):
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, tbl)
        obj = {}
        for row in r.select('id', id):
            obj = row
        return obj
    
    def open_uvc(self):
        uvc_form = Form(self.uvc_ui)
        add_btn = uvc_form.ui.findChild(QPushButton, 'add')
        edt_btn = uvc_form.ui.findChild(QPushButton, 'edit')
        del_btn = uvc_form.ui.findChild(QPushButton, 'delt')
        valid_btn = uvc_form.ui.findChild(QPushButton, 'valid_btn')
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

        if add_btn:
            try:
                add_btn.clicked.disconnect()
            except:
                pass
        if edt_btn:
            try:
                edt_btn.clicked.disconnect()
            except:
                pass
        if del_btn:
            try:
                del_btn.clicked.disconnect()
            except:
                pass

        uvc_form.open()
        uvc_id = int(self.get_selected_feature()['uvc'])
        db_obj = self.get_obj('uvc', uvc_id)
        if db_obj:
            uvc_form.fill(db_obj)
    
        sf_relation = RelationShipManager(uvc_form, ['id', 'code_serie', 'pct_recouv'])
        sf_relation.fill_displayer(uvc_id)
        self.sfsubmitted.connect(lambda:sf_relation.fill_displayer(uvc_id))
        if add_btn:
            add_btn.clicked.connect(lambda:self.open_sf())
        if edt_btn:
            edt_btn.clicked.connect(lambda:self.open_sf(sf_relation.get_selected_related()))
        if del_btn:
            del_btn.clicked.connect(lambda:self.del_related_rec(sf_relation.get_selected_related(), sf_relation.get_tbl_wdgt()))
        valid_btn.clicked.connect(lambda:uvc_form.submit(None, uvc_id))
        iface.mapCanvas().currentLayer().selectionChanged.connect(self.change_feature)
        uvc_form.ui.visibilityChanged.connect(lambda:self.close_form(uvc_form))

    
    
    def open_sf(self, id=None):
        sf_form = Form(self.sf_ui, 'win')
        valid_btn = sf_form.ui.findChild(QPushButton, 'valid_btn')
        add_btn = sf_form.ui.findChild(QPushButton, 'add')
        edt_btn = sf_form.ui.findChild(QPushButton, 'edit')
        del_btn = sf_form.ui.findChild(QPushButton, 'delt')
        
        try:
            sf_form.submitted.disconnect()
        except:
            pass
        try:
            add_btn.clicked.disconnect()
        except:
            pass
        if edt_btn:
            try:
                edt_btn.clicked.disconnect()
            except:
                pass
        if del_btn:
            try:
                del_btn.clicked.disconnect()
            except:
                pass
        try:
            valid_btn.clicked.disconnect()
        except:
            pass
        try:
            sf_form.ui.visibilityChanged.disconnect()
        except:
            pass
        synt_relation = RelationShipManager(sf_form, ['id', 'cd_syntax', 'code_hic', 'abon_domin'])
        sf = self.get_obj('sigmaf', id)
        sf_form.fill(sf)
        if id:
            valid_btn.clicked.connect(lambda:sf_form.submit(self.get_selected_feature()['uvc'], id))
        else:
            cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
            db = DbManager(cur_carhab_lyr.dbPath)
            r = Recorder(db, 'sigmaf')
            if r.get_last_id()[0]:
                id = r.get_last_id()[0] + 1
            else:
                id = 1
            valid_btn.clicked.connect(lambda:sf_form.submit(self.get_selected_feature()['uvc']))
        
        synt_relation.fill_displayer(id)
        self.synsubmitted.connect(lambda:synt_relation.fill_displayer(id))
        sf_form.submitted.connect(self.sf_form_submitted)
        if add_btn:
            add_btn.clicked.connect(lambda:self.open_syntaxon(id))
        if edt_btn:
            edt_btn.clicked.connect(lambda:self.open_syntaxon(id, synt_relation.get_selected_related()))
        if del_btn:
            del_btn.clicked.connect(lambda:self.del_related_rec(synt_relation.get_selected_related(), synt_relation.get_tbl_wdgt()))
            
        sf_form.open()
        
    def sf_form_submitted(self):
        self.sfsubmitted.emit()
        
    def syn_form_submitted(self):
        self.synsubmitted.emit()
        
        
    def open_syntaxon(self, parent_id=None, id=None):
        syntax_form = Form(self.syntax_ui, 'win')
        valid_btn = syntax_form.ui.findChild(QPushButton, 'valid_btn')
        try:
            valid_btn.clicked.disconnect()
        except:
            pass
        
        syntax = self.get_obj('composyntaxon', id)
        syntax_form.fill(syntax)
        if id:
            valid_btn.clicked.connect(lambda:syntax_form.submit(parent_id, id))
        else:
            cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
            db = DbManager(cur_carhab_lyr.dbPath)
            r = Recorder(db, 'composyntaxon')
            if r.get_last_id()[0]:
                id = r.get_last_id()[0] + 1
            else:
                id = 1
            valid_btn.clicked.connect(lambda:syntax_form.submit(parent_id))
        
        syntax_form.submitted.connect(self.syn_form_submitted)
        syntax_form.open()
        
    def del_related_rec(self, id, tbl_wdgt):
        tbl_name = tbl_wdgt.parent().objectName().split('rel_')[1]
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, tbl_name)
        r.delete_row(id)
        db.commit()
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

class Form(QObject):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     **************************************************************************/
     """
    
    submitted = pyqtSignal()
    
    def __init__(self, ui, mode='dock'):
        """ Constructor. """
        QObject.__init__(self)
        self.ui = ui
        self.mode = mode
    
    def open(self):
        if self.mode == 'dock':
            iface.addDockWidget(Qt.RightDockWidgetArea, self.ui)
        elif self.mode == 'win':
            self.ui.setWindowModality(2)
            iface.addDockWidget(Qt.AllDockWidgetAreas, self.ui)
    
    def get_field_value(self, widget):
        if isinstance(widget, QComboBox) and widget.currentText():
            if widget.objectName() == 'cd_syntax':
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
                aut_list.append(aut)
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
                pvf_content = get_csv_content('PVF2.csv')
                for row in pvf_content:
                    widget.addItem(row[1], row[0])
            elif widget.objectName() == 'code_hic':
                hic_content = get_csv_content('HIC.csv')
                for row in hic_content:
                    widget.addItem(row[2], row[0])
            else:
                item_list = set_list_from_csv(widget.objectName() + '.csv')
            widget.addItems(item_list)
            if value:
                widget.setEditText(unicode(value))
            else:
                widget.setEditText(None)
        elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
            if widget.objectName() == 'calc_surf':
                sel_feat = FormManager.instance().get_selected_feature()
                if sel_feat.geometry().type() == 'Point':
                    value = 'es'
                if sel_feat.geometry().type() == 'Line':
                    value = 'lin'
                if sel_feat.geometry().type() == 'Polygon':
                    value = 'sig'
            if value:
                widget.setText(unicode(value))
            else:
                widget.setText(None)
        elif isinstance(widget, QCheckBox):
            if value:
                widget.setChecked(True)
            else:
                widget.setChecked(False)
        elif isinstance(widget, QDateEdit):
            if value:
                widget.setDate(QDate.fromString(value, 'yyyy-MM-dd'))
            else:
                widget.setDate(QDate.currentDate())

    def fill(self, obj):
        form_fields = self.ui.findChildren(QWidget)
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field = self.ui.findChild(QWidget,db_field[0])
            self.set_field_value(field, None)
        for form_field in form_fields:
            db_value = obj.get(form_field.objectName())
            if db_value:
                self.set_field_value(form_field, db_value)
                
    def get_form_obj(self, parent_id):
        obj = {}
        for db_field in Config.DB_STRUCTURE[self.ui.objectName()]:
            field_name = db_field[0]
            if not field_name == 'id':
                obj[field_name] = None
                if field_name == 'uvc':
                    obj['uvc'] = parent_id
                elif field_name == 'sigmaf':
                    obj['sigmaf'] = parent_id
                for form_field in self.ui.findChildren(QWidget):
                    if form_field.objectName() == field_name:
                        obj[field_name] = self.get_field_value(form_field)
        return obj
        
    def submit(self, parent_id=None, id=None):
        obj = self.get_form_obj(parent_id)
        cur_carhab_lyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        db = DbManager(cur_carhab_lyr.dbPath)
        r = Recorder(db, self.ui.objectName())
        if id:
            r.update(id, obj)
        else:
            r.input(obj)
        db.commit()
        db.close()
        iface.removeDockWidget(self.ui)
        self.submitted.emit()
