import numpy
from numpy import zeros
from numpy import logical_and
from osgeo import gdal

classification_values = [0,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000] #The interval values to classify  
classification_output_values = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170] #The value assigned to each interval  
  


in_file = "InputFileName.tif"

ds = gdal.Open(in_file)
band = ds.GetRasterBand(1)

block_sizes = band.GetBlockSize()
x_block_size = block_sizes[0]
y_block_size = block_sizes[1]

xsize = band.XSize
ysize = band.YSize

format = "GTiff"
driver = gdal.GetDriverByName( format )
dst_ds = driver.Create("out.tif", xsize, ysize, 1, gdal.GDT_Byte )
dst_ds.SetGeoTransform(ds.GetGeoTransform())
dst_ds.SetProjection(ds.GetProjection())



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

        data = band.ReadAsArray(j, i, cols, rows)
        r = zeros((rows, cols), numpy.float)

        for k in range(len(classification_values) - 1):
            r = r + classification_output_values[k] * logical_and(data >= classification_values[k], data < classification_values[k + 1])
        r = r + classification_output_values[k] * (data >= classification_values[k + 1])

        dst_ds.GetRasterBand(1).WriteArray(r,j,i)


dst_ds = None
