# IMPORTANT! 
# El directori de treball des del que s'executa el programa ha de ser qVista/codi
# S'hauria d'executar d'una manera similar a:
# [PYTHON] "Programes específics/geocodificador cmd/geocodifica.py" [ARGS]

import sys
from moduls.QvMapificacio import QvMapificacio, PANDAS_ENABLED
if PANDAS_ENABLED:
    import pandas as pd
else:
    print('ATENCIÓ! És necessari el mòdul pandas per utilitzar aquest programa')
    sys.exit(1)
from moduls.QvMapVars import MAP_ZONES
import configuracioQvista
from moduls.QvApp import QvApp
import argparse
import math
from qgis.core import QgsVectorLayer
from qgis.core.contextmanagers import qgisapp
import os
from pathlib import Path
import shutil

def get_args():
    parser = argparse.ArgumentParser(description='Geocodifica un arxiu csv, afegint-li camps de coordenades ETRS89 al final')
    # afegir l'adreça del csv
    parser.add_argument('arxiu',help="Ruta de l'arxiu a geocodificar", type=str, nargs=1)
    parser.add_argument('--sortida',help="Ruta on volem l'arxiu de sortida. Si no s'indica, sortirà en un directori per defecte", default=None)
    parser.add_argument('--tipus-via',help="Camp on tenim el tipus de via de l'adreça, si en tenim", default=None)
    parser.add_argument('--via',help="Camp on tenim la via de l'adreça, si en tenim", default="Nom_via")
    parser.add_argument('--num-ini',help="Camp on tenim el número inicial (o número en general) de l'adreça, si en tenim", default=None)
    parser.add_argument('--num-fin',help="Camp on tenim el número final de l'adreça, si en tenim", default=None)
    parser.add_argument('--lletra-ini',help="Camp on tenim el número inicial (o número en general) de l'adreça, si en tenim", default=None)
    parser.add_argument('--lletra-fin',help="Camp on tenim el número final de l'adreça, si en tenim", default=None)
    parser.add_argument('--zones', help=f"Zones resultants que volem obtenir amb la geocodificació. {', '.join(MAP_ZONES.keys())}", default=None, nargs='*')
    try:
        parser.add_argument('--extrapola-dades-zona',help='Si no funciona la geocodificació, extrapolarà les dades a partir de la zona (barri/districte)', action=argparse.BooleanOptionalAction, default=False)
    except AttributeError:
        # Versió anterior a la 3.9
        parser.add_argument('--extrapola-dades-zona', action='store_true', help='Si no funciona la geocodificació, extrapolarà les dades a partir de la zona (barri/districte)', default=False)
        parser.add_argument('--no-extrapola-dades-zona', dest='extrapola-dades-zona', action='store_false')
        pass
    parser.add_argument('--nom-barri',help="Camp on tenim el nom del barri, si en tenim", default=None)
    parser.add_argument('--nom-districte',help="Camp on tenim el nom del districte, si en tenim", default=None)
    parser.add_argument('--codi-barri', help="Camp on tenim el codi del barri, si en tenim", default=None)
    parser.add_argument('--codi-districte', help="Camp on tenim el codi del districte, si en tenim", default=None)

    return parser.parse_args()

def print_error_o_avis(*args, tipus=None, **kwargs):
    if tipus is None:
        tipus='INDETERMINAT'
    print(f'{tipus}: ', *args, **kwargs)
def print_error(*args, **kwargs):
    print_error_o_avis(*args, tipus='ERROR', **kwargs)
def print_avis(*args, **kwargs):
    print_error_o_avis(*args, tipus='AVÍS', **kwargs)

def rsplit(txt, seps, maxsplit):
    """Emula el str.rsplit permetent utilitzar múltiples separadors. Si només tenim un separador, és exactament igual

    Args:
        txt (str): Text que volem fer split
        seps (str|List[str]): Separador o llista de separadors
        maxsplit (int): Nombre màxim de splits que volem fer

    Returns:
        List[str]: Resultat de fer split
    """
    if isinstance(seps, str):
        return txt.rsplit(seps, maxsplit)
    # El mòdul re té la funció split, que permet passar una expressió regular
    # Per emular el rsplit, fem un split normal sobre el text invertit
    # Ens queda una llista invertida amb els resultats invertits, així que ho invertim tot
    # l[::-1] inverteix la llista l
    # Donat que poden aparèixer separadors junts (per exemple: 'Diagonal, 220' té la coma i l'espai seguits),
    #  fem un strip per evitar que quedin caràcters sobrants als extrems del string
    import re
    invers = txt[::-1]
    seps_str = "".join(seps)
    aux = re.split(f'[{seps_str}]',invers, maxsplit=maxsplit)
    return [x[::-1].strip(seps_str) for x in aux][::-1]


