import numpy
from numpy import zeros
from numpy import logical_and
from osgeo import gdal


classification_values = [0,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000] #The interval values to classify  
classification_output_values = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170] #The value assigned to each interval  
  


in_file = "InputFileName.tif"

ds = gdal.Open(in_file)
band = ds.GetRasterBand(1)
xsize = band.XSize
ysize = band.YSize

data = band.ReadAsArray(0, 0, xsize, ysize)

conditions_list = []
values_list_r = []
values_list_g = []
values_list_b = []

r = zeros((ysize, xsize), numpy.float)

for i in range(len(classification_values) - 1):
    r[logical_and(data >= classification_values[i], data < classification_values[i + 1])] = classification_output_values[i]

r[(data >= classification_values[i + 1])] = classification_output_values[i] 

format = "GTiff"
driver = gdal.GetDriverByName( format )
dst_ds = driver.Create("out.tif", xsize, ysize, 1, gdal.GDT_Byte )
dst_ds.SetGeoTransform(ds.GetGeoTransform())
dst_ds.SetProjection(ds.GetProjection())

dst_ds.GetRasterBand(1).WriteArray(r)

dst_ds = None
