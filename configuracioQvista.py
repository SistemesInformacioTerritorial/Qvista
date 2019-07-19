import os

#Parametres configuració inicial
versio="0.2"
titolFinestra = "qVista %s  Sistema d'Informació Territorial de Barcelona"%versio

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/Cataleg/Capes/"
carpetaCatalegProjectesLlista = "N:/9SITEB/Publicacions/qVista/Cataleg/Mapes/"
projecteInicial = 'mapesOffline/qVista default map.qgs'

estatConnexio = "Xarxa municipal: Connectat"

QvTempdir='C:/temp/qVista/'
tempdir=QvTempdir+'temp/'
docdir='n:/siteb/apl/pyqgis/qvista/dades/'
docdirPlantilles=docdir+'plantilles/'
arxiuAvis=docdir+'Avisos.htm'
arxiuNews=docdir+'Noticies.htm'
arxiuTmpAvis=tempdir+'ultimAvisObert'
arxiuTmpNews=tempdir+'ultimaNewOberta'
arxiuMapesRecents=tempdir+'mapesRecents'
carpetaDocuments=docdir+'Documentacio/'
arxiuInfoQVista=docdir+'InfoQVista.pdf'

if not os.path.exists(QvTempdir):
    try:
        os.mkdir(QvTempdir)
    except:
        print('ERROR. No he pogut crear el directori temporal '+QvTempdir)

if not os.path.exists(tempdir):
    try:
        os.mkdir(tempdir)
    except:
        print('ERROR. No he pogut crear el directori temporal '+tempdir)

if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    carpetaCatalegProjectesLlista = "../dades/CatalegProjectes/"
    projecteInicial = 'mapesOffline/qVista default map.qgs'
    estatConnexio = "Xarxa municipal: Desconnectat"

    