import os
import psycopg2 
import ogr

'''
Skript nacte veskere geometrie z shapefiles vsech obci do postgresql/postgis databaze.
'''

# Folders
url_shapefiles = '../shapefiles/'
 
# Change working directory to the folder containing shapefiles.
os.chdir(url_shapefiles)  

conn = psycopg2.connect('dbname=postgres user=postgres password= host=localhost port=5432')
cur = conn.cursor()

# Open all shapefiles.
for directory in os.listdir():
    os.chdir(url_shapefiles + directory + '/')
    
    sh = ogr.Open(directory + '.shp')
    layer = sh.GetLayer(0)
    
    # Get all features in the shapefile.
    for i in range(layer.GetFeatureCount()):
        f = layer.GetFeature(i)
        
        # Election result for one okrsek
        wkt = f.GetGeometryRef().ExportToWkt() # Geometry as Well-Known Text
        xobec = f.GetFieldAsString(3)
        xmc = f.GetFieldAsString(4)
        xokrsek = f.GetFieldAsString(1)
        
        # If momc code does not exist, we denote it by 0.
        if xmc == '':
            xmc = 0

        # Load geometry into database
        cur.execute('INSERT INTO Geo ("obec","momc","okrsek",geom) VALUES (%s,%s,%s,ST_Force_2D(ST_GeomFromText(%s,5514)))', 
                    (xobec, xmc, xokrsek, wkt))
        
        conn.commit()

cur.close()
conn.close()

        
        
    