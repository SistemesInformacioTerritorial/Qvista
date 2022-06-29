
import argparse
import math
from qgis.core import QgsVectorLayer
from qgis.core.contextmanagers import qgisapp
import sys
import os
from moduls.QvMapificacio import QvMapificacio, PANDAS_ENABLED
if PANDAS_ENABLED:
    import pandas as pd
from moduls.QvApp import QvApp


def get_args():
    parser = argparse.ArgumentParser(description='Geocodifica un arxiu csv, afegint-li camps de coordenades ETRS89 al final')
    # afegir l'adreça del csv
    parser.add_argument('arxiu',help="Ruta de l'arxiu a geocodificar", type=str, nargs=1)
    parser.add_argument('--sortida',help="Ruta on volem l'arxiu de sortida. Si no s'indica, sortirà en un directori per defecte", default=None)
    parser.add_argument('--tipus-via',help="Camp on tenim el tipus de via de l'adreça, si en tenim", default=None)
    parser.add_argument('--via',help="Camp on tenim la via de l'adreça, si en tenim", default="Nom_via")
    parser.add_argument('--num',help="Camp on tenim el número de l'adreça, si en tenim", default="Numero_via")
    parser.add_argument('--nom-barri',help="Camp on tenim el nom del barri, si en tenim", default="Barri")
    parser.add_argument('--nom-districte',help="Camp on tenim el nom del districte, si en tenim", default="Districte")
    parser.add_argument('--codi-barri', help="Camp on tenim el codi del barri, si en tenim", default=None)
    parser.add_argument('--codi-districte', help="Camp on tenim el codi del districte, si en tenim", default=None)

    return parser.parse_args()

def adapta_nom(nom):
    """Adapta un nom de manera que no hi hagi confusions per diferents formes d'escriure
    Converteix el nom en minúscula, elimina els espais, cometes simples i cometes dobles, així com els accents

    Args:
        nom (str): [description]
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

def main():
    args = get_args()
    # args.arxiu = 'C:/Users/omarti/Documents/Random/CATB_retallat_prova.csv'
    print(args)
    with qgisapp(guienabled=False) as app:
        QvApp() # instanciem el singleton, per garantir que tingui la base de dades
        # if not os.path.isfile(args.arxiu):
        #     print(f"ERROR! No existeix l'arxiu {args.arxiu}")
        #     sys.exit(1)
        mapificador = QvMapificacio(args.arxiu[0])
        camps = args.tipus_via, args.via, args.num
        # el mapificador espera rebre una llista o una tupla, amb les zones. 
        # Per tant, posant la coma, zones serà una tupla amb un únic element
        zones = 'Coordenada',
        try:
            res = mapificador.geocodificacio(camps, zones)
        except Exception as e:
            print(e)
        if not res:
            print('ERROR de mapificació:',mapificador.msgError)
            pass
        if args.nom_barri is not None or args.nom_districte is not None or args.codi_barri is not None or args.codi_districte is not None:
            if PANDAS_ENABLED:
                try:
                    df = pd.read_csv(mapificador.fZones, header=0, sep=';')
                except Exception as e:
                    print(e)
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
                for (index, row) in df.iterrows():
                    if math.isnan(row['QVISTA_ETRS89_COORD_X']):
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
                sortida = args.sortida if args.sortida is not None else args.arxiu.replace('.csv',' out.csv')
                df.to_csv(sortida, index=False, sep=';')
                print(f'Arxiu desat a {sortida}')
            else:
                print("ERROR. No s'ha pogut accedir al mòdul pandas")



if __name__=='__main__':
    main()