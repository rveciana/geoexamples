import fiona
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from shapely.geometry import MultiPolygon, Polygon

'''
http://matplotlib.org/basemap/users/aeqd.html
'''


if __name__ == '__main__':
    


    fig = plt.figure()

    ax = fig.add_subplot(111, axisbg='w', frame_on=False)

    #width = 28000000
    width = 900000
    lon_0 = 10
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
    

    print type(polygons)
    for polygon in polygons:
        patch2b = PolygonPatch(polygon, fc='#555555', ec='#787878', alpha=0.5, zorder=2)
        ax.add_patch(patch2b)

    '''
    with fiona.open('world/ne_110m_admin_0_countries.shp', 'r') as source:
        for rec in source:
            pass
            #polygon = m(rec['geometry'])
            print type(rec['geometry'])
            
            #patch2b = PolygonPatch(polygon, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
            #plt.add_patch(patch2b)
    # draw the title.
    '''
    plt.title('Closest country')
    plt.show()