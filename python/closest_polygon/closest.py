'''
The post's first example
'''
from shapely.geometry import Polygon
from shapely.geometry import LineString
from math import cos
from math import sin
from math import pi

def closest_polygon(x, y, angle, polygons, dist = 10000):
   
    angle = angle * pi / 180.0
    line = LineString([(x, y), (x + dist * sin(angle), y + dist * cos(angle))])

    dist_min = None
    closest_polygon = None
    for i in range(len(polygons)):
        difference = line.difference(polygons[i])
        if difference.geom_type == 'MultiLineString':
            dist = list(difference.geoms)[0].length
            if dist_min is None or dist_min > dist:
                dist_min = dist
                closest_polygon = i
        
    
    
    return {'closest_polygon': closest_polygon, 'distance': dist_min}


if __name__ == '__main__':

    polygons = []
    polygons.append(Polygon([(4, 2), (4, 4), (6, 4), (6, 2)]))
    polygons.append(Polygon([(7, 2), (7, 4), (9, 4), (9, 2)]))
   
    
    print closest_polygon(3, 3, 90, polygons)

