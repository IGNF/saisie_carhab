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
from resources_rc import *

from PyQt4.QtGui import QToolBar

from custom_action import CustomAction

from new_job import NewJob
from open_job import OpenJob
from import_layer import ImportLayer
from sigma_facies_form import SigmaFaciesForm
from uvc_form import UvcForm
from uvc_form_perso import UvcFormPerso
from st_view import StView
from gabarit import Gabarit
from check_completion import CheckCompletion
from fse import ImportFSE, ExportFSE

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
        self.menu = 'Saisie Carhab'
        self.toolbar = self.iface.addToolBar(u'SaisieCarhab')
        self.toolbar.setObjectName(u'SaisieCarhab')
        self.resourcesPath = ':/plugins/SaisieCarhab/resources/img/'

    def initGui(self):
        '''Instanciate CustomActions to add to plugin toolbar.'''
        
        # Open UVC mtd form action instance.
        openUvcFormPerso = UvcFormPerso(self.iface)
        openUvcFormPersoIconPath = self.resourcesPath + 'form_user.png'
        openUvcFormPersoAction = CustomAction(
            iconPath=openUvcFormPersoIconPath,
            text='Saisie des métadonnées.',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=openUvcFormPerso.run,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=False
            )
        
        # User disconnect action instance.
        userDisconnectIconPath = self.resourcesPath + 'user_disconnect.png'
        userDisconnectAction = CustomAction(
            iconPath=userDisconnectIconPath,
            text='Déconnexion.',
            enabledFlag=False,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=openUvcFormPerso.disconnect,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=False
            )
        
        # New job action instance.
        newJob = NewJob()
        newJobIconPath = self.resourcesPath + 'nouveau_chantier.png'
        newJobAction = CustomAction(
            iconPath=newJobIconPath,
            text='Nouveau job',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=newJob.run,
            editModeOnly=False,
            checkable=False
            )
        
        # Open job action instance.
        openJob = OpenJob()
        openJobIconPath = self.resourcesPath + 'ouvrir_chantier.png'
        openJobAction = CustomAction(
            iconPath=openJobIconPath,
            text='Ouvrir job existant',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=openJob.run,
            editModeOnly=False,
            checkable=False
            )
        
        # Import layer action instance.
        importLayer = ImportLayer()
        importLayerIconPath = self.resourcesPath + 'import_features.png'
        importLayerAction = CustomAction(
            iconPath=importLayerIconPath,
            text='Importer un shapefile dans un job',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=importLayer.run,
            editModeOnly=False,
            checkable=False
            )
        
        # Open UVC form action instance.
        openUvcForm = UvcForm(self.iface)
        openUvcFormIconPath = self.resourcesPath + 'form_uvc.png'
        openUvcFormAction = CustomAction(
            iconPath=openUvcFormIconPath,
            text='Saisie d\'UVC',
            enabledFlag=False,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=openUvcForm.run,
            editModeOnly=True,
            featureSelectedOnly=True,
            checkable=False
            )
        
        # Open Sigma facies form action instance.
        openSigmaFaciesForm = SigmaFaciesForm(self.iface)
        openSigmaFaciesFormIconPath = self.resourcesPath + 'form_sf.png'
        openSigmaFaciesFormAction = CustomAction(
            iconPath=openSigmaFaciesFormIconPath,
            text='Saisie de Sigma Facies',
            enabledFlag=False,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=openSigmaFaciesForm.run,
            editModeOnly=True,
            featureSelectedOnly=False,
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
            text='Afficher avancement de la saisie',
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
        importFSE = ImportFSE()
        importFSEIconPath = self.resourcesPath + 'import_fse.png'
        importFSEAction = CustomAction(
            iconPath=importFSEIconPath,
            text='Importer des données au format FSE',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=importFSE.run,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=False
            )
        
        # Export carhab layer (sqlite) to FSE format (csv).
        exportFSE = ExportFSE()
        exportFSEIconPath = self.resourcesPath + 'export_fse.png'
        exportFSEAction = CustomAction(
            iconPath=exportFSEIconPath,
            text='Exporter la couche carhab au format standard d\'échange',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            callback=exportFSE.run,
            editModeOnly=False,
            featureSelectedOnly=False,
            checkable=False
            )

        # Add created actions to plugin.
        self.addAction(openUvcFormPersoAction)
        self.addAction(userDisconnectAction)
        self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').addSeparator()
        self.addAction(newJobAction)
        self.addAction(openJobAction)
        self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').addSeparator()
        self.addAction(openUvcFormAction)
        self.addAction(openSigmaFaciesFormAction)
        self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').addSeparator()
        self.addAction(gabaritAction)
        self.addAction(openStViewAction)
        self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').addSeparator()
        self.addAction(importLayerAction)
        self.addAction(checkCompletionAction)
        self.addAction(importFSEAction)
        self.addAction(exportFSEAction)

    def addAction(self, action):
        '''
        Add custom actions to toolbar, menu and bind its to map tool if defined.
        
        :param action: A custom action instance.
        :type action: CustomAction
        '''

        self.actions.append(action)

        if action.isToAddToToolbar():
            self.toolbar.addAction(action)

        if action.isToAddToMenu():
            self.iface.addPluginToMenu(
                self.menu,
                action)

        if action.getMapTool():
            action.getMapTool().setAction(action)

    def unload(self):
        '''Removes the plugin menu item and icon from QGIS GUI.'''
        
        for action in self.iface.mainWindow().findChild(QToolBar, 'SaisieCarhab').actions():
            self.iface.removePluginMenu(
                'Saisie Carhab',
                action)
            self.iface.removeToolBarIcon(action)
