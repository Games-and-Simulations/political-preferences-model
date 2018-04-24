

def get_party_name(party_num):
    '''
    Vycet sledovanych stran a jejich kodu ve volbach 2013.
    
    :param party_num: Cislo strany ve volbach 2013.
    :returns: Nazev strany prislusny k cislu.
    '''
    return {
        1: 'CSSD',
        2: 'SVOBODNI',
        3: 'PIRATI',
        4: 'TOP09',
        6: 'ODS',
        11: 'KDU-CSL',
        15: 'SPO',
        17: 'USVIT',
        20: 'ANO',
        21: 'KSCM',
        23: 'ZELENI'
            }.get(party_num, 'OTHER')
        