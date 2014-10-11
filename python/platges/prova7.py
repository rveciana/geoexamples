
from matplotlib import pyplot

from shapely.geometry import Polygon
from shapely.geometry import Point

from closest_polygon import closest_polygon
from descartes import PolygonPatch
if __name__ == '__main__':

    polygons = []
    polygons.append(Polygon([(4, 2), (4, 4), (6, 4), (6, 2)]))
    polygons.append(Polygon([(7, 2), (7, 4), (9, 4), (9, 2)]))
    polygons.append(Polygon([(2, 2), (2, 4), (4, 4), (4, 2), (3.5, 2), (3.5, 3.5), (3.2, 3.5), (3.2, 2)]))

   
    
    print closest_polygon(3, 3, 90, polygons)
    
    
    
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