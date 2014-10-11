from shapely.geometry import LineString

from math import cos
from math import sin
from math import pi

def closest_polygon(x, y, angle, polygons, dist = 100):
  
    angle = angle * pi / 180.0
    line = LineString([(x, y), (x + dist * sin(angle), y + dist * cos(angle))])

    i = 0  
    dist_min = None
    closest = None
    for polygon in polygons:
        
        difference = line.difference(polygon)
        
        if difference.geom_type == 'MultiLineString':
            dist = list(difference.geoms)[0].length
            
            if dist_min is None or dist_min > dist:
                dist_min = dist
                closest = i
        i += 1
    
    
    return closest