def adapta_nom(nom):
    """Adapta un nom de manera que no hi hagi confusions per diferents formes d'escriure
    Converteix el nom en minúscula, elimina els espais, cometes simples i cometes dobles, així com els accents

    Args:
        nom (str): Nom que volem adaptar
    Returns:
        str: el nom passat per paràmetres, aplicant-li els canvis descrits
    """
    canvis = (
        (' ',''),
        ('"',''),
        ("'",''),
        ('à','a'),
        ('è','e'),
        ('é','e'),
        ('í','i'),
        ('ò','o'),
        ('ó','o'),
        ('ú','u'),
        ('ï','i'),
        ('ü','u')
    )
    nom = nom.lower()
    for (x,y) in canvis:
        nom = nom.replace(x, y)
    # nom = nom.replace(' ','').replace('"','').replace("'",'')
    return nom

def extrapola_dades_zones(df, fallen, args):
    """Modifica el dataframe per posar les coordenades a les files que no en tenen a partir dels barris/districtes.
    Afegeix també un camp que indica si les coordenades s'han extrapolat

    Args:
        df (pandas.DataFrame): DataFrame amb totes les files
        fallen (pandas.DataFrame): DataFrame amb les files que fallen
        args (argparse.Namespace): Arguments que s'han passat al programa

    Returns:
        pandas.DataFrame: df modificat per afegir les coordenades extrapolades
    """
    # Molt optimitzable
    # Però com que es cridarà poc, tampoc passa res
    pathZones = 'dades/Zones.gpkg'
    pathBarris = pathZones+'|layername=barris'
    layerBarris = QgsVectorLayer(pathBarris, 'ogr')
    pathDistrictes = pathZones+'|layername=districtes'
    layerDistrictes = QgsVectorLayer(pathDistrictes, 'ogr')
    barris = {}
    barris_codi = {}
    for rowB in layerBarris.getFeatures():
        atributs = rowB.attributes()
        # num_barri = atributs[1]
        nom_barri = adapta_nom(atributs[2])
        codi_barri = atributs[1]
        # num_districte = atributs[3]
        centre = rowB.geometry().centroid().asPoint()

        barris[nom_barri] = centre
        barris_codi[codi_barri] = centre
    
    districtes = {}
    districtes_codi = {}
    for rowD in layerDistrictes.getFeatures():
        atributs = rowD.attributes()
        nom_districte = adapta_nom(atributs[2])
        codi_districte = atributs[1]
        centre = rowB.geometry().centroid().asPoint()
        districtes[nom_districte]=centre
        districtes_codi[codi_districte]=centre
    def obte_punt_codi(row, camp_codi, dic):
        """Obté un punt a partir del codi (de districte o de barri)

        Args:
            row (dict): Fila del csv d'on hem de treure el codi
            camp_codi (str): Nom del camp d'on hem de treure el codi
            dic (dict): Diccionari d'on hem de treure el punt (districtes_codi o barris_codi)

        Returns:
            QgsPointXY: Centroide del districte/barri buscat
        """
        try:
            codi = row[camp_codi]
            if codi is None:
                return None
            codi = str(codi)
            if len(codi)==1:
                codi = '0'+codi
            return dic[codi]
        except:
            return None
    def obte_punt_nom(row, camp_nom, dic):
        """Obté un punt a partir del nom del districte o del barri

        Args:
            row (dict): Fila del csv d'on hem de treure el nom
            camp_nom (str): Nom del camp d'on hem de treure el nom del districte/barri
            dic (dict): Diccionari d'on hem de treure el punt (districtes_codi o barris_codi)

        Returns:
            QgsPointXY: Centroide del districte/barri buscat
        """
        try:
            nom = adapta_nom(row[camp_nom])
            return dic[nom]
        except:
            return None
    # for (index, row) in df.iterrows():
        # if math.isnan(row['QVISTA_ETRS89_COORD_X']):
    df['INFERIT_DE_ZONA'] = 'No'
    for (index, row) in fallen.iterrows():
        punts_possibles = (
            obte_punt_codi(row, args.codi_barri, barris_codi),
            obte_punt_nom(row, args.nom_barri, barris),
            obte_punt_codi(row,args.codi_districte, districtes_codi),
            obte_punt_nom(row,args.nom_districte, districtes)
        )
        punts = filter(lambda x: x is not None, punts_possibles)
        try:
            punt = next(punts)
        except:
            continue
        df.loc[index,'QVISTA_ETRS89_COORD_X'] = punt.x()
        df.loc[index,'QVISTA_ETRS89_COORD_Y'] = punt.y()
        df.loc[index,'INFERIT_DE_ZONA'] = 'Sí'
    return df

