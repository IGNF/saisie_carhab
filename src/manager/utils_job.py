# -*- coding: utf-8 -*-
from os import path

from PyQt4.QtGui import QMessageBox, QFileDialog, QToolBar, QToolButton
from qgis.utils import iface
import csv

pluginDirectory = path.dirname(__file__)

def popup(msg):
    '''Display a popup.
    
        :param msg: The message to display.
        :type msg: str
    '''
    
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Information")
    msgBox.setText(msg.decode('utf-8'))
    msgBox.exec_()
        
def execFileDialog(nameFilter='*.shp', name='Sélectionner un fichier...', mode='open'):
    file_desc = None
    dialog = QFileDialog()
    dialog_params = (None,
        name.decode('utf-8'),
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
    msg = args[0].decode('utf-8')
    if len(args) > 1:
        title = args[0].decode('utf-8')
        msg = args[1].decode('utf-8')
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
            if action.text() == buttonActionName.decode('utf-8'):
                for widget in action.associatedWidgets():
                    if type(widget) == QToolButton:
                        return widget
    return None

def get_csv_content(csf_file_name):
    # create dict
    items = []
    csv_path = path.join(pluginDirectory, csf_file_name)
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            items.append((row[0], row[1]))
    return items
    
def set_list_from_csv(csvFileName, castType='string', column=0):
    csv_path = path.join(pluginDirectory, csvFileName)
    if not path.isfile(csv_path):
        return ['no csv...'.decode('utf-8')]
    # Create list
    items = []
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            items.append(row[column].decode('utf-8'))
    
    if castType == "int":     
        return items
    else:
        return sorted(set(items))