# -*- coding: UTF-8 -*-
from osgeo import gdal
from osgeo import osr
import numpy
import numpy.ma as ma

datafile = 'wrfout_d01_2013-07-16_00:00:00'
#The pressure where we want to calculate the geopotential height
p_ref = 850

proj_out = osr.SpatialReference()
proj_out.SetPS(90, -1.5, 1, 0, 0)

ds_in = gdal.Open(datafile)


subdatasets = ds_in.GetSubDatasets()
variables = []
for subdataset in subdatasets:
    variables.append(subdataset[1].split(" ")[1])


ds_lon = gdal.Open('NETCDF:"wrfout_d01_2013-07-16_00:00:00":XLONG')
ds_lat = gdal.Open('NETCDF:"wrfout_d01_2013-07-16_00:00:00":XLAT')

longs = ds_lon.GetRasterBand(1).ReadAsArray()
lats = ds_lat.GetRasterBand(1).ReadAsArray()

ds_lon = None
ds_lat = None


#Calculating Geotransform
proj_gcp = osr.SpatialReference()
proj_gcp.ImportFromEPSG(4326)

transf = osr.CoordinateTransformation(proj_gcp, proj_out)

ul = transf.TransformPoint(float(longs[0][0]), float(lats[0][0]))
lr = transf.TransformPoint(float(longs[len(longs)-1][len(longs[0])-1]), float(lats[len(longs)-1][len(longs[0])-1]))

ur = transf.TransformPoint(float(longs[0][len(longs[0])-1]), float(lats[0][len(longs[0])-1]))
ll = transf.TransformPoint(float(longs[len(longs)-1][0]), float(lats[len(longs)-1][0]))

#Geotransform
gt0 = ul[0]
gt1 = (ur[0] - gt0) / len(longs[0])
gt2 = (lr[0] - gt0 - gt1*len(longs[0])) / len(longs)
gt3 = ul[1]
gt5 = (ll[1] - gt3) / len(longs)
gt4 = (lr[1] - gt3 - gt5*len(longs) ) / len(longs[0])


gt = (gt0,gt1,gt2,gt3,gt4,gt5)



'''
Calculate pressure
'''
ds_p = gdal.Open('NETCDF:"'+datafile+'":P')
ds_pb = gdal.Open('NETCDF:"'+datafile+'":PB')

num_bands = ds_p.RasterCount
num_bands_p = num_bands

x_size = ds_p.RasterXSize
y_size = ds_p.RasterYSize

data_p = numpy.zeros(((num_bands, y_size, x_size)))
for i in range(num_bands):
    data_p[i,:,:] = ( ds_p.GetRasterBand(num_bands - i).ReadAsArray() + ds_pb.GetRasterBand(num_bands - i).ReadAsArray() ) / 100

ds_p = None
ds_pb = None

'''
Height data
'''
ds_hgt = gdal.Open('NETCDF:"'+datafile+'":HGT')
data_hgt = ds_hgt.GetRasterBand(1).ReadAsArray()
ds_hgt = None
'''
Surface pressure data
'''
ds_psfc = gdal.Open('NETCDF:"'+datafile+'":PSFC')
data_psfc = ds_psfc.GetRasterBand(1).ReadAsArray()
ds_psfc = None
'''
TK data
'''
ds_t = gdal.Open('NETCDF:"'+datafile+'":T')
num_bands = ds_t.RasterCount
data_t = numpy.zeros(((num_bands, y_size, x_size)))
for i in range(num_bands):
    data_t[i,:,:] =  ds_t.GetRasterBand(num_bands - i).ReadAsArray()
ds_t = None

data_tk = (data_t + 300.) * pow( data_p / 1000 ,2.0/7.0) #Be careful with converting 2 and 7 to float!  
'''
QVAPOR (qv) data
'''
ds_qv = gdal.Open('NETCDF:"'+datafile+'":QVAPOR')
num_bands = ds_qv.RasterCount
data_qv = numpy.zeros(((num_bands, y_size, x_size)))
for i in range(num_bands):
    data_qv[i,:,:] =  ds_qv.GetRasterBand(num_bands - i).ReadAsArray()
