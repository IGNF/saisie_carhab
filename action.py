# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from qgis.gui import QgsMapTool
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
from qgis.utils import iface

from PyQt4.QtGui import *


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

class CustomAction(QAction):
    """
    /***************************************************************************
     CustomAction Class
            
            Class that inherits from QAction and contains common stuff to
            button actions developed for the plugin.
     ***************************************************************************/
    """
    def __init__(self,
        iconPath,
        text,
        enabledFlag=True,
        addToMenu=True,
        addToToolbar=True,
        statusTip=None,
        whatsThis=None,
        parent=None,
        editModeOnly=True,
        featureSelectedOnly=False,
        mapTool=None,
        callback=None,
        checkable=True):
        '''
        Constructor :

        :param iconPath: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param enabledFlag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param addToMenu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type addToMenu: bool

        :param addToToolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type addToToolbar: bool

        :param statusTip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type statusTip: str

        :param whatsThis: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :type whatsThis: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param editModeOnly: Flag indicating whether the action should be
            enabled only if edit mode is activated. Defaults to True.
        :type editModeOnly: bool

        :param mapTool: Optional instance of QgsMapTool that will be binded
            with the action and then called when the action is triggered.
        :type mapTool: QgsMapTool

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param checkable: Flag indicating whether the action should be checkable.
            Defaults to True
        :type checkable: bool
        '''
        # Declare inheritance to QAction class.
        super(QAction, self).__init__(QIcon(iconPath), text, parent)
        
        self.addToMenu = addToMenu
        self.addToToolbar = addToToolbar
        self.editModeOnly = editModeOnly
        self.featureSelectedOnly= featureSelectedOnly
        self.mapTool = mapTool
        self.callback = callback
        
        self.setEnabled(enabledFlag)
        self.setCheckable(checkable)
        
        if statusTip:
            self.setStatusTip(statusTip)

        if whatsThis:
            self.setWhatsThis(whatsThis)
        
        if self.mapTool and not isinstance(self.mapTool, QgsMapTool):
            raise ValueError('mapTool must be QgsMapTool instance')
        
        # To retrieve previous state of QGIS toolbar when the action is deactivated.
        self.previousActivatedMapTool = None
        
        self.triggered.connect(self.activateAction)
        
        if editModeOnly:
            # Enable/disable action when editing mode is activated/deactivated
            iface.actionToggleEditing().triggered.connect(self.enableActionAtEditModeChange)
            # Check if new current layer is in editing mode
            iface.mapCanvas().currentLayerChanged.connect(self.enableActionAtCurrentLayerChange)
        
        if featureSelectedOnly:
            # Enable action when a feature is selected only.
            
            QgsMapLayerRegistry.instance().layersAdded.connect(self.setFeatureSelectedBehaviourToLayers)
            # Check if new current layer is in editing mode
            iface.mapCanvas().currentLayerChanged.connect(self.enableActionAtCurrentLayerChange)
    
    '''Getters'''
    def getMapTool(self):
        return self.mapTool
    
    def getCallback(self):
        return self.callback
    
    def isToAddToMenu(self):
        return self.addToMenu

    def isToAddToToolbar(self):
        return self.addToToolbar

    def isMapTool(self):
        return self.mapTool


    def enableAction(self, toEnable):
        '''Enable/disable action.
        
            :param toEnable: True / False to enable / disable the action.
            :type toEnable: bool
        
        '''
        
        self.setEnabled(toEnable)
        
        canvas = iface.mapCanvas()
        if toEnable:
            self.previousActivatedMapTool = canvas.mapTool()
        else:
            canvas.unsetMapTool(self.getMapTool())
            if self.previousActivatedMapTool:
                canvas.setMapTool(self.previousActivatedMapTool)
        
    def enableActionAtEditModeChange(self, editMode):
        '''Enable / disable action at edit mode activation / deactivation.
        '''
        
        curLyr = iface.activeLayer()
        if curLyr and type(curLyr) == QgsVectorLayer and (not self.featureSelectedOnly or len(curLyr.selectedFeatures()) > 0):
            self.enableAction(editMode)
        else:
            self.enableAction(False)
    
    def enableActionAtSelectionChange(self, newFeatId, oldFeatId, clearAndSelect):
        '''Enable action at feature selection.
        '''
        curLyr = iface.activeLayer()
        if  not self.editModeOnly or (curLyr and curLyr.isEditable()):
            toEnable = True if newFeatId else False
            self.enableAction(toEnable)
        else:
            self.enableAction(False)
    
    def setFeatureSelectedBehaviourToLayers(self, layers):
        
        for layer in layers:
            if type(layer) == QgsVectorLayer:
                layer.selectionChanged.connect(self.enableActionAtSelectionChange)
        
    def enableActionAtCurrentLayerChange(self):
        '''Check if new current layer is in editing mode and apply corresponding 
            action behavior.
        '''
        
        if iface.activeLayer():
            if self.editModeOnly:
                self.enableActionAtEditModeChange(iface.activeLayer().isEditable())
            if self.featureSelectedOnly:
                curLyr = iface.activeLayer()
                toEnable = True if (type(curLyr) == QgsVectorLayer and len(curLyr.selectedFeatures()) > 0) else False
                self.enableActionAtSelectionChange(toEnable, None, None)
                
        else:
            self.enableAction(False)
            
    def activateAction(self):
        '''Activate action : bind to map tool if given, call of callback if given.'''
        if self.getMapTool():
            iface.mapCanvas().setMapTool(self.getMapTool())
        if self.getCallback():
            self.getCallback()()