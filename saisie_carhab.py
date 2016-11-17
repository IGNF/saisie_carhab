# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaisieCarhab Class
        
        A QGIS plugin Data acquisition tools from vector segmentation layers

        begin : 2015-05-05
        
        author : IGN
        
        contact : carhab@ign.fr
 ***************************************************************************/
 
"""

# Initialize Qt resources from file resources.py

from __future__ import unicode_literals

from resources_rc import *

from PyQt4.QtGui import QToolBar, QMenu, QToolButton
from PyQt4.QtCore import QSettings
from qgis.core import QgsProject
from action import CustomAction

from job_manager import create_job, open_job
from work_layer import run_import, WorkLayerRegistry, run_export, run_import_std
from form_manager import FormManager
from catalogs import Catalog
from map_tools import StView, Gabarit
from legend_actions import CheckCompletion
from export_format import  ExportStd
from feature_actions import Duplicate, Eraser

class SaisieCarhab:

    def __init__(self, iface):
        '''
        Constructor.
        
        :param iface: An interface instance that will be passed to this class
        which provides the hook by which you can manipulate the QGIS
        application at run time.
        :type iface: QgsInterface
        '''
        # Save reference to the QGIS interface
        self.iface = iface
        # Declare instance attributes
        self.actions = []
        self.menus = []
        self.menu = 'Saisie Carhab'
        self.toolbar = self.iface.addToolBar('SaisieCarhab')
        self.toolbar.setObjectName('SaisieCarhab')
        self.resourcesPath = ':/plugins/SaisieCarhab/resources/img/'

    def initGui(self):
        '''Instanciate CustomActions to add to plugin toolbar.'''
        
        
        # New job action instance.
        newJobIconPath = self.resourcesPath + 'nouveau_chantier.png'
        newJobAction = CustomAction(
            iconPath=newJobIconPath,
            text='Créer une nouvelle couche de travail',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=create_job,
            editModeOnly=False,
            checkable=False
        )
        
        # Open job action instance.
        openJobIconPath = self.resourcesPath + 'ouvrir_chantier.png'
        openJobAction = CustomAction(
            iconPath=openJobIconPath,
            text='Ouvrir une couche de travail existante',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=open_job,
            editModeOnly=False,
            checkable=False
        )
        
        # Open catalog manager.
        catalogManager = Catalog()
        openCatalogManager = self.resourcesPath + 'catalog_manager.png'
        openCatalogAction = CustomAction(
            iconPath=openCatalogManager,
            text='Séléctionner la localisation des catalogues',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=catalogManager.run,
            editModeOnly=False,
            checkable=False
        )
        
        # Import layer action instance.
        importLayerIconPath = self.resourcesPath + 'import_features.png'
        importLayerAction = CustomAction(
            iconPath=importLayerIconPath,
            text='Importer les géométries d\'un shapefile dans la couche de travail active',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=run_import,
            editModeOnly=False,
            checkable=False
        )
        
        # Open UVC form action instance.
        openUvcForm = FormManager.instance()
        openUvcFormIconPath = self.resourcesPath + 'form_uvc.png'
        openUvcFormAction = CustomAction(
            iconPath=openUvcFormIconPath,
            text='Saisie d\'UVC',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=openUvcForm.run,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=False
        )
        
        # UVC duplication action.
        duplicate = Duplicate(self.iface.mapCanvas())
        duplicateUvcFormIconPath = self.resourcesPath + 'pipette_icon.png'
        duplicateUvcFormAction = CustomAction(
            iconPath=duplicateUvcFormIconPath,
            text='Dupliquer une UVC',
            enabledFlag=False,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            mapTool=duplicate,
            editModeOnly=False,
            featureSelectedOnly=True,
            checkable=True
        )
        
        # UVC erasing action.
        eraser = Eraser()
        eraseUvcFormIconPath = self.resourcesPath + 'eraser.png'
        eraseUvcFormAction = CustomAction(
            iconPath=eraseUvcFormIconPath,
            text='Effacer toute la saisie associée aux UVC sélectionnées',
            enabledFlag=False,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=eraser.erase,
            editModeOnly=False,
            featureSelectedOnly=True,
            checkable=False
        )

        # Gabarit.
        gabarit = Gabarit(self.iface.mapCanvas())
        gabaritIconPath = self.resourcesPath + 'gabarit_icon.png'
        gabaritAction = CustomAction(
            iconPath=gabaritIconPath,
            text='Appliquer un gabarit au curseur.',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            mapTool=gabarit,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=True
        )
    
        # Open street view into default browser.
        openStView = StView(self.iface.mapCanvas())
        openStViewIconPath = self.resourcesPath + 'see_element.png'
        openStViewAction = CustomAction(
            iconPath=openStViewIconPath,
            text='Google street view',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            mapTool=openStView,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=True
        )
        
        # Color layer by acquisition progress.
        checkCompletion = CheckCompletion()
        checkCompletionIconPath = self.resourcesPath + 'completion_control.png'
        checkCompletionAction = CustomAction(
            iconPath=checkCompletionIconPath,
            text='Afficher l\'avancement de la saisie',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=checkCompletion.run,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=True
        )
        
        # Convert FSE layer to carhab layer (sqlite).
#        importFSE = ImportFSE()
        importFSEIconPath = self.resourcesPath + 'import_fse.png'
        importFSEAction = CustomAction(
            iconPath=importFSEIconPath,
            text='Peupler la couche de travail courante avec des données au format standard',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=run_import_std,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=False
        )
        
        # Export carhab layer (sqlite) to FSE format (csv).
#        exportFSE = ExportStd()
        exportFSEIconPath = self.resourcesPath + 'export_fse.png'
        exportFSEAction = CustomAction(
            iconPath=exportFSEIconPath,
            text='Exporter la couche de travail active dans le format standard',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=run_export,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=False
        )

        # Add menu.
        open_menu = QMenu(self.iface.mainWindow())
#        self.menu.addAction(openJobAction)
#        self.menu.addAction(importFSEAction)
        
        
        # Add created actions to plugin.
        self.add_action(newJobAction)
        self.add_action(openJobAction, open_menu)
        self.add_action(openCatalogAction)
        self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').addSeparator()
        self.add_action(openUvcFormAction)
        self.add_action(duplicateUvcFormAction)
        self.add_action(eraseUvcFormAction)
        self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').addSeparator()
        self.add_action(gabaritAction)
        #self.add_action(openStViewAction)
        self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').addSeparator()
        self.add_action(importLayerAction)
        self.add_action(checkCompletionAction)
        self.add_action(importFSEAction, open_menu)
        self.add_action(exportFSEAction)
        WorkLayerRegistry.instance().init_work_layers()
        self.iface.mapCanvas().renderComplete.connect(WorkLayerRegistry.instance().init_work_layers)
        
        
    def add_action(self, action, menu=None):
        '''
        Add custom actions to toolbar, menu and bind its to map tool if defined.
        
        :param action: A custom action instance.
        :type action: CustomAction
        '''
        if menu:
            if not menu in self.menus:
                toolbtn = QToolButton()
                toolbtn.setMenu(menu)
                toolbtn.setDefaultAction(action)
                toolbtn.setPopupMode(QToolButton.MenuButtonPopup)
#                self.iface.addToolBarWidget(toolbtn)
                self.toolbar.addWidget(toolbtn)
                self.menus.append(menu)
            menu.addAction(action)
        else:
            if action.isToAddToToolbar():
                self.toolbar.addAction(action)
        
        self.actions.append(action)

        if action.isToAddToMenu():
            self.iface.addPluginToMenu(
                self.menu,
                action)

        if action.getMapTool():
            action.getMapTool().setAction(action)

    def unload(self):
        '''Removes the plugin menu item and icon from QGIS GUI.'''
        
        s = QSettings()
        s.remove('cache_val')
        s.remove('layer_lgd_style')
        s.remove('current_info')
        for action in self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').actions():
            self.iface.removePluginMenu(
                'Saisie Carhab',
                action)
            self.iface.removeToolBarIcon(action)
