'''
isobands_matplotlib.py is a script for creating isobands.
Works in a similar way as gdal_contour, but creating polygons
instead of polylines

This version requires matplotlib, but there is another one,
isobands_gdal.py that uses only GDAL python
'''
from numpy import arange
from numpy import meshgrid
from osgeo import ogr
from osgeo import gdal
from osgeo import osr
from math import floor
from math import ceil
from os.path import exists
from os import remove
from argparse import ArgumentParser

import matplotlib
matplotlib.use('Agg') #workaround to make it run on systems without Xwindows
import matplotlib.pyplot as plt



def isobands(in_file, band, out_file, out_format, layer_name, attr_name, 
    offset, interval, fixed_levels, min_level = None):
    '''
    The method that calculates the isobands
    '''
    ds_in = gdal.Open(in_file)
    band_in = ds_in.GetRasterBand(band)
    xsize_in = band_in.XSize
    ysize_in = band_in.YSize

    geotransform_in = ds_in.GetGeoTransform()

    srs = osr.SpatialReference()
    srs.ImportFromWkt( ds_in.GetProjectionRef() )  

    #Creating the output vectorial file
    drv = ogr.GetDriverByName(out_format)

    if exists(out_file):
        remove(out_file)
    dst_ds = drv.CreateDataSource( out_file )
       
    dst_layer = dst_ds.CreateLayer(layer_name, geom_type = ogr.wkbPolygon, 
        srs = srs)

    fdef = ogr.FieldDefn( attr_name, ogr.OFTReal )
    dst_layer.CreateField( fdef )



    x_pos = arange(geotransform_in[0], 
        geotransform_in[0] + xsize_in*geotransform_in[1], geotransform_in[1])
    y_pos = arange(geotransform_in[3], 
        geotransform_in[3] + ysize_in*geotransform_in[5], geotransform_in[5])
    x_grid, y_grid = meshgrid(x_pos, y_pos)

    raster_values = band_in.ReadAsArray(0, 0, xsize_in, ysize_in)

    if fixed_levels != None:
        levels = fixed_levels
    else:
        stats = band_in.GetStatistics(False, True)
        if min_level == None:
            min_value = stats[0]
            min_level = offset + interval * floor((min_value - offset)/interval)
       
        max_value = stats[1]
        #Due to range issues, a level is added
        max_level = offset + interval * (1 + ceil((max_value - offset)/interval)) 
        levels = arange(min_level, max_level, interval)
    contours = plt.contourf(x_grid, y_grid, raster_values, levels)

    

    for level in range(len(contours.collections)):
        paths = contours.collections[level].get_paths()
        for path in paths:

            feat_out = ogr.Feature( dst_layer.GetLayerDefn())
            feat_out.SetField( attr_name, contours.levels[level] )
            pol = ogr.Geometry(ogr.wkbPolygon)


            ring = None            
            
            for i in range(len(path.vertices)):
                point = path.vertices[i]
                if path.codes[i] == 1:
                    if ring != None:
                        pol.AddGeometry(ring)
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    
                ring.AddPoint_2D(point[0], point[1])
            

            pol.AddGeometry(ring)
            
            feat_out.SetGeometry(pol)
            if dst_layer.CreateFeature(feat_out) != 0:
                print "Failed to create feature in shapefile.\n"
                exit( 1 )

            
            feat_out.Destroy()


if __name__ == "__main__":

    PARSER = ArgumentParser(
        description="Calculates the isobands from a raster into a vector file")
    PARSER.add_argument("src_file", help="The raster source file")
    PARSER.add_argument("out_file", help="The vectorial out file")
    PARSER.add_argument("-b", 
        help="The band in the source file to process (default 1)", 
        type=int, default = 1, metavar = 'band')
    PARSER.add_argument("-off", 
        help="The offset to start the isobands (default 0)", 
        type=float, default = 0.0, metavar = 'offset')
    PARSER.add_argument("-i", 
        help="The interval  (default 0)", 
        type=float, default = 0.0, metavar = 'interval')
    PARSER.add_argument("-fl", 
        help="name one or more 'fixed levels' to extract (default 0)", 
        type=float, nargs="+", metavar = 'fixed levels')
    PARSER.add_argument("-nln", 
        help="The out layer name  (default bands)", 
        default = 'bands', metavar = 'layer_name')
    PARSER.add_argument("-a", 
        help="The out layer attribute name  (default h)", 
        default = 'h', metavar = 'attr_name')
    PARSER.add_argument("-f", 
        help="The output file format name  (default ESRI Shapefile)", 
        default = 'ESRI Shapefile', metavar = 'formatname')
    ARGS = PARSER.parse_args()

    isobands(ARGS.src_file, ARGS.b, ARGS.out_file, ARGS.f, ARGS.nln, ARGS.a, 
        ARGS.off, ARGS.i, ARGS.fl)