ds_qv = None

'''
Calculate geopotential height
'''
ds_ph = gdal.Open('NETCDF:"'+datafile+'":PH')
ds_phb = gdal.Open('NETCDF:"'+datafile+'":PHB')

num_bands = ds_ph.RasterCount
data_hgp = numpy.zeros(((num_bands, ds_ph.RasterYSize, ds_ph.RasterXSize)))
for i in range(num_bands):
    data_hgp[i,:,:] = ( ds_ph.GetRasterBand(num_bands - i).ReadAsArray() + ds_phb.GetRasterBand(num_bands - i).ReadAsArray() ) / 9.81

ds_ph = None
ds_phb = None



data_positions = numpy.apply_along_axis(lambda a: a.searchsorted(p_ref), axis = 0, arr = data_p)

##Regular interpolation

p0 = numpy.choose(data_positions - 1, data_p)
p1 = numpy.choose(data_positions, data_p, mode = 'clip')

layer_p = numpy.where((p1-p0)!=0, (data_positions - 1)  + ((p_ref - p0) / (p1 - p0)), 0) 
layer_h = layer_p + 0.5

h0 = numpy.floor(layer_h).astype(int)
h1 = numpy.ceil(layer_h).astype(int)

data_out = ( numpy.choose(h0, data_hgp, mode = 'clip') * (h1 - layer_h) ) + ( numpy.choose(h1, data_hgp, mode = 'clip') * (layer_h - h0) )

#We apply a filter to avoid the cases where the layer is below the first one
data_out = data_out * (data_positions < num_bands_p)

##Extrapolation
##If the pressure is between the surface pressure and the lowest layer
array_filter = numpy.logical_and(data_positions == num_bands_p, p_ref*100 < data_psfc)

zlev = ( ( (100.*p_ref - 100*data_p[-1,:,:])*data_hgt + (data_psfc - 100.*p_ref)*data_hgp[-1,:,:] ) / (data_psfc - 100*data_p[-1,:,:])) 
data_out = data_out + (zlev * array_filter )


#If the pressure is higher than the surface pressure
array_filter = numpy.logical_and(data_positions == num_bands_p, p_ref*100 >= data_psfc)
expon=287.04*0.0065/9.81

ptarget = (data_psfc*0.01) - 150.0

#Calculates the value of the kupper, from the module_interp.f90 file
#adds a level to fit the original program value
kupper  = numpy.apply_along_axis(lambda a: numpy.where(a == numpy.min(a))[0][0] + 1, axis = 0, arr = numpy.absolute(data_p - ptarget))



pbot=numpy.maximum(100*data_p[-1,:,:], data_psfc)
zbot=numpy.minimum(data_hgp[-1,:,:], data_hgt)


tbotextrap=numpy.choose(kupper, data_tk) * pow((pbot/(100*numpy.choose(kupper, data_p))),expon)
#Virtual temp is calculated:
#virtual=tmp*(0.622+rmix)/(0.622*(1.+rmix))
#the original tvbotextrap formula is
#tvbotextrap=virtual(tbotextrap,data_qv[29,:,:])
tvbotextrap=tbotextrap*(0.622+data_qv[-1,:,:])/(0.622*(1+data_qv[-1,:,:]))

zlev = zbot+((tvbotextrap/0.0065)*(1.0-pow(100.0*p_ref/pbot,expon)))


data_out = data_out + ( zlev * array_filter )


#Write the output raster
driver = gdal.GetDriverByName( 'GTiff' )
ds_out = driver.Create( 'out.tiff', x_size, y_size, 1, gdal.GDT_Float32 )
ds_out.SetGeoTransform( gt )
ds_out.SetProjection(proj_out.ExportToWkt())
ds_out.GetRasterBand(1).WriteArray( data_out )


ds_in = None
ds_out = None