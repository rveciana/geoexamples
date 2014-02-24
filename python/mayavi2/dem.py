"""
Plotting the terrain DEM with Mayavi2
"""

from osgeo import gdal
import numpy as np
from mayavi import mlab

ds = gdal.Open('dem.tiff')
data = ds.ReadAsArray()

data = data.astype(np.float32)

mlab.figure(size=(640, 800), bgcolor=(0.16, 0.28, 0.46))

surf = mlab.surf(data, warp_scale=0.2) 
mlab.show()