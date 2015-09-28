# -*- coding: utf-8 -*-
import os.path
from utils_job import pluginDirectory, popup, setListFromCsv
from qgis.utils import iface
from PyQt4.QtCore import Qt, QSize
from PyQt4.uic import loadUi
from PyQt4.QtGui import QComboBox, QLabel, QListWidgetItem, QListWidget,\
    QPushButton, QToolButton, QTextEdit, QCheckBox, QLineEdit
import csv
from semantic_model import SigmaFaciesModel, SigmaFacies
import sqlite3
class SigmaFaciesForm(object):
    """
    /***************************************************************************
     Sigma Facies form Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """ Constructor. """
        self.sigmaFaciesFormUi = loadUi(os.path.join(pluginDirectory, 'form_sf.ui'))
        
    def run(self):
        
        if self.sigmaFaciesFormUi.isVisible():
            try:
                self.sigmaFaciesFormUi.findChild(QToolButton, 'psh_btn_add_syntax').clicked.disconnect(self.pickSyntaxon)
                self.sigmaFaciesFormUi.findChild(QToolButton, 'psh_btn_del_syntax').clicked.disconnect(self.delSyntaxon)
                self.sigmaFaciesFormUi.findChild(QPushButton, 'psh_btn_val_sf').clicked.disconnect(self.validForm)
            except:
                pass
            self.sigmaFaciesFormUi.close()
        else:
            # Change mouse cursor form.
            iface.mapCanvas().setCursor(Qt.CrossCursor)
    
            # Show the carhab layer list
            iface.addDockWidget(Qt.RightDockWidgetArea, self.sigmaFaciesFormUi)
            
            typCplxCbBox = self.sigmaFaciesFormUi.findChild(QComboBox, 'cb_box_typ_cplx')
            typCplxCbBox.setDuplicatesEnabled(False)
            typCplxCbBox.clear()
            typCplxCbBox.addItems(setListFromCsv("complexes.csv"))
            
            typSerieCbBox = self.sigmaFaciesFormUi.findChild(QComboBox, 'cb_box_typ_serie')
            typSerieCbBox.setDuplicatesEnabled(False)
            typSerieCbBox.clear()
            typSerieCbBox.addItems(setListFromCsv("series.csv"))
            
            syntaxonCbBox = self.sigmaFaciesFormUi.findChild(QComboBox, 'cb_box_compo_syntax')
            syntaxonCbBox.setDuplicatesEnabled(False)
            syntaxonCbBox.clear()
            syntaxonCbBox.addItems(setListFromCsv("syntaxons.csv"))
            
            self.sigmaFaciesFormUi.findChild(QToolButton, 'psh_btn_add_syntax').clicked.connect(self.pickSyntaxon)
            self.sigmaFaciesFormUi.findChild(QToolButton, 'psh_btn_del_syntax').clicked.connect(self.delSyntaxon)
            
            self.sigmaFaciesFormUi.findChild(QPushButton, 'psh_btn_val_sf').clicked.connect(self.validForm)

    def pickSyntaxon(self):
        
        syntaxonToAdd = self.sigmaFaciesFormUi.findChild(QComboBox, 'cb_box_compo_syntax').currentText()
        
        for index in xrange(self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').count()):
            if syntaxonToAdd == self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').itemWidget(self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').item(index)).findChild(QLabel, 'syntaxon_name_label').text():
                popup('Ce syntaxon est déjà dans la liste.')
                return
            
        syntaxonWdgt = loadUi(os.path.join(pluginDirectory,'syntaxon_item_form.ui'))
        
        
        syntaxonWdgt.findChild(QLabel, 'syntaxon_name_label').setText(syntaxonToAdd)
        syntaxonItem = QListWidgetItem()
        syntaxonItem.setSizeHint(QSize(100,70))
        self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').addItem(syntaxonItem)
        self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').setItemWidget(syntaxonItem, syntaxonWdgt)
        
    def delSyntaxon(self):
        
        if self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').currentItem():
            self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').takeItem(self.sigmaFaciesFormUi.findChild(QListWidget, 'list_syntax').currentRow())
        
        
    def validForm(self):
        try:
            sigmaF = SigmaFacies()
            
            sigmaF.nom = self.sigmaFaciesFormUi.findChild(QLineEdit, 'line_edit_nom_sf').text().encode('utf-8')
            sigmaF.typeComplexe = self.sigmaFaciesFormUi.findChild(QComboBox, 'cb_box_typ_cplx').currentText().encode('utf-8')
            sigmaF.typeSerie = self.sigmaFaciesFormUi.findChild(QComboBox, 'cb_box_typ_serie').currentText().encode('utf-8')
            sigmaF.confianceSerie = self.sigmaFaciesFormUi.findChild(QCheckBox, 'cfce_serie').isChecked()
            sigmaF.confianceComplexe = self.sigmaFaciesFormUi.findChild(QCheckBox, 'cfce_cplx').isChecked()
            sigmaF.expression = self.sigmaFaciesFormUi.findChild(QLineEdit, 'expression').text().encode('utf-8')
            sigmaF.typicite = self.sigmaFaciesFormUi.findChild(QCheckBox, 'typicite').isChecked()
            sigmaF.remarque = self.sigmaFaciesFormUi.findChild(QTextEdit, 'rmq').toPlainText().encode('utf-8')
            
            SigmaFaciesModel().insert(sigmaF)
        
        except sqlite3.IntegrityError:
            popup("Ce nom de sigma facies existe déjà. Veuillez en saisir un autre.")