"""
Creates a shaded relief file from a DEM.
"""

from osgeo import gdal
from numpy import gradient
from numpy import pi
from numpy import arctan
from numpy import arctan2
from numpy import sin
from numpy import cos
from numpy import sqrt
from numpy import zeros
from numpy import uint8
import matplotlib.pyplot as plt

def hillshade(array, azimuth, angle_altitude): 
    
    x, y = gradient(array)
    slope = pi/2. - arctan(sqrt(x*x + y*y))
    aspect = arctan2(-x, y)
    azimuthrad = azimuth*pi / 180.
    altituderad = angle_altitude*pi / 180.
     
 
    shaded = sin(altituderad) * sin(slope)\
     + cos(altituderad) * cos(slope)\
     * cos(azimuthrad - aspect)
    return 255*(shaded + 1)/2

ds = gdal.Open('w001001.tiff')  
band = ds.GetRasterBand(1)  
arr = band.ReadAsArray()

hs_array = hillshade(arr,315, 45)
plt.imshow(hs_array,cmap='Greys')
plt.show()
