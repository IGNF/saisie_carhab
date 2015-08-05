from carhab_layer_registry import *
from utils_job import execFileDialog
        
class OpenJob(object):
    """
    /***************************************************************************
     Open Job Class
            
            Open a carhab layer job.
     ***************************************************************************/
     """
    def __init__(self):
        """ Constructor. """
        
        pass
        
    def run(self):
        '''Specific stuff at tool activating.'''
        
        selectedFileName = execFileDialog('*.sqlite')
        if selectedFileName:
            carhabLayer = CarhabLayer(selectedFileName)
            CarhabLayerRegistry.instance().addCarhabLayer(carhabLayer)
        