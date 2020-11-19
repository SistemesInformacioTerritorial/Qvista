
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
    parser.add_argument('--tipus-via',help="Camp on tenim el tipus de via de l'adreça", default=None)
    # parser.add_argument('--via',help="Camp on tenim la via de l'adreça", default=None)
    parser.add_argument('--via',help="Camp on tenim la via de l'adreça", default="Nom_via")
    # parser.add_argument('--num',help="Camp on tenim el número de l'adreça", default=None)
    parser.add_argument('--num',help="Camp on tenim el número de l'adreça", default="Numero_via")
    parser.add_argument('--barri',help="Camp on tenim el nom del barri", default="Barri")
    parser.add_argument('--districte',help="Camp on tenim el nom del districte", default="Districte")

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
        if not hasattr(args,'arxiu'):
            print("ERROR! No s'ha indicat arxiu a geocodificar")
            sys.exit(1)
        mapificador = QvMapificacio(args.arxiu[0])
        camps = args.tipus_via, args.via, args.num
        zones = 'Coordenada', 'Districte', 'Barri'
        print('Comencem mapificació')
        try:
            res = mapificador.geocodificacio(camps, zones)
        except Exception as e:
            print(e)
        print('Acabem mapificació')
        if not res:
            #Error
            pass
        print('Anem a comprovar si hi ha barri o districte')
        if args.barri is not None or args.districte is not None:
            print('Anem a mirar si tenim el pandas')
            if PANDAS_ENABLED:
                print('Tenim el pandas')
                try:
                    df = pd.read_csv(mapificador.fZones, header=0, sep=';')
                except Exception as e:
                    print(e)
                pathZones = 'dades/Zones.gpkg'
                print('PATH DE ZONES:',os.path.abspath(pathZones))
                pathBarris = pathZones+'|layername=barris'
                layerBarris = QgsVectorLayer(pathBarris, 'ogr')
                pathDistrictes = pathZones+'|layername=districtes'
                layerDistrictes = QgsVectorLayer(pathDistrictes, 'ogr')
                barris = {}
                for rowB in layerBarris.getFeatures():
                    atributs = rowB.attributes()
                    # num_barri = atributs[1]
                    nom_barri = adapta_nom(atributs[2])
                    # num_districte = atributs[3]
                    centre = rowB.geometry().centroid().asPoint()

                    barris[nom_barri] = centre
                
                districtes = {}
                for rowD in layerDistrictes.getFeatures():
                    atributs = rowD.attributes()
                    nom_districte = adapta_nom(atributs[2])
                    centre = rowB.geometry().centroid().asPoint()
                    districtes[nom_districte]=centre
                for (index, row) in df.iterrows():
                    if math.isnan(row['QVISTA_ETRS89_COORD_X']):
                        # obtenir a partir del barri o del districte
                        fet = False
                        if args.barri is not None:
                            try:
                                punt = barris[adapta_nom(row[args.barri])]
                                df.loc[index,'QVISTA_ETRS89_COORD_X'] = punt.x()
                                df.loc[index,'QVISTA_ETRS89_COORD_Y'] = punt.y()
                                fet = True
                            except KeyError as e:
                                # No s'ha pogut reconèixer el barri
                                pass
                        if not fet and args.districte is not None:
                            try:
                                punt = districtes[adapta_nom(row[args.districte])]
                                df.loc[index,'QVISTA_ETRS89_COORD_X'] = punt.x()
                                df.loc[index,'QVISTA_ETRS89_COORD_Y'] = punt.y()
                                fet = True
                            except KeyError as e:
                                # No s'ha pogut reconèixer el districte
                                pass
                df.to_csv(mapificador.fZones, index=False, sep=';')
            else:
                print("ERROR. No s'ha pogut accedir al mòdul pandas")



if __name__=='__main__':
    main()