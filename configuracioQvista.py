import os

#Parametres configuració inicial
versio="0.2"
titolFinestra = versio+"qVista %s  Sistema d'Informació Territorial de Barcelona"%versio

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/Cataleg/Capes/"
carpetaCatalegProjectesLlista = "N:/9SITEB/Publicacions/qVista/Cataleg/Mapes/"
projecteInicial = 'mapesOffline/qVista default map.qgs'

estatConnexio = "Xarxa municipal: Connectat"

tempdir='C:/temp/qVista/temp/'
docdir='n:/siteb/apl/pyqgis/qvista/dades/'
arxiuAvis=docdir+'Avisos.htm'
arxiuNews=docdir+'Noticies.htm'
arxiuTmpAvis=tempdir+'ultimAvisObert'
arxiuTmpNews=tempdir+'ultimaNewOberta'

if not os.path.exists(tempdir):
    try:
        os.mkdir(tempdir)
    except:
        print('ERROR. No he pogut crear el directori temporal')

if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    carpetaCatalegProjectesLlista = "../dades/CatalegProjectes/"
    projecteInicial = 'mapesOffline/qVista default map.qgs'
    estatConnexio = "Xarxa municipal: Desconnectat"

    