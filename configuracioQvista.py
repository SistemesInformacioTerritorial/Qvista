import os

#Parametres configuració inicial
versio="0.1"
titolFinestra = versio+"qVista %s  Sistema d'Informació Territorial de Barcelona"%versio

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/Cataleg/Capes/"
carpetaCatalegProjectesLlista = "N:/9SITEB/Publicacions/qVista/Cataleg/Mapes/"
projecteInicial = 'mapesOffline/Districtes.qgs'

estatConnexio = "Xarxa municipal: Connectat"

tempdir='C:/temp/qVista/temp/'
docdir='L:/DADES/SIT/Doc/QVISTA/'
arxiuAvis=docdir+'Avisos.htm'
arxiuNews=docdir+'Noticies.htm'
arxiuTmpAvis=tempdir+'ultimAvisObert'
arxiuTmpNews=tempdir+'ultimaNewOberta'

if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    carpetaCatalegProjectesLlista = "../dades/CatalegProjectes/"
    projecteInicial = 'mapesOffline/Districtes.qgs'
    estatConnexio = "Xarxa municipal: Desconnectat"

    