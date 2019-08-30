import os

#Parametres configuració inicial
versio="0.4"
titolFinestra = "qVista %s  Sistema d'Informació Territorial de Barcelona"%versio

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/Cataleg/Capes/"
carpetaCatalegProjectesLlista = ["N:/9SITEB/Publicacions/qVista/Cataleg/Mapes publics/","N:/9SITEB/Publicacions/qVista/Cataleg/Mapes privats/"]
projecteInicial = 'mapesOffline/qVista default map.qgs'

estatConnexio = "Xarxa municipal: Connectat"

QvTempdir='C:/temp/qVista/'
tempdir=QvTempdir+'temp/' #Seran els arxius temporals de qVista que no s'han de guardar entre execucions
dadesdir=QvTempdir+'dades/' #Arxius temporals que volem conservar, amb configuracions i similars

docdir='n:/siteb/apl/pyqgis/qvista/dades/'
docdirPlantilles=docdir+'plantilles/'

arxiuAvis=docdir+'Avisos.htm'
arxiuNews=docdir+'Noticies.htm'
carpetaDocuments=docdir+'Documentacio/'
arxiuInfoQVista=docdir+'InfoQVista.pdf'

arxiuTmpAvis=dadesdir+'ultimAvisObert'
arxiuTmpNews=dadesdir+'ultimaNewOberta'
arxiuMapesRecents=dadesdir+'mapesRecents'


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

if not os.path.exists(dadesdir):
    try:
        os.mkdir(dadesdir)
    except:
        print('ERROR. No he pogut crear el directori temporal '+dadesdir)

if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    carpetaCatalegProjectesLlista = "../dades/CatalegProjectes/"
    projecteInicial = 'mapesOffline/qVista default map.qgs'
    estatConnexio = "Xarxa municipal: Desconnectat"

    