# -*- coding: utf-8 -*-
import os.path
from utils_job import pluginDirectory
from qgis.core import QGis, QgsMapLayerRegistry, QgsGeometry
from qgis.utils import iface
from PyQt4.QtCore import Qt, QDate
from PyQt4.uic import loadUi
from PyQt4.QtGui import QGroupBox, QPushButton, QComboBox, QLineEdit, QTextEdit, QLabel,\
    QDateEdit
from semantic_model import Uvc, UvcModel

class UvcFormPerso(object):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """ Constructor. """
        
        self.uvcFormPersoUi = loadUi(os.path.join(pluginDirectory, 'form_perso.ui'))
    
    def run(self):
        if self.uvcFormPersoUi.isVisible():
            self.uvcFormPersoUi.close()
        else:
            print 'activate'
            selectedPolygon = iface.mapCanvas().currentLayer().selectedFeatures()
            if len(selectedPolygon) == 1:
                uvcId = selectedPolygon[0].attribute('uvc')
                uvc = UvcModel().get(uvcId)
                
            # Show the carhab layer list
            iface.addDockWidget(Qt.RightDockWidgetArea, self.uvcFormPersoUi)
            
            self.uvcFormPersoUi.findChild(QPushButton, 'psh_btn_val_perso').clicked.connect(self.validForm)


    def validForm(self):
        
        selectedPolygon = iface.mapCanvas().currentLayer().selectedFeatures()
        if len(selectedPolygon) == 1:
            uvcId = selectedPolygon[0].attribute('uvc')
            
            uvc = UvcModel().get(uvcId)
            
            
            uvc.echelle = self.uvcFormUi.findChild(QComboBox, 'ech_l_uvc').currentText().encode('utf-8')
            uvc.modeDetermination = self.uvcFormUi.findChild(QComboBox, 'mode_c_uvc').currentText().encode('utf-8')
            uvc.observationVegetation = self.uvcFormUi.findChild(QComboBox, 'obs_c_uvc').currentText().encode('utf-8')
            uvc.remarque = self.uvcFormUi.findChild(QTextEdit, 'rmq_uvc').toPlainText().encode('utf-8')

            UvcModel().update(uvc)
