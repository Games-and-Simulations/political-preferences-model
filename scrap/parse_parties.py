import decimal

def parse(party_items, get_party_name):
    '''
    Precte volebni vysledek sledovanych stran a vratiho ve slovniku.
    Vycet sledovanych stran je dodan funkci 'get_party_name'.
    Vysledky zbylych stran jsou sectony do polozky OTHER.
    
    :param party_items: List listu vysledku voleb ve formatu
        [[cislo_strany(int), pocet_hlasu(int), procento_hlasu(Decimal)],]
    :param get_party_name: Funkce s jednim parametrem (cislo strany) vracejici 
        nazev strany prislusny k tomuto cislu v jednotlivych volbach. 
    :returns: Slovnik vysledku sledovanych stran jako jmeno_strany(string) => [pocet_hlasu(int), procento_hlasu(string)]
        
    '''
    dicti = {}
    dicti['OTHER'] = [0, decimal.Decimal(0.0)]
    for party in party_items:
        name = get_party_name(party[0])
        if name == 'OTHER':
            curr = dicti['OTHER']
            dicti['OTHER'] = [curr[0]+party[1], curr[1]+party[2]]
        else:
            dicti[name] = [party[1], str(party[2])]

    dicti['OTHER'][1] = str(dicti['OTHER'][1])
    
    return dicti
    