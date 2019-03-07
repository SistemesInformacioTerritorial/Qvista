import os

#Parametres configuració inicial

titolFinestra = "qVista 0.1  Sistema d'Informació Territorial de Barcelona"

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/Cataleg/Capes/"
carpetaCatalegProjectesLlista = "N:/9SITEB/Publicacions/qVista/Cataleg/Mapes/"
projecteInicial = 'mapesOffline/Districtes.qgz'

estatConnexio = "Xarxa municipal: Connectat"

if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    carpetaCatalegProjectesLlista = "../dades/CatalegProjectes/"
    projecteInicial = 'mapesOffline/Districtes.qgz'
    estatConnexio = "Xarxa municipal: Desconnectat"

    