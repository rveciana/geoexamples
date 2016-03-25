'''
isobands_matplotlib.py is a script for creating isobands.
Works in a similar way as gdal_contour, but creating polygons
instead of polylines

This version only requires GDAL python, but is more complicated
than isobands_matplotlib.py, that requires matplotlib
'''
from osgeo import ogr
from osgeo import gdal
from osgeo import osr
from math import floor
from os.path import exists
from os import remove
from argparse import ArgumentParser
import numpy

def isobands(in_file, band, out_file, out_format, layer_name, attr_name, 
    offset, interval, min_level = None):
    '''
    The method that calculates the isobands
    '''    
    #Loading the raster file
    ds_in = gdal.Open(in_file)
    band_in = ds_in.GetRasterBand(band)
    xsize_in = band_in.XSize
    ysize_in = band_in.YSize

    stats = band_in.GetStatistics(False, True)
    
    if min_level == None:
        min_value = stats[0]
        min_level = ( offset + interval * 
            (floor((min_value - offset)/interval) - 1) )
    nodata_value = min_level - interval    



    geotransform_in = ds_in.GetGeoTransform()
    
    srs = osr.SpatialReference()
    srs.ImportFromWkt( ds_in.GetProjectionRef() )  

    data_in = band_in.ReadAsArray(0, 0, xsize_in, ysize_in)


    #The contour memory
    contour_ds = ogr.GetDriverByName('Memory').CreateDataSource('')
    contour_lyr = contour_ds.CreateLayer('contour', 
        geom_type = ogr.wkbLineString25D, srs = srs )
    field_defn = ogr.FieldDefn('ID', ogr.OFTInteger)
    contour_lyr.CreateField(field_defn)
    field_defn = ogr.FieldDefn('elev', ogr.OFTReal)
    contour_lyr.CreateField(field_defn)

    #The in memory raster band, with new borders to close all the polygons
    driver = gdal.GetDriverByName( 'MEM' )
    xsize_out = xsize_in + 2
    ysize_out = ysize_in + 2

    column = numpy.ones((ysize_in, 1)) * nodata_value
    line = numpy.ones((1, xsize_out)) * nodata_value

    data_out = numpy.concatenate((column, data_in, column), axis=1)
    data_out = numpy.concatenate((line, data_out, line), axis=0)

    ds_mem = driver.Create( '', xsize_out, ysize_out, 1, band_in.DataType)
    ds_mem.GetRasterBand(1).WriteArray(data_out, 0, 0)
    ds_mem.SetProjection(ds_in.GetProjection())
    #We have added the buffer!
    ds_mem.SetGeoTransform((geotransform_in[0]-geotransform_in[1],
        geotransform_in[1], 0, geotransform_in[3]-geotransform_in[5], 
        0, geotransform_in[5]))
    gdal.ContourGenerate(ds_mem.GetRasterBand(1), interval, 
        offset, [], 0, 0, contour_lyr, 0, 1)

    #Creating the output vectorial file
    drv = ogr.GetDriverByName(out_format)
    if exists(out_file):
        remove(out_file)
    dst_ds = drv.CreateDataSource( out_file )

      
    dst_layer = dst_ds.CreateLayer(layer_name, 
        geom_type = ogr.wkbPolygon, srs = srs)

    fdef = ogr.FieldDefn( attr_name, ogr.OFTReal )
    dst_layer.CreateField( fdef )


    contour_lyr.ResetReading()

    geometry_list = {}
    for feat_in in contour_lyr:
        value = feat_in.GetFieldAsDouble(1)

        geom_in = feat_in.GetGeometryRef()
        points = geom_in.GetPoints()

        if ( (value >= min_level and points[0][0] == points[-1][0]) and 
            (points[0][1] == points[-1][1]) ):
            if (value in geometry_list) is False:
                geometry_list[value] = []

            pol = ogr.Geometry(ogr.wkbPolygon)
            ring = ogr.Geometry(ogr.wkbLinearRing)

            for point in points:

                p_y = point[1]
                p_x = point[0]
                          
                if p_x < (geotransform_in[0] + 0.5*geotransform_in[1]):
                    p_x = geotransform_in[0] + 0.5*geotransform_in[1]
                elif p_x > ( (geotransform_in[0] + 
                    (xsize_in - 0.5)*geotransform_in[1]) ):
                    p_x = ( geotransform_in[0] + 
                        (xsize_in - 0.5)*geotransform_in[1] )
                if p_y > (geotransform_in[3] + 0.5*geotransform_in[5]):
                    p_y = geotransform_in[3] + 0.5*geotransform_in[5]
                elif p_y < ( (geotransform_in[3] + 
                    (ysize_in - 0.5)*geotransform_in[5]) ):
                    p_y = ( geotransform_in[3] + 
                        (ysize_in - 0.5)*geotransform_in[5] )

                ring.AddPoint_2D(p_x, p_y)
                
  
            pol.AddGeometry(ring)
            geometry_list[value].append(pol)



    values = sorted(geometry_list.keys())

    geometry_list2 = {}

    for i in range(len(values)):
        geometry_list2[values[i]] = []
        interior_rings = []
        for j in range(len(geometry_list[values[i]])):
            if (j in interior_rings) == False:
                geom = geometry_list[values[i]][j]
                
                for k in range(len(geometry_list[values[i]])):
                    
                    if ((k in interior_rings) == False and 
                        (j in interior_rings) == False):
                        geom2 = geometry_list[values[i]][k]
                        
                        if j != k and geom2 != None and geom != None:
                            if geom2.Within(geom) == True:
                                
                                geom3 = geom.Difference(geom2)
                                interior_rings.append(k)
                                geometry_list[values[i]][j] = geom3
                                                            
                            elif geom.Within(geom2) == True:
                                
                                geom3 = geom2.Difference(geom)
                                interior_rings.append(j)
                                geometry_list[values[i]][k] = geom3
                    
        for j in range(len(geometry_list[values[i]])):
            if ( (j in interior_rings) == False and 
                geometry_list[values[i]][j] != None ):
                geometry_list2[values[i]].append(geometry_list[values[i]][j])
    

    for i in range(len(values)):
        value = values[i]
        if value >= min_level:
            for geom in geometry_list2[values[i]]:
                
                if i < len(values)-1:

                    for geom2 in geometry_list2[values[i+1]]:
                        if geom.Intersects(geom2) is True:
                            geom = geom.Difference(geom2)
                
                feat_out = ogr.Feature( dst_layer.GetLayerDefn())
                feat_out.SetField( attr_name, value )
                feat_out.SetGeometry(geom)
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
        ARGS.off, ARGS.i)
