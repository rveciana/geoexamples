from matplotlib import pyplot
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import Point
from descartes import PolygonPatch
from math import cos
from math import sin
from math import pi

def closest_polygon(x, y, angle, polygons, dist = 100):
  
    angle = angle * pi / 180.0
    line = LineString([(x, y), (x + dist * sin(angle), y + dist * cos(angle))])

    i = 0  
    dist_min = None
    for polygon in polygons:
        
        difference = line.difference(polygon)
        print i, difference
        if difference.geom_type == 'MultiLineString':
            dist = list(difference.geoms)[0].length
            print dist
            if dist_min is None or dist_min > dist:
                dist_min = dist
        i += 1
    print "Dist min: " , dist_min
    
    return i


if __name__ == '__main__':

    polygons = []
    polygons.append(Polygon([(4, 2), (4, 4), (6, 4), (6, 2)]))
    polygons.append(Polygon([(7, 2), (7, 4), (9, 4), (9, 2)]))
    polygons.append(Polygon([(2, 2), (2, 4), (4, 4), (4, 2), (3.5, 2), (3.5, 3.5), (3.2, 3.5), (3.2, 2)]))

   
    
    closest_polygon(3, 3, 90, polygons)
    
    
    
    BLUE = '#6699cc'
    GRAY = '#999999'
    RED = '#FF0000'

    fig = pyplot.figure(num=1, figsize=(10, 4), dpi=180)
    ax = fig.add_subplot(121)

    ax.plot(3, 3,'go')

    for polygon in polygons:

        patch2b = PolygonPatch(polygon, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
        ax.add_patch(patch2b)
    

    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.set_aspect(1)
    pyplot.show()
    
    
    

