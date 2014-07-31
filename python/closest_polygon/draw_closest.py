from shapely.geometry import Polygon
from descartes import PolygonPatch
from matplotlib import pyplot
def draw_polygons(polygons):
    BLUE = '#6699cc'
    GRAY = '#999999'
    RED = '#FF0000'

    fig = pyplot.figure(num=1, figsize=(4, 4), dpi=180)
    ax = fig.add_subplot(111)

    ax.plot(3, 3,'go')

    for polygon in polygons:

        patch2b = PolygonPatch(polygon, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
        ax.add_patch(patch2b)
    

    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.set_aspect(1)
    pyplot.show()

if __name__ == '__main__':

    polygons = []
    polygons.append(Polygon([(4, 2), (4, 4), (6, 4), (6, 2)]))
    polygons.append(Polygon([(7, 2), (7, 4), (9, 4), (9, 2)]))
   
    
    print draw_polygons(polygons)
    