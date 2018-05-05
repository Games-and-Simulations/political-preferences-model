from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import json
from momc_translation import translate_momc as translate_momc
import os
import decimal
from parse_parties import parse

'''
Skript pro ziskavani vysledku voleb do poslanecke snemovny
ze stranek Ceskeho Statistickeho Uradu "volby.cz". 

Otestovan pro volby 2013 a 2017.

Zacina na strance s vysledky hlasovani za uzemni celky.
Odtud pokracuje na podstranky okresu a dale obci a nasledne
vycty okrsku nebo primo jednotlive okrsky, pokud obce obsahuje pouze jeden okrsek.

Kazdy okrsek je jednoznacne identifikovan tremi udaji:
    cislo obce
    cislo momc - mestska cast (maji pouze statutarni mesta, pro nase ucely maji ostatni uvedeno cislo 0)
    cislo okrsku

Data jsou ukladana do souboru po jednotlivych okrscich ve formatu JSON.
Nazev souboru ma format 'obec_momc_okrsek.json'.

startovni URL:
------
volby 2013: 'https://volby.cz/pls/ps2013/ps3?xjazyk=CZ'
volby 2017: 'https://volby.cz/pls/ps2017/ps3?xjazyk=CZ'
'''

# Import modulu pro zpracovani vysledku pro strany v danych volbach.
# Nutne importovat spravny modul (2013/2017).
from parse_parties2017 import get_party_name

# Vysledky budou ukladany do aktualni slozky.
os.chdir('../JSON/test')

# Startovni URL - hlavni stranka vysledku voleb.
url = 'https://volby.cz/pls/ps2017/ps3?xjazyk=CZ'



# g promenna udrzujici cislo prohledavaneho kraje
gxkraj = False

def delete_nbsp(string):
    '''
    Vymaze '&nbsp' character z retezce.
    '''
    if '\xa0' in string:
        idx = string.index('\xa0')
        string = string[:idx] + string[idx+1:]
    return string

def create_filename(xobec, xokrsek, xmc):
    '''
    Sestavi nazev souboru pro dany okrsek ve formatu 'obec_momc_okrsek.json'.
    '''
    if not xokrsek:
        xokrsek = '0'
    if not xmc:
        xmc = '0'
    return str(xobec) + '_' + str(xmc) + '_' + str(xokrsek) + '.json'

def put_into_json(xobec, xokrsek, xmc, xkraj, statistics, results):
    '''
    Ulozi data do json souboru (pro jeden okrsek) v aktualni slozce.
    Nazev souboru ma format 'obec_momc_okrsek.json'.
    '''
    filename = create_filename(xobec, xokrsek, xmc)
    file = open(filename, 'w')
    json.dump({'properties': 
                        {'xobec' : xobec,
                         'xokrsek' : xokrsek,
                         'xmc' : xmc,
                         'xkraj' : xkraj,
                         'statistics' : statistics,
                         'result' : results
                         }
                    }, file)
    file.close()
    
def statistics_scrap(table):
    '''
    Precte data z tabulky volebnich statistik
    '''
    items = table.find_all('td', class_='cislo')
    if len(items) == 9: # obec - 9 polozek, okrsek - 6 polozek
        items = items[3:]
    for item in range(0,len(items)): # smaz &nbsp; character
        items[item] = delete_nbsp(items[item].text.strip())
    return {
            'VOLICI' : int(items[0]),
            'VYDANE' : int(items[1]),
            'ODEVZDANE' : int(items[3]),
            'PLATNE' : int(items[4]),
            'UCAST' : str(items[2].replace(',','.')),
            'PLATNYCH' : str(items[5].replace(',','.'))
            }

def party_scrap(tables):
    '''
    Precte data z tabulky volebnich vysledku (pro vsechny strany).
    
    Vrati list listu ve formatu: [[cislo_strany, pocet_hlasu, procento_hlasu], ]
    Datove typy [[int, int, Decimal], ]
    '''
    party_items = []
    for parties_table in tables:
        for row in parties_table.find_all('tr')[2:]: # preskoc prvni dva radky
            i = row.find_all('td')
            # preskoc prazdne radky
            if (i[0].text.strip() == '-'): 
                continue
            party_items.append([int(i[0].text.strip()),  # cislo strany
                                int(delete_nbsp(i[2].text.strip())),  # pocet hlasu - nutne smazat &nbsp;
                                decimal.Decimal(i[3].text.strip().replace(',','.'))]) # procento hlasu
    return party_items

