# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path

from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QPushButton, QTableWidget, QTableWidgetItem
from PyQt4.uic import loadUi

from utils_job import pluginDirectory, popup, get_csv_content

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

#    Constructor:
    
    def __init__(self, child_table, displayed_fields):
        QObject.__init__(self)
        self.child_table = child_table
        self.displayed_fields = displayed_fields if 'id' in displayed_fields\
            else ['id'] + displayed_fields
        
        self.ui = loadUi(path.join(pluginDirectory, 'relations_widget.ui'))
        self._tbl_wdgt = self.ui.findChild(QTableWidget, 'rel_tbl')
        
        btns = ['add', 'edit', 'delt']
        add, edit, delt = [self.ui.findChild(QPushButton, b) for b in btns]
        add.clicked.connect(self.add_related)
        edit.clicked.connect(self.edit_related)
        delt.clicked.connect(self.del_related)
        
        self.ui.setTitle(child_table)
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
            value = unicode(item.get(field)) if item.get(field) else None
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
            self._tbl_wdgt.setHorizontalHeaderLabels(self.displayed_fields)
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

    def get_items(self):
        result = []
        for row in range(self._tbl_wdgt.rowCount()):
            result.append(self._tbl_wdgt.item(row, 0).text())
        return result
    
    def add_item(self, item):
        num_row = self._tbl_wdgt.rowCount()
        self._tbl_wdgt.insertRow(num_row)
        self._set_item(num_row, item)
            
    def upd_item(self, item):
        num_row = self._tbl_wdgt.currentRow()
        self._set_item(num_row, item)