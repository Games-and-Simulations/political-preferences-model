import psycopg2

'''
Skript pro tvorbu statistik z tabulky obyvatel.
Kazdy radek cilove tabulky obsahuje statistiky pro jeden okrsek a jeho identifikaci.


Statistiky:
        0 - total population in okrsek (constituency)
        1 - area of okrsek in km2
        2 - population density (population / area)
        3 - avg age
        4 - % people below 18 
        5 - % people aged [18,35) 
        6 - % peopla aged [35,55) 
        7 - % people aged [55,Inf) 
        8 - gender ratio
            EDUCATION
        9 - % people with BASIC
        10 - % w SECONDARY WITHOUT FINAL EXAM
        11 - % w SECONDARY WITH FINAL EXAM
        12 - % w HIGHER PROFESSIONAL
        13 - % w UNIVERSITY
            STATUS
        14 - % of people DIVORCED
        15 - % MARRIED
        16 - % SINGLE
        17 - % WIDOWED
            ACTIVITY
        18 - % of people INACTIVE
        19 - % STUDENT
        20 - % WORKING
        21 - % WORKING or STUDENT
            NUMBER OF PEOPLE IN A HOUSEHOLD
        22 - average 
        23 - % living alone (1)
        24 - % with someone (2)
        25 - % with more people (3+)
            CHILDREN
        26 - average
        27 - % with no children (0)
        28 - % with one or two (1-2)
        29 - % with more than two (3+)
'''

src_table = 'demo_prague'       # or demo_brno
target_table = 'stat_prague'    # or stat_brno
area = 'WHERE kraj=1 OR kraj=2' # or 'WHERE kraj=11'

def parse_enum(table):
    dicti = {}
    for row in table:
        num = row[0]
        category = row[1]
        dicti[category] = num
    return dicti

def get_val(dicti, key):
    try:
        return int(dicti[key])
    except KeyError:
        return 0



conn = psycopg2.connect('dbname=postgres user=postgres password= host=localhost port=5432')
cur = conn.cursor()

# Select all rows from geo relevant area
cur.execute('SELECT id, obec, momc, okrsek FROM geo ' + area)
rows = cur.fetchall()

for row in rows:
    obec = str(row[1])
    momc = str(row[2])
    okrsek = str(row[3])
    
    # pocet lidi v okrsku
    cur.execute('SELECT COUNT(id) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek)
    total = int(cur.fetchone()[0])
    if total == 0:
        print(obec, momc, okrsek, 'no matching entry in '+src_table)
        continue
    
    # plocha a hustota zalidneni
    cur.execute('''SELECT ST_Area(geom) FROM geo 
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek)
    area = float(cur.fetchone()[0]) / 1000000
    density = total / area
    
    # prumerny vek
    cur.execute('SELECT AVG(age) FROM '+src_table+'''
                   WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek)
    age_avg = float(cur.fetchone()[0])
    
    # vek < 18
    cur.execute('SELECT COUNT(age) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND age < 18')
    age_u18 = int(cur.fetchone()[0]) / total
 
    # vek 18 < 35
    cur.execute('SELECT COUNT(age) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND age > 17 AND age < 35')
    age_18to35 = int(cur.fetchone()[0]) / total
    
    # vek 35 < 55
    cur.execute('SELECT COUNT(age) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND age > 34 AND age < 55')
    age_35to55 = int(cur.fetchone()[0]) / total
    
    # vek 55 <
    cur.execute('SELECT COUNT(age) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND age > 54')
    age_55o = int(cur.fetchone()[0]) / total
    
    # gender ratio
    cur.execute('SELECT COUNT(gender), gender FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+'''
                    GROUP BY gender''')
    dicti = parse_enum(cur.fetchall())
    gender_male = get_val(dicti, 'MALE')
    gender_female = get_val(dicti, 'FEMALE')
    gender_ratio = gender_male / gender_female
 
    # education
    cur.execute('SELECT COUNT(education), education FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+'''
                    GROUP BY education''')
    d = parse_enum(cur.fetchall())
    #edu_undefined = get_val(d, 'UNDEFINED') / total
    edu_basic = get_val(d, 'BASIC') / total
    edu_without = get_val(d, 'SECONDARY_WITHOUT_FINAL_EXAM') / total
    edu_with = get_val(d, 'SECONDARY_WITH_FINAL_EXAM') / total
    edu_prof = get_val(d, 'HIGHER_PROFESSIONAL') / total
    edu_uni = get_val(d, 'UNIVERSITY') / total
    
    # status
    cur.execute('SELECT COUNT(status), status FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+'''
                    GROUP BY status''')
    d = parse_enum(cur.fetchall())                
    stat_div = get_val(d, 'DIVORCED') / total
    stat_mar = get_val(d, 'MARRIED') / total
    stat_sin = get_val(d, 'SINGLE') / total
    stat_wid = get_val(d, 'WIDOWED') / total
    
    # activity
    cur.execute('SELECT COUNT(activity), activity FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+'''
                    GROUP BY activity''')
    d = parse_enum(cur.fetchall())            
    act_inact = get_val(d, 'INACTIVE') / total
    act_stud = get_val(d, 'STUDENT') / total
    act_work = get_val(d, 'WORKING') / total
    #act_unknown = get_val(d, 'UNKNOWN') / total
    act_combi = act_stud + act_work
    
    # household average
    cur.execute('SELECT AVG(household) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek)
    house_avg = float(cur.fetchone()[0])
    
    # household = 1
    cur.execute('SELECT COUNT(household) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND household=1')
    house_one = int(cur.fetchone()[0]) / total
    # household = 2
    cur.execute('SELECT COUNT(household) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND household=2')
    house_two = int(cur.fetchone()[0]) / total
    # household > 2
    cur.execute('SELECT COUNT(household) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND household > 2')
    house_more = int(cur.fetchone()[0]) / total
    
    
    # children average
    cur.execute('SELECT AVG(children) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek)
    child_avg = float(cur.fetchone()[0])
    
    # children = 0
    cur.execute('SELECT COUNT(children) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND children=0')
    child_none = int(cur.fetchone()[0]) / total
    # children 1 or 2
    cur.execute('SELECT COUNT(children) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND children < 3 AND children > 0')
    child_oneortwo = int(cur.fetchone()[0]) / total
    # children > 2
    cur.execute('SELECT COUNT(children) FROM '+src_table+'''
                    WHERE obec='''+obec+' AND momc='+momc+' AND okrsek='+okrsek+' AND children > 2')
    child_more = int(cur.fetchone()[0]) / total
    
    cur.execute('INSERT INTO '+target_table+''' 
                (obec,momc,okrsek,population,area,density,age_avg,age_u18,age_18to35,age_35to55,age_55o,gender_ratio,
                edu_basic,edu_without,edu_with,edu_prof,edu_uni,status_single,status_married,
                status_divorced,status_widowed,act_inact,act_stud,act_work,act_combined,
                house_avg,house_one,house_two,house_more,children_avg,children_none,
                children_oneortwo,children_more)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s)''',
               (obec,momc,okrsek,total,area,density,age_avg,age_u18,age_18to35,age_35to55,age_55o,gender_ratio,
                edu_basic,edu_without,edu_with,edu_prof,edu_uni,stat_sin,stat_mar,
                stat_div,stat_wid,act_inact,act_stud,act_work,act_combi,
                house_avg,house_one,house_two,house_more,child_avg,child_none,
                child_oneortwo,child_more))
    conn.commit()

cur.close()
conn.close()