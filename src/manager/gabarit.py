# -*- coding: utf-8 -*-
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsPoint, QgsGeometry
from qgis.gui import QgsMapTool, QgsRubberBand
from PyQt4.QtGui import QColor
from PyQt4.QtCore import QPoint

class Gabarit(QgsMapTool):
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
        self.activated.connect(self.createMoveTrack)
        self.deactivated.connect(self.destroyMovetrack)
        
        
    def createMoveTrack(self, line=False, color=QColor(255, 71, 25, 170), width=0.2):
        '''Create move track.
        
            :param line: Flag indicating if geometry to draw is a line (True)
                or a polygon(False).
            :type line: bool
        
            :param color: Color of line.
            :type color: QColor
            
            :param width: Width of line.
            :type width: int
            
            :return: Created rubber band. 
            :rtype: QgsRubberBand
        '''
        
        moveTrack = QgsRubberBand(self.canvas, line)
        moveTrack.setColor(color)
        moveTrack.setWidth(width)
        return moveTrack
    
    def getMoveTrack(self):
        '''Find and return move track.
        
            :return: Rubber band. 
            :rtype: QgsRubberBand
        '''
        
        for sceneItem in self.canvas.scene().items():
            if isinstance(sceneItem, QgsRubberBand):
                return sceneItem
        return None
    
    def updateMoveTrack(self, geometry):
        '''Update drawn move track.
        
            :param point: New point hovered by mouse cursor.
            :type point: QgsGeometry
        '''
        if self.getMoveTrack():
            if geometry.type() == 1 or geometry.type() == 2: # Geometry is polyline or polygon
                self.getMoveTrack().setToGeometry(geometry, None)
    
    def destroyMovetrack(self):
        '''Destroy drawn move track.'''
        if self.getMoveTrack():
            self.canvas.scene().removeItem(self.getMoveTrack())
    
    def canvasMoveEvent(self, event):
        '''Override slot fired when mouse is pressed.'''
        
        point = self.toMapCoordinates(QPoint(event.pos().x(), event.pos().y()))
        print point
        square = QgsGeometry().fromPoint(point).buffer(35, 1, 3, 1, 0)
        self.updateMoveTrack(square)
