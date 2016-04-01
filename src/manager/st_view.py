# -*- coding: utf-8 -*-
import webbrowser
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem
from PyQt4.QtCore import QPoint
from qgis.gui import QgsMapTool

class StView(QgsMapTool):
    """
    /***************************************************************************
     Open Street Viw Class
            
            Open Street View at the clicked coordinates.
     ***************************************************************************/
     """
    def __init__(self, canvas):
        """ Constructor. """
        
        self.canvas = canvas
        
        # Declare inheritance to QgsMapTool class.
        super(QgsMapTool, self).__init__(canvas)
    
    def canvasPressEvent(self, event):
        '''Override slot fired when mouse is pressed.'''
        
        if event.button() == 1: # Do action only if left button was clicked
            point = self.toMapCoordinates(QPoint(event.pos().x(), event.pos().y()))
            source_crs = QgsCoordinateReferenceSystem(2154)
            dest_crs = QgsCoordinateReferenceSystem(4326)
            transform = QgsCoordinateTransform(source_crs, dest_crs)
            transformedPoint = transform.transform(point)
            
            url = 'https://www.google.fr/maps/?layer=c&cbll='+str(transformedPoint.y())+','+str(transformedPoint.x())
            webbrowser.open_new_tab(url)