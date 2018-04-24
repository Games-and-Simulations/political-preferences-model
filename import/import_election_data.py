import os
import json
import psycopg2 
import ogr
from decimal import Decimal as D

'''
Skript pro kazdou feature v kazdem shapefile ve slozce (jedna feature odpovida jednomu okrsku)
nalezne JSON soubor s vysledky voleb a nahraje ho do tabulky v databazi.
Ke kazde radce v tabulce s vysledky voleb tedy existuje radka v tabulce geometrii. 

Pro volby 2013 - databazova tabulka Snemovna2013.
'''

# Folder with shapefiles
url_shapefiles = '../shapefiles/'
# Folder where json files (election results) are stored
url_json = '../JSON/Snemovna2013'



def construct_filename(xobec, xmc, xokrsek):
    if xmc == '':
        xmc = '0'
    if xokrsek == '':
        xokrsek = '0'
    return [str(xobec), '_', str(xmc), '_', str(xokrsek)]

def find_json(filename):
    os.chdir(url_json)
    jsfile = open(''.join(filename) + '.json')
    return jsfile
 
# Change working directory  
os.chdir(url_shapefiles)  

# Open connection to database
conn = psycopg2.connect('dbname=postgres user=postgres password= host=localhost port=5432')
cur = conn.cursor()

for directory in os.listdir():
    os.chdir(url_shapefiles + directory + '/')
    
    # ogr
    sh = ogr.Open(directory + '.shp')
    layer = sh.GetLayer(0)
    for i in range(layer.GetFeatureCount()):
        f = layer.GetFeature(i)
        # election result for one okrsek
        wkt = f.GetGeometryRef().ExportToWkt() # Geometry as Well-Known Text
        xobec = f.GetFieldAsString(3)
        xmc = f.GetFieldAsString(4)
        xokrsek = f.GetFieldAsString(1)
        
        if xmc == '':
            xmc = 0

        try:
            jsfile = json.load(find_json(construct_filename(xobec, xmc, xokrsek)))
            stats = jsfile['properties']['statistics']
            result = jsfile['properties']['result']
            
            
            # Load election result into database
            cur.execute('INSERT INTO Snemovna2013 ("obec","momc","okrsek","pocet_volicu","ucast","other","cssd","svobodni","pirati","top09","ods","kducsl","spo","usvit","ano","kscm","zeleni") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (xobec, xmc, xokrsek, stats['VOLICI'],
                         D(stats['UCAST']), D(result['OTHER'][1]),
                         D(result['CSSD'][1]), D(result['SVOBODNI'][1]),
                         D(result['PIRATI'][1]), D(result['TOP09'][1]),
                         D(result['ODS'][1]), D(result['KDU-CSL'][1]),
                         D(result['SPO'][1]), D(result['USVIT'][1]),
                         D(result['ANO'][1]), D(result['KSCM'][1]), D(result['ZELENI'][1])))
            
            conn.commit()
        except FileNotFoundError:
            print(xobec, xmc, xokrsek)
            
cur.close()
conn.close()

        
        
    