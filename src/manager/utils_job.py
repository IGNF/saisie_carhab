# -*- coding: utf-8 -*-
import os.path

from PyQt4.QtGui import QMessageBox, QFileDialog, QToolBar, QToolButton
from qgis.core import QgsPoint
from qgis.utils import iface

pluginDirectory = os.path.dirname(__file__)

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
    
    dialog = QFileDialog(None, name.decode('utf-8'))
    dialog.setFilter(nameFilter)
    if mode == 'save':
        dialog.setAcceptMode(1)
        dialog.setDefaultSuffix(nameFilter.split('*.')[1])
    else:
        dialog.setFileMode(1)

    if dialog.exec_():
        fileName = dialog.selectedFiles()[0]
        return fileName
    return None

def question(*args):
    title = ''
    msg = args[0].decode('utf-8')
    if len(args) > 1:
        title = args[0].decode('utf-8')
        msg = args[1].decode('utf-8')
    reply = QMessageBox.question(None, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        return True
    else:
        return False

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
