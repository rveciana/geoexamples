
from urllib2 import urlopen
from urllib2 import HTTPError
from sys import exit
from datetime import datetime
from barbs import draw_wind_barbs

def download_file(year,month,day,hour,valid_time):
    filename = "gfs_3_%d%02d%02d_%02d00_%03d.grb"%(year, month, day, hour, valid_time)
    url = "http://nomads.ncdc.noaa.gov/data/gfs-avn-hi/%d%02d/%d%02d%02d/gfs_3_%d%02d%02d_%02d00_%03d.grb"%(year, month, year, month, day, year, month, day, hour, valid_time)
    try: 
        req = urlopen(url)
    except HTTPError:
        print "File not found: May be the date is incorrect?"
        exit()

    f = open(filename, 'w')
    f.write(req.read())
    f.close()
    return filename

if __name__ == "__main__":
    now = datetime.now()
    print now.year
    year = raw_input('Type year ('+str(now.year)+'): ')
    month = raw_input('Type month ('+str(now.month)+'): ')
    day = raw_input('Type day ('+str(now.day)+'): ')
    hour = raw_input('Type hour (0): ')
    valid_time = raw_input('Type valid time (0): ')
    if (year == ''):
        year = now.year
    if (month == ''):
        month = now.month
    if (day == ''):
        day = now.day  
    if (hour == ''):
        hour = 0
    if (valid_time == ''):
        valid_time = 0     
    filename = download_file(int(year),int(month),int(day),int(hour),int(valid_time))
    out_filename = filename.replace("grb","png")

    print out_filename
    draw_wind_barbs(600, 400, out_filename, filename, 4326, [0, 0.1, 0, 70, 0, -0.1], 'UGRD', 'VGRD', '850-ISBL', 20, 20, '#000000')