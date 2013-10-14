'''
Joins a shp file from EUROSTAT with the xls with the region names so
the resulting shp file has the name of every region and the code.
Roger Veciana, oct 2013
'''
from osgeo import ogr
from os.path import exists
from os.path import basename
from os.path import splitext
from os import remove

def create_shp(in_shp, out_shp, csv_data):
    print "Extracting data"
    
    in_ds = ogr.Open( in_shp )
    if in_ds is None:
        print "Open failed.\n"
        sys.exit( 1 )
    in_lyr = in_ds.GetLayerByName( splitext(basename(in_shp))[0] )
    if in_lyr is None:
        print "Error opening layer"
        sys.exit( 1 )

    if exists(out_shp):
        remove(out_shp)
    driver_name = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driver_name )
    if drv is None:
        print "%s driver not available.\n" % driver_name
        sys.exit( 1 )
    out_ds = drv.CreateDataSource( out_shp )
    if out_ds is None:
        print "Creation of output file failed.\n"
        sys.exit( 1 )
    proj = in_lyr.GetSpatialRef()
    ##Creating the layer with its fields
    out_lyr = out_ds.CreateLayer( 
        splitext(basename(out_shp))[0], proj, ogr.wkbMultiPolygon )
    lyr_def = in_lyr.GetLayerDefn ()
    for i in range(lyr_def.GetFieldCount()):
        out_lyr.CreateField ( lyr_def.GetFieldDefn(i) )

    field_defn = ogr.FieldDefn( "NAME", ogr.OFTString )
    out_lyr.CreateField ( field_defn )

    field_defn = ogr.FieldDefn( "COUNTRY", ogr.OFTString )
    out_lyr.CreateField ( field_defn )

    field_defn = ogr.FieldDefn( "COUNTRY_CO", ogr.OFTString )
    out_lyr.CreateField ( field_defn )

    field_defn = ogr.FieldDefn( "POPULATION", ogr.OFTInteger )
    out_lyr.CreateField ( field_defn )
    

    ##Writing all the features
    in_lyr.ResetReading()
    for feat_in in in_lyr:
        value = feat_in.GetFieldAsString(feat_in.GetFieldIndex('NUTS_ID'))
        if value in csv_data:
            #print csv_data[value]
            feat_out = ogr.Feature( out_lyr.GetLayerDefn())
            feat_out.SetField( 'NUTS_ID', value )
            feat_out.SetField( 'NAME', csv_data[value]['label'] )
            feat_out.SetField( 'POPULATION', csv_data[value]['population'] )
            feat_out.SetField( 'COUNTRY_CO', csv_data[value]['id_country'] )
            feat_out.SetField( 'COUNTRY', csv_data[csv_data[value]['id_country']]['label'] )
            feat_out.SetField( 'STAT_LEVL_', csv_data[value]['level'] )
            feat_out.SetField( 'SHAPE_AREA', feat_in.GetFieldAsString(feat_in.GetFieldIndex('SHAPE_AREA')) )
            feat_out.SetField( 'SHAPE_LEN', feat_in.GetFieldAsString(feat_in.GetFieldIndex('SHAPE_LEN')) )

            feat_out.SetGeometry(feat_in.GetGeometryRef())
            out_lyr.CreateFeature(feat_out)
    in_ds = None
    out_ds = None   

def read_population(csv_file):
    '''
    Reads the NUTS csv population file and returns the data in a dict
    '''
    csv_data = {}
    f = open(csv_file, "r")
    f.readline(); #Skip header
    for line in f:
        line_data = line.split(";")
        try:
            csv_data[line_data[0]] = int(float(line_data[4]) * 1000)
        except Exception, e:
            csv_data[line_data[0]] = -9999
    f.close

    return csv_data
def read_names(csv_file, population_data):
    '''
    Reads a NUTS csv file and returns the data in a dict
    '''
    csv_data = {}
    f = open(csv_file, "r")
    f.readline(); #Skip header
    for line in f:
        line_data = line.split(";")
        csv_data[line_data[0]] = {'label': line_data[1],
            'level': line_data[2],
            'id_country': line_data[3],
            'code_country': line_data[4],
            'population': 0}
        if line_data[0] in population_data:
            csv_data[line_data[0]]['population'] = population_data[line_data[0]]

    f.close

    return csv_data

if __name__ == '__main__':
    population_data = read_population('demo_r_d3avg_1_Data.csv')
    csv_data = read_names('NUTS_2010.csv', population_data)
    #create_shp('Data/NUTS_RG_03M_2010.shp', 'regions.shp', csv_data)
    create_shp('NUTS_2010_10M_SH/Data/NUTS_RG_10M_2010.shp', 'regions.shp', csv_data)