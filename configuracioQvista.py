import os
#Parametres configuració inicial
projecteInicial='n:/9siteb/publicacions/qvista/dades/projectes/bcn11_nord.qgs'

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/CatalegProjectes/"
if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    projecteInicial = 'mapesOffline/DistrictesMartorell.qgz'
carpetaCatalegOpenData="d:/dropbox/repsQV/qvista/CatalegOpenData"
titolFinestra = 'qVista 0.1'

