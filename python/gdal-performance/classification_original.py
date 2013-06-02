#! /usr/bin/python  
  
#Change the value with your raster filename here  
raster_file = 'InputFileName.tif'  
output_file = 'out.tif'  
  
classification_values = [0,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000] #The interval values to classify  
classification_output_values = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170] #The value assigned to each interval  
  
from osgeo import gdal  
from osgeo.gdalconst import *  
import numpy  
import struct  
  
#Opening the raster file  
dataset = gdal.Open(raster_file, GA_ReadOnly )  
band = dataset.GetRasterBand(1)  
#Reading the raster properties  
projectionfrom = dataset.GetProjection()  
geotransform = dataset.GetGeoTransform()  
xsize = band.XSize  
ysize = band.YSize  
datatype = band.DataType  
  
#Reading the raster values  
values = band.ReadRaster( 0, 0, xsize, ysize, xsize, ysize, datatype )  
#Conversion between GDAL types and python pack types (Can't use complex integer or float!!)  
data_types ={'Byte':'B','UInt16':'H','Int16':'h','UInt32':'I','Int32':'i','Float32':'f','Float64':'d'}  
values = struct.unpack(data_types[gdal.GetDataTypeName(band.DataType)]*xsize*ysize,values)  
  
#Now that the raster is into an array, let's classify it  
out_str = ''  
for value in values:  
    index = 0  
    for cl_value in classification_values:  
        if value <= cl_value:  
            out_str = out_str + struct.pack('B',classification_output_values[index])  
            break  
        index = index + 1  
#Once classified, write the output raster  
#In the example, it's not possible to use the same output format than the input file, because GDAL is not able to write this file format. Geotiff will be used instead  
gtiff = gdal.GetDriverByName('GTiff')   
output_dataset = gtiff.Create(output_file, xsize, ysize, 4)  
output_dataset.SetProjection(projectionfrom)  
output_dataset.SetGeoTransform(geotransform)  
  
output_dataset.GetRasterBand(1).WriteRaster( 0, 0, xsize, ysize, out_str )   
output_dataset = None  