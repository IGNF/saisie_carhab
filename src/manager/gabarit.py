# -*- coding: utf-8 -*-
from qgis.core import QgsGeometry, QgsRectangle
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
        self.counter = 0 # 0 = square, 1 = circle, 2 = horizontal rectangle, 3 = vertical rectangle
        
        # Declare inheritance to QgsMapTool class.
        super(QgsMapTool, self).__init__(canvas)
        self.activated.connect(self.activateGabarit)
        self.deactivated.connect(self.destroyMovetrack)
        
    def activateGabarit(self):
        
        self.counter = 0
        self.createMoveTrack()
    
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
    
    def setDesign(self, point):
        
        if self.counter == 0:
            gabarit = QgsGeometry().fromPoint(point).buffer(35, 1, 3, 1, 0)
        elif self.counter == 1:
            gabarit = QgsGeometry().fromPoint(point).buffer(40, 0)
        elif self.counter == 2:
            gabarit = QgsGeometry().fromRect(QgsRectangle(point[0] - 62.5, point[1] - 20, point[0] + 62.5, point[1] + 20))
        elif self.counter == 3:
            gabarit = QgsGeometry().fromRect(QgsRectangle(point[0] - 20, point[1] - 62.5, point[0] + 20, point[1] + 62.5))
        return gabarit
    
    def canvasMoveEvent(self, event):
        '''Override slot fired when mouse is moved.'''
        
        point = self.toMapCoordinates(QPoint(event.pos().x(), event.pos().y()))
        gabarit = self.setDesign(point)
        self.updateMoveTrack(gabarit)
    
    def canvasPressEvent(self, event):
        '''Override slot fired when mouse is pressed.'''
        
        point = self.toMapCoordinates(QPoint(event.pos().x(), event.pos().y()))
        if self.counter > 2:
            self.counter = 0
        else:
            self.counter += 1
        self.updateMoveTrack(self.setDesign(point))
