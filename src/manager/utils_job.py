# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path
import sys

from PyQt4.QtGui import QMessageBox, QFileDialog, QToolBar, QToolButton
from qgis.utils import iface
from qgis.gui import QgsMessageBar
import csv

pluginDirectory = path.dirname(__file__)

def popup(msg):
    '''Display a popup.
    
        :param msg: The message to display.
        :type msg: str
    '''
    
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Information")
    msgBox.setText(msg)
    msgBox.exec_()
        
def execFileDialog(nameFilter='*.shp', name='Sélectionner un fichier...', mode='open'):
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

def findButtonByActionName(buttonActionName):
    '''Find button corresponding to the given action.
    
        :param buttonActionName: Text value of the action.
        :type buttonActionName: QString
        
        :return: Widget if found, None else.
        :rtype: QWidget or None
    '''
    for tbar in iface.mainWindow().findChildren(QToolBar):
        for action in tbar.actions():
            if action.text() == buttonActionName:
                for widget in action.associatedWidgets():
                    if type(widget) == QToolButton:
                        return widget
    return None

def get_csv_content(csf_file_name):
    # create dict
    items = []
    csv_path = path.join(pluginDirectory, csf_file_name)
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            items.append(tuple(row))
    return items
    
def set_list_from_csv(csvFileName, castType='string', column=0):
    csv_path = path.join(pluginDirectory, csvFileName)
    if not path.isfile(csv_path):
        return ['no csv...']
    # Create list
    items = []
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            items.append(row[column])
    
    if castType == "int":     
        return items
    else:
        return sorted(set(items))
    
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
    print value
    try:
        return value.decode('utf8') if value else None
    except UnicodeDecodeError, err:
        msg = "Problème d'encodage :\n"
        msg += "Les référentiels doivent être encodés en Unicode (UTF8)"
        popup(msg)
    