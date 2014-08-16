'''
Draws a map showing the closest country in each direction
'''
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from descartes import PolygonPatch

from numpy import concatenate
from numpy import linspace

from shapely.geometry import Polygon
from shapely.geometry import LineString
from math import cos
from math import sin
from math import pi

from argparse import ArgumentParser

class ClosestCountry:

    def __init__(self, center_lon, center_lat):


        self.center_lon = center_lon
        self.center_lat = center_lat
        
               
        
        
    def read_shape(self):
        #Read the countries shapefile
        self.map.readshapefile(
        'world/ne_110m_admin_0_countries',
        'world',
        color='none',
        zorder=2)

        self.xpt, self.ypt = self.map(self.center_lon, self.center_lat)

        self.polygons = [Polygon(w) for w in self.map.world]
        self.names = [w['name'] for w in self.map.world_info]
    def draw_map(self, num_angles = 360):

        #Create the map, with no countries
        self.map = Basemap(projection='aeqd',
                    lat_0=self.center_lat,lon_0=self.center_lon,resolution =None)
        #Iterate over all the angles:
        self.read_shape()
        results = {}
        distances = []
        for num in range(num_angles):
            angle = num * 360./num_angles
            closest, dist = self.closest_polygon(angle)
            if closest is not None:
                distances.append(dist)
                if (self.names[closest] in results) == False:
                    results[self.names[closest]] = []
                results[self.names[closest]].append(angle)

        width = reduce(lambda x, y: x + y, distances) / len(distances)
        #Create the figure so a legend can be added
        plt.close()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cmap = plt.get_cmap('Paired')
        
       
        self.map = Basemap(projection='aeqd', width=width, height=width,
                    lat_0=self.center_lat,lon_0=self.center_lon,resolution =None)
        self.read_shape()
        #m = Basemap(projection='aeqd', width=5000000, height=5000000,  lat_0=0,lon_0=70,resolution ='l')
        
        
        #Fill background.
        self.map.drawmapboundary(fill_color='aqua')

        #Draw parallels and meridians to give some references
        self.map.drawparallels(range(-80, 100, 20))
        self.map.drawmeridians(range(-180, 200, 20))

           
        #Draw a black dot at the center.
        xpt, ypt = self.map(self.center_lon, self.center_lat)
        self.map.plot([xpt],[ypt],'ko')
    
        #Draw the sectors
        for i in range(len(results.keys())):
            for angle in results[results.keys()[i]]:
                anglerad = float(angle) * pi / 180.0
                anglerad2 = float(angle + 360./num_angles) * pi / 180.0
                polygon = Polygon([(xpt, ypt), (xpt + width * sin(anglerad), ypt + width * cos(anglerad)), (xpt + width * sin(anglerad2), ypt + width * cos(anglerad2))])
                patch2b = PolygonPatch(polygon, fc=cmap(float(i)/(len(results) - 1)), ec=cmap(float(i)/(len(results) - 1)), alpha=1., zorder=1)
                ax.add_patch(patch2b)
        

        #Draw the countries
        for polygon in self.polygons:
            patch2b = PolygonPatch(polygon, fc='#555555', ec='#787878', alpha=1., zorder=2)
            ax.add_patch(patch2b)

        #Draw the legend
        cmap = self.cmap_discretize(cmap, len(results.keys()))
        mappable = cm.ScalarMappable(cmap=cmap)
        mappable.set_array([])
        mappable.set_clim(0, len(results))
        colorbar = plt.colorbar(mappable, ticks= [x + 0.5 for x in range(len(results.keys()))])
        colorbar.ax.set_yticklabels(results.keys())

        plt.title('Closest country')


    def closest_polygon(self, angle, dist = 280000000):
  
        angle = angle * pi / 180.0
        line = LineString([(self.xpt, self.ypt), (self.xpt + dist * sin(angle), self.ypt + dist * cos(angle))])

        i = 0  
        dist_min = None
        index_min = None
        for polygon in self.polygons:
            try:
                difference = line.difference(polygon)
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
            
        return (index_min, dist_min)
    def show_map(self):
        '''
        Shows the map on the screen
        '''

        plt.show()

    def save_map(self, out_file):
        '''
        Saves the figure to a file
        '''
        plt.savefig(out_file)


    def cmap_discretize(self, cmap, N):
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
        colors_i = concatenate((linspace(0, 1., N), (0., 0., 0., 0.)))
        
        colors_rgba = cmap(colors_i)
        
        indices = linspace(0, 1., N + 1)
        cdict = {}
        for ki, key in enumerate(('red', 'green', 'blue')):
            cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in xrange(N + 1)]
        
        return colors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)
'''
Program Mainline
'''
if __name__ == "__main__":

    PARSER = ArgumentParser(
        description="Creates a map with the closest country in each direction")
    PARSER.add_argument("lon", help="The point longitude", type=float)
    PARSER.add_argument("lat", help="The point latitude", type=float)
    PARSER.add_argument("-n", help="Number of angles", 
        type=int, default=10, metavar = 'num_angles')
    PARSER.add_argument("-o", help="Out file. If present, saves the file instead of showing it", 
        type=str, default=None, metavar = 'out_file')

    ARGS = PARSER.parse_args()

    INST = ClosestCountry(ARGS.lon, ARGS.lat)
    INST.draw_map(ARGS.n)
    if ARGS.o is None:
        INST.show_map()
    else:
        INST.save_map(ARGS.o)