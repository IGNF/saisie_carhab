import os.path
from utils_job import pluginDirectory
from qgis.utils import iface
from PyQt4.QtCore import Qt
from PyQt4.uic import loadUi

class SigmaFaciesForm(object):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self):
        """ Constructor. """
        
        self.sigmaFaciesFormUi = loadUi(os.path.join(pluginDirectory, 'form_sf.ui'))
        
    def run(self):
        '''Specific stuff at tool activating.'''
        
        
        # Show the carhab layer list
        iface.addDockWidget(Qt.RightDockWidgetArea, self.sigmaFaciesFormUi)