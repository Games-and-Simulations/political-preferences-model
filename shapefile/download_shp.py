from bs4 import BeautifulSoup
import urllib
import zipfile
import os

'''
Skript stahne shapefiles jednotlivych obci ze stranek
Ceskeho uradu zemerickeho a katastralniho.
Ulozi je do slozek pojmenovanych kodem obce.

URL: http://services.cuzk.cz/shp/obec/epsg-5514/
'''

# Parameters
url_source = 'http://services.cuzk.cz/shp/obec/epsg-5514/'
url_target = '../shapefiles/'



def extract_VOP_file(zipf, namelist, xobec, extension):
    if xobec + '/VO_P' + extension in namelist:
        zipf.extract(xobec + '/VO_P' + extension)
    else:
        print('Folder ' + xobec + ' missing ' + extension)   

def extract_VOP_files(filename, xobec):
    zipf = zipfile.ZipFile(filename, 'r')
    namelist = zipf.namelist()
    extract_VOP_file(zipf, namelist, xobec, '.shp')
    extract_VOP_file(zipf, namelist, xobec, '.shx')
    extract_VOP_file(zipf, namelist, xobec, '.dbf')
    extract_VOP_file(zipf, namelist, xobec, '.prj')    
    zipf.close()
    
def rename_VOP_file(xobec, extension):
    try:
        os.rename(xobec + '/VO_P' + extension, xobec + '/' + xobec + extension)
    except FileExistsError:
        os.remove(xobec + '/VO_P' + extension)
    except FileNotFoundError:
        pass
        
def rename_VOP_files(xobec):
    rename_VOP_file(xobec, '.shp')
    rename_VOP_file(xobec, '.shx')
    rename_VOP_file(xobec, '.dbf')
    rename_VOP_file(xobec, '.prj')
        
        

# Change working directory
os.chdir(url_target)

# Load page
soup = BeautifulSoup(urllib.request.urlopen(url_source).read(), 'html.parser')
links = soup.find('table').find_all('a')

# Fetch and process data
for a in links:
    filename = a['href']
    xobec = filename.split('.')[0]
    # 1 download
    urllib.request.urlretrieve(url_source + filename, filename)
    # 2 extract
    extract_VOP_files(filename, xobec)
    # 3 rename
    rename_VOP_files(xobec)
    # 4 delete
    os.remove(filename)
    
