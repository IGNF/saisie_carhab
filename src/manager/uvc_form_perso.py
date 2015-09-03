# -*- coding: utf-8 -*-
import os.path
from utils_job import pluginDirectory, findButtonByActionName, popup
from qgis.core import QGis, QgsMapLayerRegistry, QgsGeometry
from qgis.utils import iface
from PyQt4.QtCore import Qt, QDate, QSettings
from PyQt4.uic import loadUi
from PyQt4.QtGui import QGroupBox, QPushButton, QComboBox, QLineEdit, QTextEdit, QLabel,\
    QDateEdit
import csv
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
        
        s = QSettings()
        
        s.remove("saisieCarhab/username")
        s.remove("saisieCarhab/userorga")
        s.remove("saisieCarhab/date")
    
    def run(self):
        
        if self.uvcFormPersoUi.isVisible():
            self.uvcFormPersoUi.close()
        else:
            organismCbBox = self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_orga')
            organismCbBox.setDuplicatesEnabled(False)
            organismCbBox.clear()
            # Show the user form
            iface.addDockWidget(Qt.LeftDockWidgetArea, self.uvcFormPersoUi)
            
            with open( os.path.join( pluginDirectory, "personnes.csv" ), 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                # Create organisms list
                organisms = []
                for row in reader:
                    organisms.append(row[1].decode('utf8'))
            
            organismCbBox.addItems(sorted(set(organisms)))
            organismCbBox.editTextChanged.connect(self.fillPeopleCbBox)
            
            s = QSettings()
            
            self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_orga').setEditText(s.value("saisieCarhab/userorga", ""))
            self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_personne').setEditText(s.value("saisieCarhab/username", ""))
            self.uvcFormPersoUi.findChild(QDateEdit, 'cb_box_date').setDate(s.value("saisieCarhab/date", QDate.currentDate()))
            try:
                self.uvcFormPersoUi.findChild(QPushButton, 'psh_btn_val_perso').clicked.disconnect(self.validForm)
            except:
                pass
            self.uvcFormPersoUi.findChild(QPushButton, 'psh_btn_val_perso').clicked.connect(self.validForm)

    def fillPeopleCbBox(self, organism):
        
        print 'fill people'
        peopleCbBox = self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_personne')
        peopleCbBox.clear()
        with open( os.path.join( pluginDirectory, "personnes.csv" ), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            # Create organisms list
            people = []
            for row in reader:
                if row[1] == organism:
                    people.append(row[0].decode('utf8'))
        
        peopleCbBox.addItems(sorted(set(people)))
    
    def validForm(self):
        ''' Add user form values into settings registry.
        '''
        if self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_personne').currentText() == "" or self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_orga').currentText() == "":
            popup("Des champs n\'ont pas été saisis !")
            return
        s = QSettings()
        
        s.setValue("saisieCarhab/username", self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_personne').currentText())
        s.setValue("saisieCarhab/userorga", self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_orga').currentText())
        s.setValue("saisieCarhab/date", self.uvcFormPersoUi.findChild(QDateEdit, 'cb_box_date').date())
        
        peopleCbBox = self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_personne')
        organismsCbBox = self.uvcFormPersoUi.findChild(QComboBox, 'cb_box_orga')
        
        rowExists = False
        peopleList = []
        with open( os.path.join( pluginDirectory, "personnes.csv" ), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if peopleCbBox.currentText() == row[0]:
                    rowExists = True
                    break
                #peopleList.append(row[0]+','+row[1])
        if not rowExists:
            peopleList.append([peopleCbBox.currentText()+','+organismsCbBox.currentText()])
            with open(os.path.join( pluginDirectory, "personnes.csv"), 'ab') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([peopleCbBox.currentText().encode('utf-8'),organismsCbBox.currentText().encode('utf-8')])
        
        self.uvcFormPersoUi.close()
        findButtonByActionName('Déconnexion.').setEnabled(True)
        
    def disconnect(self):
        ''' Delete user infos from qgis settings.
        '''
        
        s = QSettings()
        
        s.remove("saisieCarhab/username")
        s.remove("saisieCarhab/userorga")
        s.remove("saisieCarhab/date")
        
        popup('Session carhab terminée.')
        
        findButtonByActionName('Déconnexion.').setEnabled(False)
        if self.uvcFormPersoUi.isVisible():
            self.uvcFormPersoUi.close()
