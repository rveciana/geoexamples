import numpy
from osgeo import ogr
from osgeo import gdal
from osgeo import osr
from math import floor
from math import ceil
import matplotlib.pyplot as plt

'''
http://matplotlib.org/api/path_api.html
http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.contourf
http://matplotlib.org/basemap/api/basemap_api.html#mpl_toolkits.basemap.Basemap.contourf
http://fossies.org/dox/matplotlib-1.2.0/classmatplotlib_1_1contour_1_1QuadContourSet.html
'''

def isobands(in_file, band, out_file, out_format, band_name, offset, interval, min_level = None):

    ds_in = gdal.Open(in_file)
    band_in = ds_in.GetRasterBand(band)
    xsize_in = band_in.XSize
    ysize_in = band_in.YSize

    geotransform_in = ds_in.GetGeoTransform()

    srs = osr.SpatialReference()
    srs.ImportFromWkt( ds_in.GetProjectionRef() )  

    #Creating the output vectorial file
    drv = ogr.GetDriverByName(out_format)
    dst_ds = drv.CreateDataSource( out_file )
       
    dst_layer = dst_ds.CreateLayer(band_name, geom_type = ogr.wkbPolygon, srs = srs)

    fd = ogr.FieldDefn( band_name, ogr.OFTReal )
    dst_layer.CreateField( fd )



    x = numpy.arange(geotransform_in[0], geotransform_in[0] + xsize_in*geotransform_in[1], geotransform_in[1])
    y = numpy.arange(geotransform_in[3], geotransform_in[3] + ysize_in*geotransform_in[5], geotransform_in[5])
    X, Y = numpy.meshgrid(x, y)
    Z = band_in.ReadAsArray(0, 0, xsize_in, ysize_in)

    stats = band_in.GetStatistics(True, True)
    if min_level == None:
        min_value = stats[0]
        min_level = offset + interval * floor((min_value - offset)/interval)
   
    max_value = stats[1]
    max_level = offset + interval * (1 + ceil((max_value - offset)/interval)) #Due to range issues, a levels added

    N = numpy.arange(min_level, max_level, interval)

    cs = plt.contourf(X, Y, Z, N)

    

    for level in range(len(cs.collections)):
        paths = cs.collections[level].get_paths()
        for path in paths:

            feat_out = ogr.Feature( dst_layer.GetLayerDefn())
            feat_out.SetField( band_name, cs.levels[level] )
            pl = ogr.Geometry(ogr.wkbPolygon)


            ring = None            
            
            for i in range(len(path.vertices)):
                point = path.vertices[i]
                if path.codes[i] == 1:
                    if ring != None:
                        pl.AddGeometry(ring)
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    
                ring.AddPoint_2D(point[0], point[1])
            

            pl.AddGeometry(ring)
            
            feat_out.SetGeometry(pl)
            if dst_layer.CreateFeature(feat_out) != 0:
                print "Failed to create feature in shapefile.\n"
                exit( 1 )

            
            feat_out.Destroy()


if __name__ == "__main__":
    in_file = 'w001001.adf'
    band = 1
    interval = 500
    offset = 0
    out_file = 'polygons.shp' 
    out_format = "ESRI Shapefile"
    band_name = 'altitud'
    isobands(in_file, band, out_file, out_format,band_name,offset, interval)