import fiona
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
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

def cmap_discretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)

    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
    print colors_i
    colors_rgba = cmap(colors_i)
    print colors_rgba
    indices = np.linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in xrange(N + 1)]
    
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)


if __name__ == '__main__':
    


    fig = plt.figure()

    ax = fig.add_subplot(111, axisbg='w', frame_on=False)

    #width = 28000000
    width = 100000
    width = 5500000
    lon_0 = 70
    lat_0 = 0
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

    results = {}
    num_angles = 2000
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
            if (None in results) == False:
                results[None] = []
            results[None].append(angle)
            print "NONE FOR %d"%num

    

    i = 0
    cb_names = []
    for name, angles in results.iteritems():
        print name, float(i)/(len(results) - 1), cmap(float(i)/(len(results) - 1))
        cb_names.append(name)

        for angle in angles:
            dist = width
            anglerad = float(angle) * pi / 180.0
            anglerad2 = float(angle + 360./num_angles) * pi / 180.0
            
            polygon = Polygon([(x, y), (x + dist * sin(anglerad), y + dist * cos(anglerad)), (x + dist * sin(anglerad2), y + dist * cos(anglerad2))])
            patch2b = PolygonPatch(polygon, fc=cmap(float(i)/(len(results) - 1)), ec=cmap(float(i)/(len(results) - 1)), alpha=1., zorder=1)
            ax.add_patch(patch2b)
            #m.plot([x, x + dist * sin(anglerad)], [y, y + dist * cos(anglerad)],color = cmap(float(i)/len(results)))

        i += 1
    

    for polygon in polygons:
        patch2b = PolygonPatch(polygon, fc='#555555', ec='#787878', alpha=1., zorder=2)
        ax.add_patch(patch2b)

    print len(results)
    #m.colorbar(ax,location='bottom',pad="5%")
    cmap = cmap_discretize(cmap, len(results))
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(0, len(results))
    colorbar = plt.colorbar(mappable, ticks= [x + 0.5 for x in range(len(results))])
    colorbar.ax.set_yticklabels(cb_names)
  
    plt.title('Closest country')
    plt.show()