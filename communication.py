# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path

from PyQt4.QtGui import QMessageBox, QFileDialog
from PyQt4.QtCore import pyqtSignal
from qgis.utils import iface
from qgis.gui import QgsMessageBar
from qgis.core import QgsApplication
pluginDirectory = path.dirname(__file__)

class ProgressBarMsg(object):
    
    aborted = pyqtSignal()
    
    def __init__(self):
        self.pgbar = loadUi(os.path.join(pluginDirectory, "progress_bar.ui"))
        self.msgBarItm = QgsMessageBarItem('', 'Import des entités', self.pgbar)
        self.value = 0
        self.lock = False

    def add_to_iface(self):
        iface.messageBar().pushItem(self.msgBarItm)
        self.pgbar.destroyed.connect(self.remove)

    def update(self, value):
        QgsApplication.processEvents()
        if self.pgbar and not self.lock:
            self.lock = True
            self.pgbar.setValue(value)
            self.value = value
            self.lock = False
    
    def remove(self, msgBarItm):
        self.pgbar = None
        if self.value != 100: # To recognize an abortement by user of import.
            QgsApplication.processEvents()
            self.aborted.emit()

def file_dlg(nameFilter='*.shp', name='Sélectionner un fichier...', mode='open'):
    file_desc = None
    dialog = QFileDialog()
    dialog_params = (None,
        name,
        '',
        nameFilter,
        '',
        QFileDialog.DontUseNativeDialog)
    if mode == 'save':
        dialog.setDefaultSuffix(nameFilter.split('*.')[1])
        file_desc = dialog.getSaveFileNameAndFilter(*dialog_params)
    else:
        dialog.setFileMode(1)
        file_desc = dialog.getOpenFileNameAndFilter(*dialog_params)

    if file_desc[0]:
        suffix = nameFilter.split('*')[1]
        has_ext = len(file_desc[0].split(suffix)) > 1
        file_name = file_desc[0] if has_ext else file_desc[0] + suffix
        if file_name:
            return file_name
    return None

def question(*args):
    title = ''
    msg = args[0]
    if len(args) > 1:
        title = args[0]
        msg = args[1]
    reply = QMessageBox.question(None, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    return reply == QMessageBox.Yes
    
def popup(msg):
    '''Display a popup.
    
        :param msg: The message to display.
        :type msg: str
    '''
    
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Information")
    msgBox.setText(msg)
    msgBox.exec_()
        
def no_carhab_lyr_msg():
    iface.messageBar().pushMessage('Pas de couche "CarHab" active',
        'Pour effectuer cette action, importer un chantier CarHab et '\
        'sélectionner une de ses couches dans la légende',
        QgsMessageBar.INFO,
        5)
               
def no_vector_lyr_msg():
    iface.messageBar().pushMessage('Pas de couche sélectionnée',
        'Pour cette action, sélectionner une couche vectorielle dans la légende',
        QgsMessageBar.INFO,
        5)
        
def no_selected_feat_msg():
    iface.messageBar().pushMessage('Pas de sélection',
        'Pour cette action, sélectionner au moins une géométrie sur la carte',
        QgsMessageBar.INFO,
        5)
        
def one_only_selected_feat_msg():
    iface.messageBar().pushMessage('Sélection d\'une entité obligatoire',
        'Pour cette action, sélectionner une et \
        une seule géométrie sur la carte',
        QgsMessageBar.INFO,
        5)
        
def error_update_db():
    iface.messageBar().pushMessage('Echec de la mise à jour',
        'Une erreur est survenue dans la mise à jour de la couche de travail,\
         celle-ci ne s\'est pas faite',
        QgsMessageBar.CRITICAL,
        5)
        
def selection_out_of_lyr_msg():
    iface.messageBar().pushMessage('Sélection hors couche',
        'Pour sortir de la sélection, fermer le formulaire en cours',
        QgsMessageBar.INFO,
        5)
        
def close_form_required_lyr_msg():
    iface.messageBar().pushMessage('Formulaire en cours de saisie',
        'Pour changer la sélection, valider ou fermer le formulaire en cours',
        QgsMessageBar.INFO,
        5)
        
def warning_input_lost_msg():
    return question('Modifications non sauvegardées',
        "Les modifications en cours seront perdues. Continuer ?")
        
def encode(value):
    return unicode(value).encode('utf8') if value else None

def decode(value):
    try:
        return value.decode('utf8') if value else None
    except UnicodeDecodeError, err:
        msg = "Problème d'encodage :\n"
        msg += "Les référentiels doivent être encodés en Unicode (UTF8)"
        popup(msg)