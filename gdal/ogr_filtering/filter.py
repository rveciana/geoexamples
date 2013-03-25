'''
Writes an ogr file from an input file, filtering the content
Roger Veciana, 23/mar/2013
'''
from osgeo import ogr
from os.path import exists
from os.path import basename
from os.path import splitext
from os import remove
import sys

def extract(in_file, out_file, filter_field, filter_values):
    '''
    Opens the input file, copies it into the oputput file, checking 
    the filter.
    '''
    print "Extracting data"
    
    in_ds = ogr.Open( in_file )
    if in_ds is None:
        print "Open failed.\n"
        sys.exit( 1 )
    in_lyr = in_ds.GetLayerByName( splitext(basename(in_file))[0] )
    if in_lyr is None:
        print "Error opening layer"
        sys.exit( 1 )


    ##Creating the output file, with its projection
    if exists(out_file):
        remove(out_file)
    driver_name = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driver_name )
    if drv is None:
        print "%s driver not available.\n" % driver_name
        sys.exit( 1 )
    out_ds = drv.CreateDataSource( out_file )
    if out_ds is None:
        print "Creation of output file failed.\n"
        sys.exit( 1 )
    proj = in_lyr.GetSpatialRef()
    ##Creating the layer with its fields
    out_lyr = out_ds.CreateLayer( 
        splitext(basename(out_file))[0], proj, ogr.wkbMultiPolygon )
    lyr_def = in_lyr.GetLayerDefn ()
    for i in range(lyr_def.GetFieldCount()):
        out_lyr.CreateField ( lyr_def.GetFieldDefn(i) )
    
    
    ##Writing all the features
    in_lyr.ResetReading()

    for feat in in_lyr:
        value = feat.GetFieldAsString(feat.GetFieldIndex(filter_field))
        if filter_func(value, filter_values):
            out_lyr.CreateFeature(feat)
       

    in_ds = None
    out_ds = None


def filter_func(value, filter_values):
    '''
    The custom filter function. In this case, we chack that the value is in the
    value list, stripping the white spaces. In the case of numeric values, a
    comparaison could be done
    '''
    if value.strip() in filter_values:
        return True
    else:
        return False

if __name__ == '__main__':
    extract('./recintos_ETRS89.shp', './municipis.shp',
     'provincia', ('8', '25', '17', '43'))

