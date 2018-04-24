import csv
import psycopg2
import time

'''
Přečti csv soubor s demografickými daty, kde každý řádek jsou údaje o jedné osobě (včetně zeměpisných souřadnic).
Nahraje ho řádek po řádku do postgres/postgis databáze, tak, aby výsledný řádek v tabulce obsahoval nikoliv souřadnice,
ale údaje o obci, momc a oksrku.
'''

url = '../demography_csv/population-sample-brno.csv' # or population-sample-prague.csv
tablename = 'demo_brno' # or demo_prague


def save_row(row, cursor):
    long = row[1]
    lat = row[0]
    age = row[2]
    gender = row[3]
    education = row[4]
    status = row[5]
    activity = row[6]
    household = row[7]
    children = row[8]
    cursor.execute("SELECT geo.obec, geo.momc, geo.okrsek FROM geo WHERE ST_Contains(geo.geom, ST_Transform(ST_GeomFromText('POINT("+long+" "+lat+")', 4326), 5514))")
    result = cursor.fetchone()
    if result is None:
        print(long,lat,age,gender,education,status,activity,household,children)
        return
    obec = result[0]
    momc = result[1]
    okrsek = result[2]
    cursor.execute('INSERT INTO ' + tablename + ' ("obec","momc","okrsek","age","gender","education","status","activity","household","children") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                  (obec,momc,okrsek,age,gender,education,status,activity,household,children))
    
    

# Open connection to database
conn = psycopg2.connect('dbname=postgres user=postgres password= host=localhost port=5432')
cursor = conn.cursor()

with open(url) as f:
    csvfile = csv.reader(f)
    print(f.readline())
    
    counter = 1
    start = time.time()
    
    for line in csvfile:
        save_row(line, cursor)
        
        if counter % 10000 == 0:
            print(counter, time.time() - start)
            start = time.time()
        counter += 1
        conn.commit()
 
cursor.close()
conn.close()