'''
Creates a shaded relief from a dem file, combining a coloured DEM and a hillshade image
'''
from numpy import gradient
from numpy import pi
from numpy import arctan
from numpy import arctan2
from numpy import sin
from numpy import cos
from numpy import sqrt
from numpy import zeros
from numpy import mod
from numpy import ones
from numpy import uint8
from numpy import logical_and
from numpy import maximum
from numpy import minimum
from numpy import equal
from numpy import choose
from numpy import asarray
from numpy import transpose

from os.path import exists
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly

from sys import argv
from sys import exit

from Image import fromarray


def shaded_relief(in_file, raster_band, color_file, out_file_name,
    azimuth=315, angle_altitude=45):
    '''
    The main function. Reads the input image block by block to improve the performance, and calculates the shaded relief image
    '''

    if exists(in_file) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + in_file + '\'')    
    
    dataset = gdal.Open(in_file, GA_ReadOnly )
    if dataset == None:
        raise Exception("Unable to read the data file")
    
    band = dataset.GetRasterBand(raster_band)

    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]

    #If the block y size is 1, as in a GeoTIFF image, the gradient can't be calculated, 
    #so more than one block is used. In this case, using8 lines gives a similar 
    #result as taking the whole array.
    if y_block_size < 8:
        y_block_size = 8

    xsize = band.XSize
    ysize = band.YSize

    max_value = band.GetMaximum()
    min_value = band.GetMinimum()

    #Reading the color table
    color_table = readColorTable(color_file)
    #Adding an extra value to avoid problems with the last & first entry
    if sorted(color_table.keys())[0] > min_value:
        color_table[min_value - 1] = color_table[sorted(color_table.keys())[0]]

    if sorted(color_table.keys())[-1] < max_value:
        color_table[max_value + 1] = color_table[sorted(color_table.keys())[-1]]
    #Preparing the color table
    classification_values = color_table.keys()
    classification_values.sort()

    max_value = band.GetMaximum()
    min_value = band.GetMinimum()

    if max_value == None or min_value == None:
        stats = band.GetStatistics(0, 1)
        max_value = stats[1]
        min_value = stats[0]

    out_array = zeros((3, ysize, xsize), 'uint8')

    #The iteration over the blocks starts here
    for i in range(0, ysize, y_block_size):
        if i + y_block_size < ysize:
            rows = y_block_size
        else:
            rows = ysize - i
        
        for j in range(0, xsize, x_block_size):
            if j + x_block_size < xsize:
                cols = x_block_size
            else:
                cols = xsize - j

            dem_array = band.ReadAsArray(j, i, cols, rows)
            
            hs_array = hillshade(dem_array, azimuth, 
                angle_altitude)

            rgb_array = values2rgba(dem_array, color_table, 
                classification_values, max_value, min_value)

            hsv_array = rgb_to_hsv(rgb_array[:, :, 0], 
                rgb_array[:, :, 1], rgb_array[:, :, 2]) 

            hsv_adjusted = asarray( [hsv_array[0], 
                hsv_array[1], hs_array] )          

            shaded_array = hsv_to_rgb( hsv_adjusted )
            
            out_array[:,i:i+rows,j:j+cols] = shaded_array
    
    #Saving the image using the PIL library
    im = fromarray(transpose(out_array, (1,2,0)), mode='RGB')
    im.save(out_file_name)

def hillshade(array, azimuth, angle_altitude):
    '''
    This function calculates the value of the hillshade array, 
    given an altitudes array, an azimuth and an altitude angle
    '''
        
    x, y = gradient(array)
    slope = pi/2. - arctan(sqrt(x*x + y*y))
    aspect = arctan2(-x, y)
    azimuthrad = azimuth*pi / 180.
    altituderad = angle_altitude*pi / 180.
     
 
    shaded = sin(altituderad) * sin(slope)\
     + cos(altituderad) * cos(slope)\
     * cos(azimuthrad - aspect)
    return 255*(shaded + 1)/2

def values2rgba(array, color_table, classification_values, max_value, min_value):
    '''
    This function calculates a the color of an array given a color table. 
    The color is interpolated from the color table values.
    '''
    rgba = zeros((array.shape[0], array.shape[1], 4), dtype = uint8)

    for k in range(len(classification_values) - 1):
        if classification_values[k] < max_value and (classification_values[k + 1] > min_value ):
            mask = logical_and(array >= classification_values[k], array < classification_values[k + 1])

            v0 = float(classification_values[k])
            v1 = float(classification_values[k + 1])

            rgba[:,:,0] = rgba[:,:,0] + mask * (color_table[classification_values[k]][0] + (array - v0)*(color_table[classification_values[k + 1]][0] - color_table[classification_values[k]][0])/(v1-v0) )
            rgba[:,:,1] = rgba[:,:,1] + mask * (color_table[classification_values[k]][1] + (array - v0)*(color_table[classification_values[k + 1]][1] - color_table[classification_values[k]][1])/(v1-v0) )
            rgba[:,:,2] = rgba[:,:,2] + mask * (color_table[classification_values[k]][2] + (array - v0)*(color_table[classification_values[k + 1]][2] - color_table[classification_values[k]][2])/(v1-v0) )
            rgba[:,:,3] = rgba[:,:,3] + mask * (color_table[classification_values[k]][3] + (array - v0)*(color_table[classification_values[k + 1]][3] - color_table[classification_values[k]][3])/(v1-v0) )
    return rgba