def main():
    args = get_args()
    with qgisapp(guienabled=False) as app:
        QvApp() # instanciem el singleton, per garantir que tingui la base de dades
        camps = [args.tipus_via, args.via, args.num_ini, args.lletra_ini, args.num_fin, args.lletra_fin]
        ruta = args.arxiu[0]
        mapificador = QvMapificacio(ruta)
            
        # el mapificador espera rebre una llista o una tupla, amb les zones. 
        # Si no ens indiquen zones, posem una tupla d'un únic element (coordenada)
        # Si ens n'indiquen una, posem una tupla amb dos elements (coordenada, element)
        # Si ens n'indiquen més, fem una tupla amb la coordenada i els paràmetres, aprofitant que podem "desempaquetar" la llista
        zones = args.zones
        if zones is None:
            zones = 'Coordenada', 
        elif isinstance(zones, str):
            zones = 'Coordenada', zones
        else:
            zones = 'Coordenada', *zones
        def obte_valors_camps(dic):
            # Obtenim una llista amb els 6 valors dels 6 camps
            # (posant string buit si el camp no hi és, ja que la funció get del dict permet un segon paràmetre, que és el valor per defecte)
            # Dividim el valor 1 per la última coma/espai, i posem això com a valor del número
            l = [dic.get(x, '') for x in camps]
            aux = rsplit(l[1], [',',' '], 1)
            # si no hi ha resultat al split, deixem el número buit
            if len(aux)==2:
                l[1:2] = aux
            return l
        func = obte_valors_camps if args.num_ini is None else None
        try:
            res = mapificador.geocodificacio(camps, zones, fCalcValorsAdreca=func)
        except Exception as e:
            print_error("S'ha produït una excepció durant la mapificació", repr(e))
        if not res:
            print_error(mapificador.msgError)
        sortida = args.sortida if args.sortida is not None else ruta.replace('.csv',' out.csv')
        df = pd.read_csv(mapificador.fZones, header=0, sep=';')
        
        modificat = False
        # df.loc localitza files a partir d'una llista d'etiquetes o de valors booleans
        # En aquest cas, obtenim quines són nul·les, i ens quedem només aquestes
        fallen = df.loc[df['QVISTA_ETRS89_COORD_X'].isnull() == True]
        # TRUC: None s'avalua com a fals. any([None, None, None, None]) serà fals, mentre que any([None, None, 'Nom districte', None]) serà True
        if args.extrapola_dades_zona:
            if len(fallen)>0:
                if any([args.nom_barri, args.codi_barri, args.nom_districte, args.codi_districte]):
                    df = extrapola_dades_zones(df, fallen, args)
                    df.to_csv(sortida, index=False, sep=';',float_format='%.3f')
                    modificat=True
                else:
                    print_avis('No heu indicat cap zona vàlida. No es podran extrapolar les zones')
        
        if not modificat:
            shutil.copyfile(mapificador.fZones,sortida)
        if len(fallen)>0:
            camps_sense_none = [camp for camp in camps if camp is not None]
            # camps_sense_none = list(filter(lambda x: x is not None, camps))
            print_avis('Han fallat les següents files:\n',fallen[camps_sense_none])
        print(f'Arxiu desat a {sortida}')



if __name__=='__main__':
    main()