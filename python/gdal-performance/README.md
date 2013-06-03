This examples blong to the blog entry [*GDAL performance: raster classification using NumPy*](http://geoexamples.blogspot.com/2013/06/gdal-performance-raster-classification.html)

The files are:
*classification_original.py: the first attempt [already explained in the blog](http://geoexamples.blogspot.com.es/2012/02/raster-classification-with-gdal-python.html)
*classification_numpy_arrays.py: The raster is classified using NumPy arrays
*classification_blocks.py: In addition to using NumPy arrays, the raster is read using blocks to improve the performance and be able to read *really big* files
*classification_blocks_minmx.py: A filter is used, so the classification values out of the raster range are not evaluated so the performance is improved.