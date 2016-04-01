# -*- coding: utf-8 -*-
from os import path, listdir
from utils_job import pluginDirectory
from qgis.utils import iface
from PyQt4.QtCore import Qt, QDate
from PyQt4.uic import loadUi
from PyQt4.QtGui import QGroupBox, QPushButton, QComboBox, QLineEdit,\
    QTextEdit, QWidget, QCheckBox, QDateEdit, QCompleter
from carhab_layer_manager import CarhabLayerRegistry
from db_manager import DbManager
from recorder import Recorder
from config import Config

class Form(object):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self, formUiFile):
        """ Constructor. """
        print 'init ' + formUiFile
        self.form = loadUi(path.join(pluginDirectory, formUiFile))
                                        
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
        
                          
    def set_field_value(self, widget, value):
        if isinstance(widget, QComboBox):
            if value:
                widget.setEditText(str(value))
            else:
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
        
    
        
    def run(self):
        print 'run ' + self.form.objectName()
        valid_btn = self.form.findChild(QPushButton, 'valid_btn')
        try:
            valid_btn.clicked.disconnect(self.validForm)
        except:
            pass
        
        if self.form.isVisible():
            self.form.close()
        else:
            
            cCrhbLyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
            cLyr = iface.mapCanvas().currentLayer()
            cLyrName = iface.mapCanvas().currentLayer().name()
            features = cLyr.selectedFeatures()
            db = DbManager(CarhabLayerRegistry.instance().getCurrentCarhabLayer().dbPath)
            if (len(features) > 0):
                feature = features[0]
                fid = feature.id()
                r = Recorder(db, cLyrName.split(cCrhbLyr.getName()+"_")[1])
                uvcId = r.select_value('id', fid, 'uvc')
                
            r = Recorder(db, 'uvc')
            uvcRow = r.selectById(uvcId)
            
            for formField, dbField in ((ff, dbf) for ff in self.form.findChildren(QWidget) for dbf in uvcRow.items()):
                if formField.objectName() == dbField[0]:
                    if dbField[1]:
                        self.set_field_value(formField, dbField[1])
                    else:
                        self.set_field_value(formField, None)
            
            # WITHOUT itertools @TODO : find the best way to do
            for ffield in self.form.findChildren(QComboBox):
                if (ffield.objectName() == 'echelle'):
                    ffield.completer().setCompletionMode(QCompleter.PopupCompletion)
            for formField, element in ((ff, elt) for ff in self.form.findChildren(QWidget) for elt in listdir(pluginDirectory)):
                if isinstance(formField, QGroupBox) and formField.objectName() == element[:-3]:
                    relForm = Form(element)
                    addBtn = formField.findChild(QPushButton, 'add')
                    addBtn.clicked.connect(lambda:self.opn_linked_form(relForm))
                if isinstance(formField, QPushButton) and len(formField.objectName().split('back__')) > 1 and formField.objectName().split('back__')[1] == element[:-3]:
                    relForm2 = Form(element)
                    formField.clicked.connect(lambda:self.opn_linked_form(relForm2))
            # Show the form list
            iface.addDockWidget(Qt.RightDockWidgetArea, self.form)
            valid_btn.clicked.connect(self.validForm)

    def opn_linked_form(self, form):
        self.form.close()
        form.run()

    def validForm(self):
        cCrhbLyr = CarhabLayerRegistry.instance().getCurrentCarhabLayer()
        cLyr = iface.mapCanvas().currentLayer()
        cLyrName = iface.mapCanvas().currentLayer().name()
        features = cLyr.selectedFeatures()
        if cCrhbLyr and features:
            geomTblStruct = Config.dbStructure[cLyrName.split(cCrhbLyr.getName() + "_")[1]]
            
            fkField = None
            formTblStruct = Config.dbStructure[self.form.objectName()]
            for field in formTblStruct:
                if len(field) > 2:
                    fkField = field[0] #field name
            
            refField = None
            for field in geomTblStruct:
                if len(field) > 2:
                    refField = field[0] # field name
            
            for feat in features:
                uvcId = feat[refField]
            
            obj =  {}
            for dbField in Config.dbStructure[self.form.objectName()]:
                fieldName = dbField[0]
                if not fieldName == 'id':
                    obj[fieldName] = None
                    for formField in self.form.findChildren(QWidget):
                        if formField.objectName() == fieldName:
                            obj[fieldName] = self.get_field_value(formField)
        db = DbManager(CarhabLayerRegistry.instance().getCurrentCarhabLayer().dbPath)
        r = Recorder(db, self.form.objectName())
        row = r.select(fkField, uvcId)
        print 'row'
        print row
        if fkField:
            print 'fkFIeld and NOT row'
            print fkField
            obj[fkField] = uvcId
            r.input(obj)
        else:
            print 'not fk not row, update uvc'
            r.update(uvcId, obj)
        db.commit()
        db.close()