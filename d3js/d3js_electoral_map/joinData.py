# -*- coding: UTF-8 -*-
from osgeo import ogr
import sys


electionData = {}

parties=["ERC","PP","PSC","ICV-EUiA","CiU","C's","CUP"]
f = open("newfile")
f.readline()
for line in f:
    data = line.split(";")
    #Només si hi ha municipi i no municipi
    nom = data[9].strip()
    
    if (", l'" in nom):
        nom = "L'"+nom.replace(", l'","")
    if (", les" in nom):
        nom = "Les "+nom.replace(", les","") 
    if (", la" in nom):
        nom = "La "+nom.replace(", la","")  
    if (", els" in nom):
        nom = "Els "+nom.replace(", els","") 
    if (", el" in nom):
        nom = "El "+nom.replace(", el","")   
    if (", es" in nom):
        nom = "Es "+nom.replace(", es","")  
    if (len(nom) > 0):

        if (nom in electionData) is False:
            electionData[nom] = {}
        electionData[nom][data[12].strip()] = data[14]
        print nom + " -- " + data[12].strip() + " -> " +data[14] 

f.close()

#sys.exit()
#Set the winner
for comarca in electionData.iterkeys():
    winner = None
    
    for party in electionData[comarca].iterkeys():
        #print party + " -> " + str(electionData[comarca][party])
        if (winner is None) or (int(electionData[comarca][party].replace(".","")) > int(electionData[comarca][winner].replace(".",""))):
            winner = party
            
    electionData[comarca]['winner'] = winner

#print electionData.keys()

##Create output
ds = ogr.Open( "./municipis.shp" )
if ds is None:
    print "Open failed.\n"
    sys.exit( 1 )

lyr = ds.GetLayerByName( "municipis" )
lyr.ResetReading()

proj = lyr.GetSpatialRef()

driverName = "ESRI Shapefile"
drv = ogr.GetDriverByName( driverName )
if drv is None:
    print "%s driver not available.\n" % driverName
    sys.exit( 1 )

dsOut = drv.CreateDataSource( "mun_out.shp" )
if dsOut is None:
    print "Creation of output file failed.\n"
    sys.exit( 1 )

lyrOut = dsOut.CreateLayer( "municipi", proj, ogr.wkbMultiPolygon )


if lyrOut is None:
    print "Layer creation failed.\n"
    sys.exit( 1 )

field_defn = ogr.FieldDefn( "Name", ogr.OFTString )
field_defn.SetWidth( 32 )
if lyrOut.CreateField ( field_defn ) != 0:
    print "Creating Name field failed.\n"
    sys.exit( 1 )


field_defn = ogr.FieldDefn( "Winner", ogr.OFTString )
field_defn.SetWidth( 32 )
if lyrOut.CreateField ( field_defn ) != 0:
    print "Creating Name field failed.\n"
    sys.exit( 1 )


for party in parties:
    field_defn = ogr.FieldDefn( party, ogr.OFTInteger )
    if lyrOut.CreateField ( field_defn ) != 0:
        print "Creating "+party+" field failed.\n"
        sys.exit( 1 )


for feat in lyr:
    feat_defn = lyr.GetLayerDefn()

    featOut = ogr.Feature( lyrOut.GetLayerDefn())
    #print "..."

    #print electionData[feat.GetFieldAsString(feat.GetFieldIndex('NOM_MUNI'))]
    muniName = feat.GetFieldAsString(feat.GetFieldIndex('name'))
    #LAst char is '
    print muniName

    if len(muniName)>0:
       if  muniName[-1] == "'":
          muniName = muniName[:-1]
    #muniName = muniName.replace("'"," ")
    #print muniName
    if muniName in electionData:
        
        comarcaData = electionData[muniName]
       
        featOut.SetField("Name",muniName)
        featOut.SetField("Winner",comarcaData['winner'])

        for party in parties:
            #print party+" -> "+comarcaData[party].replace(".","")

            if party in comarcaData:
                featOut.SetField( party, int(comarcaData[party].replace(".","")) )
            else:
                featOut.SetField( party, 0 )
        
        featOut.SetGeometry(feat.GetGeometryRef())
        if lyrOut.CreateFeature(featOut) != 0:
            print "Failed to create feature in shapefile.\n"
            sys.exit( 1 )
        featOut.Destroy()

ds = None
dsOut=None

#print electionData







