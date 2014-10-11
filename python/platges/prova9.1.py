import fiona
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from descartes import PolygonPatch
from shapely.geometry import MultiPolygon, Polygon, LineString
from math import cos
from math import sin
from math import pi
'''
http://matplotlib.org/basemap/users/aeqd.html
http://sensitivecities.com/so-youd-like-to-make-a-map-using-python-EN.html#.U9fa8KqP8oM
'''

def closest_polygon(x, y, angle, polygons, dist = 900000):
  
    angle = angle * pi / 180.0
    line = LineString([(x, y), (x + dist * sin(angle), y + dist * cos(angle))])

    i = 0  
    dist_min = None
    index_min = None
    for polygon in polygons:
        try:

            difference = line.difference(polygon)
            #print i, difference
            if difference.geom_type == 'MultiLineString':
                
                dist = list(difference.geoms)[0].length
                #print i, dist
                if dist_min is None or dist_min > dist:
                    dist_min = dist
                    index_min = i
        except Exception, ex:
            pass
            #print "%d doesn't work"%i
        i += 1
        
    return index_min


if __name__ == '__main__':
    


    fig = plt.figure()

    ax = fig.add_subplot(111, axisbg='w', frame_on=False)

    #width = 28000000
    width = 1000000
    lon_0 = 7
    lat_0 = 38
    m = Basemap(width=width,height=width,projection='aeqd',
                lat_0=lat_0,lon_0=lon_0,resolution =None)
    # fill background.
    m.drawmapboundary(fill_color='aqua')
    # draw coasts and fill continents.
    #m.drawcoastlines(linewidth=0.5)
    #m.fillcontinents(color='coral',lake_color='aqua')
    # 20 degree graticule.
    m.drawparallels(np.arange(-80,81,20))
    m.drawmeridians(np.arange(-180,180,20))
    # draw a black dot at the center.
    xpt, ypt = m(lon_0, lat_0)
    m.plot([xpt],[ypt],'ko')

    m.readshapefile(
    'world/ne_110m_admin_0_countries',
    'world',
    color='none',
    zorder=2)

    polygons = [Polygon(xy) for xy in m.world]
    names = [w['name'] for w in m.world_info]

    x, y = m(lon_0, lat_0)

    cmap = plt.get_cmap('Paired')

    results = {None: []}
    num_angles = 20
    #for angle in range(0, 360, 1):
    for num in range(num_angles):
        angle = num * 360./num_angles
        closest = closest_polygon(x, y, angle, polygons, width * 10)
        if closest is not None:
            print "%f, %d, %s"%(float(angle), closest, names[closest])
            if (names[closest] in results) == False:
                results[names[closest]] = [angle]
            else:
                results[names[closest]].append(angle)
        else:
            results[None].append(angle)
            print "NONE FOR %d"


    i = 0
    for name, angles in results.iteritems():
        for angle in angles:
            dist = 1000000
            anglerad = float(angle) * pi / 180.0

            #m.plot([x, x + dist * sin(anglerad)], [y, y + dist * cos(anglerad)],color = cmap(float(i)/len(results)))

        i += 1
    

    for polygon in polygons:
        patch2b = PolygonPatch(polygon, fc='#555555', ec='#787878', alpha=0.5, zorder=2)
        ax.add_patch(patch2b)

    #m.colorbar(ax,location='bottom',pad="5%")
    cmap = cmap_discretize(cmap, 4)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, 4+0.5)
    colorbar = plt.colorbar(mappable)
    '''
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, len(results)+0.5)

    
    colorbar = plt.colorbar(mappable, location='bottom',pad="5%")
    colorbar.set_ticks(np.linspace(0, 4, 4))
    '''

    plt.title('Closest country')
    plt.show()