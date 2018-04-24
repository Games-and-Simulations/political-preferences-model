

def get_party_name(party_num):
    '''
    Vycet sledovanych stran a jejich kodu ve volbach 2017
    
    :param party_num: Cislo strany ve volbach 2017.
    :returns: Nazev strany prislusny k cislu.
    '''
    return {
        1: 'ODS',
        4: 'CSSD',
        7: 'STAN',
        8: 'KSCM',
        9: 'ZELENI',
        12: 'SVOBODNI',
        15: 'PIRATI',
        20: 'TOP09',
        21: 'ANO',
        24: 'KDU-CSL',
        29: 'SPD'
            }.get(party_num, 'OTHER')
        