def readColorTable(color_file):
    '''
    The method for reading the color file.
    '''    

    color_table = {}
    if exists(color_file) is False:
        raise Exception("Color file " + color_file + " does not exist")
    
    fp = open(color_file, "r")
    for line in fp:
        if line.find('#') == -1 and line.find('/') == -1:
            entry = line.split()
            if len(entry) == 5:
                alpha = int(entry[4])
            else:
                alpha=255
            color_table[eval(entry[0])]=[int(entry[1]),int(entry[2]),int(entry[3]),alpha]
    fp.close()
    
    return color_table

def rgb_to_hsv( r,g,b ):
    '''
    Converts an rgb array to hsv. 
    The algorithm is taken from 
    http://fwarmerdam.blogspot.com.es/2010/01/hsvmergepy.html
    '''
    maxc = maximum(r,maximum(g,b))
    minc = minimum(r,minimum(g,b))

    v = maxc

    minc_eq_maxc = equal(minc,maxc)

    # compute the difference, but reset zeros to ones to avoid divide by zeros later.
    ones_arr = ones((r.shape[0],r.shape[1]))
    maxc_minus_minc = choose( minc_eq_maxc, (maxc-minc,ones_arr) )

    s = (maxc-minc) / maximum(ones_arr,maxc)
    rc = (maxc-r) / maxc_minus_minc
    gc = (maxc-g) / maxc_minus_minc
    bc = (maxc-b) / maxc_minus_minc

    maxc_is_r = equal(maxc,r)
    maxc_is_g = equal(maxc,g)
    maxc_is_b = equal(maxc,b)

    h = zeros((r.shape[0],r.shape[1]))
    h = choose( maxc_is_b, (h,4.0+gc-rc) )
    h = choose( maxc_is_g, (h,2.0+rc-bc) )
    h = choose( maxc_is_r, (h,bc-gc) )

    h = mod(h/6.0,1.0)

    hsv = asarray([h,s,v])
    
    return hsv

def hsv_to_rgb( hsv ):
    '''
    Converts an hsv array to rgb. 
    The algorithm is taken from 
    http://fwarmerdam.blogspot.com.es/2010/01/hsvmergepy.html
    '''
    h = hsv[0]
    s = hsv[1]
    v = hsv[2]

    #if s == 0.0: return v, v, v
    i = (h*6.0).astype(int)
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))

    r = i.choose( v, q, p, p, t, v )
    g = i.choose( t, v, v, q, p, p )
    b = i.choose( p, p, t, v, v, q )

    rgb = asarray([r,g,b]).astype(uint8)
    
    return rgb    

'''
Usage explanation
'''
def Usage():
    print "Not enough arguments." 
    print "Usage:"
    print argv[0] + ' [-band=1] [-azimuth=315] [-altitude=45] data_file color_file output_file'    
    exit()

'''
Program Mainline
'''
if __name__ == "__main__":

    file_name = None
    colorfile_name = None
    out_file_name = None
    band = 1
    azimuth=315
    angle_altitude=45

    i = 1
    while i < len(argv):
        arg = argv[i]

        if arg == '-band':
            band = argv[i+1]
            i = i + 1
        elif arg == '-azimuth':
            azimuth = int(argv[i+1])
            i = i + 1
        elif arg == '-altitude':
            altitude = int(argv[i+1])
            i = i + 1
        elif file_name is None:
            file_name = arg
            file_name = file_name.replace("'","")
            file_name = file_name.replace('"','')
        elif colorfile_name is None:
            colorfile_name = arg
            colorfile_name = colorfile_name.replace("'","")
            colorfile_name = colorfile_name.replace('"','')
        elif out_file_name is None:
            out_file_name = arg
            out_file_name = out_file_name.replace("'","")
            out_file_name = out_file_name.replace('"','')
        i = i + 1   


    if (len(argv) == 1 or file_name == None or colorfile_name == None 
        or out_file_name == None): 
        Usage()     
    shaded_relief(file_name, 1, colorfile_name, out_file_name, 
        azimuth, angle_altitude)