class Polygon(object):
    def __init__(self, geometry):
        self.uvc = None
        self.geometry = geometry

class PolygonModel(object):
    
    def __init__(self):
        pass
    
    def insertStatement(self, polygon):
        sql = "INSERT INTO polygon (uvc, the_geom) "
        sql += "VALUES (%d, %s)" % (polygon.uvc, polygon.geometry)
        return sql