def process_results(url, base_okrsek):
    '''
    Zpracuje stranku s vysledky volebniho okrsku.
    '''
    soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
    # ziskani cisel obce a okrsku z URL
    query_dict = parse_qs(urlparse(url).query)
    
    xobec = int(query_dict['xobec'][0])
    xokrsek = 0
    xmc = 0
    if 'xokrsek' in query_dict:
        xokrsek = int(query_dict['xokrsek'][0]) - base_okrsek
    if 'xmc'in query_dict:
        xmc = int(query_dict['xmc'][0])

    # V pripade statutarnich mest obsahuje server volby.cz chybu.
    # URL parameter xobec ve skutecnosti obsahuje momc cislo (xmc) daneho okrsku.
    # Proto je dulezite z momc cisla ziskat cislo obce. K tomu slouzi funkce translate_momc()
    if translate_momc(xobec):
        # Pokud je kod obce obsazen ve slovniku momc kodu, pak ho pouzij jako momc a ziskej cislo obce.
        xmc = xobec
        xobec = translate_momc(xobec)
        
    tables = soup.find_all('table')
    # scrap volebnich statistik
    statistics = statistics_scrap(tables[0])
    # scrap volebnich vysledku
    results = parse(party_scrap(tables[1:]), get_party_name)
     
    global gxkraj
    put_into_json(xobec, xokrsek, xmc, gxkraj, statistics, results)
    
    
def process_okrsky(url):
    '''
    Zpracuje podstranku s vyctem okrsku v dane obci / mestske casti - otevre stranku kazdeho okrsku.
    '''
    u = urlparse(url)
    soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
    # najdi vsechny odkazy
    okrsek_links = soup.find_all('td', attrs={'class':'cislo'})
    
    # cislo okrsku nezacina vzdy na nule - je nutne pamatovat si offset
    base_okrsek = int(okrsek_links[0].find('a').text.strip()) - 1 
    for okrsek in okrsek_links:
        # vytvor odkaz
        query = okrsek.find('a')['href']
        chars_to_strip = len(u.path.split('/')[-1])
        newurl = u.scheme + '://' + u.netloc + u.path[:-chars_to_strip] + query
        # zpracuj vysledky okrsku
        process_results(newurl, base_okrsek)


def process_obec(url):
    '''
    Zpracuje stranku obce.
    '''
    soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
    # obec vs vyber okrsku
    if (soup.find('title').text.strip() == 'Výsledky hlasování za územní celky – výběr okrsku | volby.cz'):
        # dana obec je dale rozdelena na okrsky 
        process_okrsky(url)
    else:
        # obec obsahuje pouze jeden okrsek
        process_results(url, 0)


def process_okres_or_momc(url):
    '''
    Zpracuje podstranku okresu s tabulkami obci. Zanori se dale do kazde obce.
    '''
    u = urlparse(url)
    soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
    
    # stranka obsahuje nekolik tabulek s obcemi
    obec_tables = soup.find_all('table')
    
    for table in obec_tables:
        # ziskat vsechny radky v tabulce - prvni dve obsahuji jen nadpisy
        rows = table.find_all('tr')[2:]
        for row in rows:
            # ziskat vsechny odkazy v radce
            a = row.find_all('a')
            if not a: # radka neobsahuje odkazy, jsme na konci => ukoncit prohledavani
                return
            else:
                a = a[1]
                
            # vytvorit odkaz na podstranku obce
            query = a['href']
            chars_to_strip = len(u.path.split('/')[-1])
            newurl = u.scheme + '://' + u.netloc + u.path[:-chars_to_strip] + query
            
            if a.text.strip() == 'X': 
                # obec - vysledky obce nebo seznam okrsku
                process_obec(newurl)
            else: 
                # statutarni mesto - seznam mestskych casti se analogickou strukturou jako tato stranka
                process_okres_or_momc(newurl)


# --------
                
u = urlparse(url)
soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
# zacina se na celostatni urovni - prohledat kazdy kraj
for kraj in range(1, 15):
    # globalni promenna udrzujici cislo prohledavaneho kraje
    gxkraj = kraj
    
    # bunka tabulky s timto ID obsahuje nazev okresu
    okres_header = 't'+str(kraj)+'sa1 t'+str(kraj)+'sb2'
    okres_names = soup.find_all('td', attrs={'headers': okres_header})
    # bunka tabulky s timto ID obsahuje link na seznam obci v prislusnem okresu
    link_header = 't'+str(kraj)+'sa3'
    okres_links = soup.find_all('td', attrs={'headers': link_header})
    
    # odstranit 'Zahranici' - zahranicni okrsky vubec neprohledavat
    if (okres_names[-1].text.strip() == 'Zahraničí'):
        okres_names = okres_names[:-1]
        okres_links = okres_links[:-1]
    
    # prohledat kazdy nalezeny okres v kraji
    for okres in range(0, len(okres_links)):
        # vytvorit URL
        query = okres_links[okres].find('a')['href']
        chars_to_strip = len(u.path.split('/')[-1])
        newurl = u.scheme + '://' + u.netloc + u.path[:-chars_to_strip] + query
        # prohledat okres
        print('entering ' + okres_names[okres].text.strip() + ':\n')
        process_okres_or_momc(newurl)


