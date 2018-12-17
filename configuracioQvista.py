import os

#Parametres configuració inicial

titolFinestra = 'qVista 0.1'

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/Cataleg/Projectes/"
projecteInicial='n:/9siteb/publicacions/qvista/dades/projectes/bcn11_nord.qgs'

estatConnexio = "Xarxa corporativa: OK"

if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    projecteInicial = 'mapesOffline/DistrictesMartorell.qgz'
    estatConnexio = "Xarxa corporativa: Desconnectat"

    