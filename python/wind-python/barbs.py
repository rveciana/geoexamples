'''
Draws wind barbs on a png from a GRIB file using PIL
'''

import Image
import ImageDraw
from osgeo import gdal
from osgeo import osr
from osgeo.gdalconst import GA_ReadOnly
from math import floor
from math import ceil
from math import sqrt
from math import atan2
from math import degrees


def find_band_number(dataset, variable, level):
    '''
    Finds the band number inside the GRIB file, given the variable and the level names
    '''
    for i in range(1,dataset.RasterCount + 1):
        band = dataset.GetRasterBand(i)
        metadata = band.GetMetadata()
        band_level = metadata['GRIB_SHORT_NAME']
        band_variable = metadata['GRIB_ELEMENT']
        if (variable == band_variable) and (level == band_level):
            return i
    return None

def draw_barb(size, module, angle, color):
    extra_pixels = 10 #Avoid cutting the barb when rotating
    barb = Image.new('RGBA', (size + extra_pixels, size + extra_pixels))
    barb_draw = ImageDraw.Draw(barb)
    size = float(size) #Force it to float  
    separation = size/6
    module5 = int(round(module/5))

    x,v = divmod(module5,2)
    l,x = divmod(x,5)

    barb_draw.line([(extra_pixels,extra_pixels+size/2),(size+extra_pixels,extra_pixels+size/2)],color)
    pos = 0
    for nl in range(0,l,1): #50 kt triangles
        barb_draw.polygon([(extra_pixels+pos,extra_pixels+size/2),(extra_pixels+pos + extra_pixels+size/8,0),(extra_pixels+pos+size/4,extra_pixels+size/2),(extra_pixels+pos,extra_pixels+size/2)],color)

        pos = pos + size/4 + separation
    for nx in range(0,x,1):
        barb_draw.line([(extra_pixels+pos,extra_pixels+size/2),(extra_pixels+pos,extra_pixels+0)],color)

        pos = pos + separation
    if pos == 0: #advance a little for 5kt barbs
        pos = pos + separation
    if v == 1: # Only 0 or 1 are possible
        barb_draw.line([(extra_pixels+pos,extra_pixels+size/2),(extra_pixels+pos,extra_pixels+size/4)],color)

    barb = barb.rotate(angle, Image.BICUBIC)

    return barb

def draw_wind_barbs(xsize, ysize, out_file, data_file, epsg, geotransform, u_var, v_var, level, separation, barb_size, barb_color):
    out_img = Image.new('RGBA', (xsize, ysize) )

    dataset = gdal.Open(data_file, GA_ReadOnly )
    u_band_id = find_band_number(dataset, u_var, level)
    v_band_id = find_band_number(dataset, v_var, level)

    band_u = dataset.GetRasterBand(u_band_id)
    band_v = dataset.GetRasterBand(v_band_id)

    geotransform_in = dataset.GetGeoTransform()   

    xsize_in = band_u.XSize
    ysize_in = band_u.YSize

    values_u = band_u.ReadAsArray(0, 0, xsize_in, ysize_in)
    values_v = band_v.ReadAsArray(0, 0, xsize_in, ysize_in)
    

    proj_in = osr.SpatialReference()
    proj_in.SetFromUserInput(dataset.GetProjection())
    proj_out = osr.SpatialReference()
    proj_out.ImportFromEPSG(epsg)

    transf = osr.CoordinateTransformation(proj_out,proj_in)

    for px in range(0,xsize + separation,separation):
        x_out = geotransform[0] + px * geotransform[1]
        for py in range(0,ysize + separation,separation):
            y_out = geotransform[3] + py * geotransform[5]
            point = transf.TransformPoint(x_out, y_out,0)
            px_in = (float(point[0]) - geotransform_in[0]) / geotransform_in[1]
            py_in = (float(point[1]) - geotransform_in[3]) / geotransform_in[5]
           
            d1 = 1/sqrt( pow((px_in - floor(px_in)), 2) + pow((py_in - floor(py_in)), 2) )
            d2 = 1/sqrt( pow((ceil(px_in) - px_in), 2) + pow((py_in - floor(py_in)), 2) )
            d3 = 1/sqrt( pow((ceil(px_in) - px_in), 2) + pow((ceil(py_in) - py_in), 2) )
            d4 = 1/sqrt( pow((px_in - floor(px_in)), 2) + pow((ceil(py_in) - py_in), 2) ) 
            d_sum = d1 + d2 + d3 + d4   

            u = (d1*values_u[floor(py_in)][floor(px_in)] + d2*values_u[floor(py_in)][ceil(px_in)] + d3*values_u[ceil(py_in)][ceil(px_in)] + d4*values_u[ceil(py_in)][floor(px_in)]) / d_sum
            v = (d1*values_v[floor(py_in)][floor(px_in)] + d2*values_v[floor(py_in)][ceil(px_in)] + d3*values_v[ceil(py_in)][ceil(px_in)] + d4*values_v[ceil(py_in)][floor(px_in)]) / d_sum

            module = 1.943844494 * sqrt((u*u)+(v*v)) #in knots
           
            angle = degrees(atan2(v,u)) #Angle like in trigonometry, not wind direction where 0 is northern wind
            try:
                barb = draw_barb(barb_size, module, angle, barb_color)
                out_img.paste(barb, (px-(barb_size/2),py-(barb_size/2)), barb)
            except Exception, ex:
                raise Exception("No es pot dibuixar la barba: " + str(ex))
   
    out_img.save( out_file )

    #Creating the pngw worldfile
    fp = open(out_file.replace("png","pngw"),"w")
    print str(geotransform[1])+"\n0\n0\n"+str(geotransform[5])+"\n"+str(geotransform[0])+"\n"+str(geotransform[3])
    fp.write(str(geotransform[1])+"\n0\n0\n"+str(geotransform[5])+"\n"+str(geotransform[0])+"\n"+str(geotransform[3]))
    fp.close()

if __name__ == '__main__':
   
    draw_wind_barbs(600, 400, 'wind.png', 'gfs_3_20130524_0000_000.grb', 4326, [0, 0.1, 0, 70, 0, -0.1], 'UGRD', 'VGRD', '850-ISBL', 20, 20, '#000000')