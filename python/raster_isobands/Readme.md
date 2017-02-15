These scripts create isobands from a raster file.

GDAL provides the program [gdal\_contour](http://www.gdal.org/gdal_contour.html), that generates vector contour lines at selected intervals from a raster file. But sometimes is better to have polygons instead of lines (like when creating filled contour maps), and unfortunately, gdal_contour doesn't  provide this feature.

There are two scripts, that are used exacly the same and produce the same results:

 * isobands\_matplotlib.py: The code is cleaner and fast, but requires matplotlib installed, which is not always possible
 * isobands\_gdal.py: Requires only GDAL python installed, but the code is dirtier.


```
    Usage: isobands_matplotlib.py [-h] [-b band] [-off offset] [-i interval]
    [-fl fixed levels [fixed levels ...]]
    [-nln layer_name] [-a attr_name] [-f formatname]
    src_file out_file
    Calculates the isobands from a raster into a vector file

    positional arguments:
      src_file         The raster source file
      out_file         The vectorial out file
    optional arguments:
      -h, --help       show this help message and exit
      -b band          The band in the source file to process (default 1)
      -off offset      The offset to start the isobands (default 0)
      -i interval      The interval (default 0)
      -fl fixed levels [fixed levels ...]
                       List of fixed levels (float)
      -nln layer_name  The out layer name (default bands)
      -a attr_name     The out layer attribute name (default h)
      -f formatname    The output file format name (default ESRI Shapefile)
```

You can get more information at this [GeoExamples blog entry](http://geoexamples.blogspot.com/2013/08/creating-vectorial-isobands-with-python.html)
