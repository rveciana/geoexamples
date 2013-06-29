'''
Script to generate a png from a raster file.
It can be used from the command line or from an other python script
'''
from os.path import exists
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from sys import argv
from sys import exit
from numpy import logical_and
from numpy import zeros
from numpy import uint8
import scipy

'''
Main function.
Requires the input file, the color file and the otuput file name. 
The raster band is 1 by default. 
If nothing is asked, the discrete colroscale image is created.
'''
def raster2png(raster_file, color_file, out_file_name, raster_band=1, discrete=True):

    if exists(raster_file) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + raster_file + '\'')    
    
    dataset = gdal.Open(raster_file, GA_ReadOnly )
    if dataset == None:
        raise Exception("Unable to read the data file")
    
    band = dataset.GetRasterBand(raster_band)

    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]

    xsize = band.XSize
    ysize = band.YSize

    max_value = band.GetMaximum()
    min_value = band.GetMinimum()

    if max_value == None or min_value == None:
        stats = band.GetStatistics(0, 1)
        max_value = stats[1]
        min_value = stats[0]

    #Reading the color table
    color_table = readColorTable(color_file)
    #Adding an extra value to avoid problems with the last & first entry
    if sorted(color_table.keys())[0] > min_value:
        color_table[min_value - 1] = color_table[sorted(color_table.keys())[0]]

    if sorted(color_table.keys())[-1] < max_value:
        color_table[max_value + 1] = color_table[sorted(color_table.keys())[-1]]
    #Preparing the color table and the output file
    classification_values = color_table.keys()
    classification_values.sort()
    



    #rgb = zeros((ysize, xsize, 4), dtype = uint8)
    rgb = zeros((ysize, xsize, 4), dtype = uint8)

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
                
            
            values = band.ReadAsArray(j, i, cols, rows)
            r = zeros((rows, cols), dtype = uint8)
            g = zeros((rows, cols), dtype = uint8)
            b = zeros((rows, cols), dtype = uint8)
            a = zeros((rows, cols), dtype = uint8)

            for k in range(len(classification_values) - 1):
                #print classification_values[k]
                if classification_values[k] < max_value and (classification_values[k + 1] > min_value ):
                    mask = logical_and(values >= classification_values[k], values < classification_values[k + 1])
                    if discrete == True:
                        r = r + color_table[classification_values[k]][0] * mask
                        g = g + color_table[classification_values[k]][1] * mask
                        b = b + color_table[classification_values[k]][2] * mask
                        a = a + color_table[classification_values[k]][3] * mask
                    else:
                        v0 = float(classification_values[k])
                        v1 = float(classification_values[k + 1])

                        r = r + mask * (color_table[classification_values[k]][0] + (values - v0)*(color_table[classification_values[k + 1]][0] - color_table[classification_values[k]][0])/(v1-v0) )
                        g = g + mask * (color_table[classification_values[k]][1] + (values - v0)*(color_table[classification_values[k + 1]][1] - color_table[classification_values[k]][1])/(v1-v0) )
                        b = b + mask * (color_table[classification_values[k]][2] + (values - v0)*(color_table[classification_values[k + 1]][2] - color_table[classification_values[k]][2])/(v1-v0) )
                        a = a + mask * (color_table[classification_values[k]][3] + (values - v0)*(color_table[classification_values[k + 1]][3] - color_table[classification_values[k]][3])/(v1-v0) )
                     
            rgb[i:i+rows,j:j+cols, 0] = r 
            rgb[i:i+rows,j:j+cols, 1] = g 
            rgb[i:i+rows,j:j+cols, 2] = b
            rgb[i:i+rows,j:j+cols, 3] = a   

    scipy.misc.imsave(out_file_name, rgb)
    

def readColorTable(color_file):
    '''
    The method for reading the color file.
    * If alpha is not defined, a 255 value is set (no transparency).
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

'''
Usage explanation
'''
def Usage():
    print "Not enough arguments." 
    print "Usage:"
    print argv[0] + ' [-exact_color_entry] [-band=1] data_file color_file output_file'    
    exit()

'''
Program Mainline
'''
if __name__ == "__main__":
    
    file_name = None
    colorfile_name = None
    out_file_name = None
    discrete = False
    band = 1

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == '-exact_color_entry':
            discrete = True
        elif arg == '-band':
            band = argv[i+1]
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



    if len(argv) == 1 or file_name == None or colorfile_name == None or out_file_name == None: 
       Usage()     
    '''
    try:
        raster2png(file_name,colorfile_name,out_file_name,band,discrete)
    except Exception, ex:
        print "Error: " + str(ex)
    '''
    raster2png(file_name,colorfile_name,out_file_name,band,discrete)