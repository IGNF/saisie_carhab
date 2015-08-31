# -*- coding: utf-8 -*-
import os.path

from PyQt4.QtGui import QMessageBox, QFileDialog

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
