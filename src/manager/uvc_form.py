# -*- coding: utf-8 -*-
import os.path
from utils_job import pluginDirectory, popup, setListFromCsv
from qgis.core import QGis, QgsMapLayerRegistry, QgsGeometry, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsPoint
from qgis.utils import iface
from PyQt4.QtCore import Qt, QSettings
from PyQt4.uic import loadUi
from PyQt4.QtGui import QGroupBox, QPushButton, QComboBox, QLineEdit, QTextEdit, QLabel,\
    QToolButton, QListWidget, QListWidgetItem
from semantic_model import Uvc, UvcModel, SigmaFaciesModel
from carhab_layer_registry import CarhabLayer, CarhabLayerRegistry
import csv

class UvcForm(object):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """ Constructor. """
        
        self.uvcFormUi = loadUi(os.path.join(pluginDirectory, 'form_uvc.ui'))
    
    def run(self):

        try:
            self.uvcFormUi.findChild(QToolButton, 'psh_btn_add_sf').clicked.disconnect(self.pickSigmaFacies)
            self.uvcFormUi.findChild(QToolButton, 'psh_btn_del_sf').clicked.disconnect(self.delSigmaFacies)
            
            self.uvcFormUi.findChild(QPushButton, 'psh_btn_val_uvc').clicked.disconnect(self.validForm)
        except:
            pass
        
        if self.uvcFormUi.isVisible():
            self.uvcFormUi.close()
        else:
            for id, carhabLayer in CarhabLayerRegistry.instance().layerMap.items():
                if id == iface.mapCanvas().currentLayer().customProperty("carhabLayer", ""):
                    selectedPolygon = iface.mapCanvas().currentLayer().selectedFeatures()
                    break
                else:
                    return
            
            self.uvcFormUi.findChild(QGroupBox, 'groupBox_dim_point').setVisible(False)
            self.uvcFormUi.findChild(QGroupBox, 'groupBox_dim_line').setVisible(False)
            self.uvcFormUi.findChild(QGroupBox, 'groupBox_dim_polygon').setVisible(False)
            
            if iface.mapCanvas().currentLayer().wkbType() == QGis.WKBPolygon:
                self.uvcFormUi.findChild(QGroupBox, 'groupBox_dim_polygon').setVisible(True)
            elif iface.mapCanvas().currentLayer().wkbType() == QGis.WKBLineString:
                self.uvcFormUi.findChild(QGroupBox, 'groupBox_dim_line').setVisible(True)
            elif iface.mapCanvas().currentLayer().wkbType() == QGis.WKBPoint:
                self.uvcFormUi.findChild(QGroupBox, 'groupBox_dim_point').setVisible(True)
            
            if len(selectedPolygon) == 1:
                uvcId = selectedPolygon[0].attribute('uvc')
                uvc = UvcModel().get(uvcId)
                
                if uvc.echelle:
                    self.uvcFormUi.findChild(QComboBox, 'ech_l_uvc').setEditText(str(uvc.echelle))
                
                self.uvcFormUi.findChild(QLineEdit, 'surf_uvc_3').setText(str(uvc.surface))
                
                if uvc.modeDetermination:
                    self.uvcFormUi.findChild(QComboBox, 'mode_c_uvc').setEditText(uvc.modeDetermination)
                
                if uvc.observationVegetation:
                    self.uvcFormUi.findChild(QComboBox, 'obs_c_uvc').setEditText(uvc.observationVegetation)
                
                if uvc.remarque:
                    self.uvcFormUi.findChild(QTextEdit, 'rmq_uvc').setText(uvc.remarque)
                
                if uvc.auteurCreation and uvc.organismeCreation and uvc.dateCreation:
                    text = ("Ajoutée par ".decode('utf-8') + uvc.auteurCreation
                             + " ( " + uvc.organismeCreation
                             + " ) le " + uvc.dateCreation 
                             + ". ")
                    if uvc.auteurMaj and uvc.dateMaj:
                        text += ("Dernière mise à jour par ".decode('utf-8') + uvc.auteurMaj
                                 + " le " + uvc.dateMaj
                                 + ".")
                    self.uvcFormUi.findChild(QLabel, 'label_info').setText(text)
                
                else:
                    self.uvcFormUi.findChild(QLabel, 'label_info').setVisible(False)
    
    
            # Show the carhab layer list
            iface.addDockWidget(Qt.RightDockWidgetArea, self.uvcFormUi)
            
            echelleCbBox = self.uvcFormUi.findChild(QComboBox, 'ech_l_uvc')
            echelleCbBox.setDuplicatesEnabled(False)
            echelleCbBox.clear()
            echelleCbBox.addItems(setListFromCsv("echelles.csv", "int"))
            
            modeObsCbBox = self.uvcFormUi.findChild(QComboBox, 'mode_c_uvc')
            modeObsCbBox.setDuplicatesEnabled(False)
            modeObsCbBox.clear()
            modeObsCbBox.addItems(setListFromCsv("modes_obs.csv", "string", 1))
            modeObsCbBox.setEditText("")
            modeObsCbBox.editTextChanged.connect(self.fillObsCbBox)
            
            sfm = SigmaFaciesModel()
            if sfm.getAll():
                sigmaFaciesCbBox = self.uvcFormUi.findChild(QComboBox, 'cb_box_compo_sf')
                sigmaFaciesCbBox.clear()
                sigmaFacies = []
                for sigmaF in sfm.getAll():
                    sigmaFacies.append(sigmaF.nom)
                
                sigmaFaciesCbBox.addItems(sigmaFacies)
            self.uvcFormUi.findChild(QToolButton, 'psh_btn_add_sf').clicked.connect(self.pickSigmaFacies)
            self.uvcFormUi.findChild(QToolButton, 'psh_btn_del_sf').clicked.connect(self.delSigmaFacies)
            
            self.uvcFormUi.findChild(QPushButton, 'psh_btn_val_uvc').clicked.connect(self.validForm)
    
    def fillObsCbBox(self, modeObs):
        
        obsCbBox = self.uvcFormUi.findChild(QComboBox, 'obs_c_uvc')
        obsCbBox.clear()
        with open( os.path.join( pluginDirectory, "modes_obs.csv" ), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            # Create organisms list
            people = []
            for row in reader:
                if row[1] == modeObs:
                    people.append(row[0].decode('utf-8'))
        
        obsCbBox.addItems(sorted(set(people)))
    
    def pickSigmaFacies(self):
        
        sigmaFToAdd = self.uvcFormUi.findChild(QComboBox, 'cb_box_compo_sf').currentText()
        for index in xrange(self.uvcFormUi.findChild(QListWidget, 'list_sf').count()):
            if sigmaFToAdd == self.uvcFormUi.findChild(QListWidget, 'list_sf').item(index).text():
                popup('Ce sigma facies est déjà dans la liste.')
                return
        syntaxonItem = QListWidgetItem(sigmaFToAdd)
        self.uvcFormUi.findChild(QListWidget, 'list_sf').addItem(syntaxonItem)
        
    def delSigmaFacies(self):
        
        if self.uvcFormUi.findChild(QListWidget, 'list_sf').currentItem():
            self.uvcFormUi.findChild(QListWidget, 'list_sf').takeItem(self.uvcFormUi.findChild(QListWidget, 'list_sf').currentRow())
        
    def validForm(self):
        
        selectedPolygon = iface.mapCanvas().currentLayer().selectedFeatures()
        if len(selectedPolygon) == 1:
            uvcId = selectedPolygon[0].attribute('uvc')
            
            uvc = UvcModel().get(uvcId)
            
            s = QSettings()
            
            uvc.auteurCreation = s.value("saisieCarhab/username".encode('utf-8'), "None")
            uvc.organismeCreation = s.value("saisieCarhab/userorga".encode('utf-8'), "None")
            uvc.dateMaj = s.value("saisieCarhab/date".encode('utf-8'), "None")
            uvc.echelle = self.uvcFormUi.findChild(QComboBox, 'ech_l_uvc').currentText().encode('utf-8')
            uvc.modeDetermination = self.uvcFormUi.findChild(QComboBox, 'mode_c_uvc').currentText().encode('utf-8')
            uvc.observationVegetation = self.uvcFormUi.findChild(QComboBox, 'obs_c_uvc').currentText().encode('utf-8')
            uvc.remarque = self.uvcFormUi.findChild(QTextEdit, 'rmq_uvc').toPlainText().encode('utf-8')
            
            UvcModel().update(uvc)
