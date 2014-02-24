"""
Draping an image over a terrain surface
"""
from osgeo import gdal
from tvtk.api import tvtk
from mayavi import mlab
import Image

ds = gdal.Open('dem.tiff')
data = ds.ReadAsArray()
im1 = Image.open("ortofoto.jpg")
im2 = im1.rotate(90)
im2.save("/tmp/ortofoto90.jpg")
bmp1 = tvtk.JPEGReader()
bmp1.file_name="/tmp/ortofoto90.jpg" #any jpeg file

my_texture=tvtk.Texture()
my_texture.interpolate=0
my_texture.set_input(0,bmp1.get_output())


mlab.figure(size=(640, 800), bgcolor=(0.16, 0.28, 0.46))

surf = mlab.surf(data, color=(1,1,1), warp_scale=0.2) 
surf.actor.enable_texture = True
surf.actor.tcoord_generator_mode = 'plane'
surf.actor.actor.texture = my_texture

mlab.show()

