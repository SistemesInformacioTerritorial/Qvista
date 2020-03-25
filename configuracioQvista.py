import os
from pathlib import Path

#Parametres configuració inicial
versio="0.7"
titolFinestra = "qVista %s  Sistema d'Informació Territorial de Barcelona"%versio

carpetaCataleg = "N:/9SITEB/Publicacions/qVista/Cataleg/Capes/"
#Definim per separat els directoris de projectes públics i privats, de manera que puguem comprovar en qualsevol moment si un directori és de projectes públics o privats
carpetaCatalegProjectesPublics=["N:/9SITEB/Publicacions/qVista/Cataleg/Mapes publics/"]
carpetaCatalegProjectesPrivats=['L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/']
carpetaCatalegProjectesLlista = [*carpetaCatalegProjectesPublics,*carpetaCatalegProjectesPrivats]
projecteInicial = os.path.abspath('mapesOffline/qVista default map.qgs')

estatConnexio = "Xarxa municipal: Connectat"

QvTempdir='C:/temp/qVista/'
tempdir=os.path.join(QvTempdir,'temp/')+'/' #Seran els arxius temporals de qVista que no s'han de guardar entre execucions
dadesdir=os.path.join(QvTempdir,'dades/')+'/' #Arxius temporals que volem conservar
configdir=os.path.join(QvTempdir+'config/')+'/' #Configuracions i coses

docdir='n:/siteb/apl/pyqgis/qvista/dades/'
imatgesDir = os.path.abspath('Imatges/')+'/'
docdirPlantilles=os.path.join(docdir,'plantilles/')

arxiuAvis=os.path.join(docdir,'Avisos.htm')
arxiuNews=os.path.join(docdir,'Noticies.htm')
carpetaDocuments=os.path.join(docdir,'Documentacio/')
arxiuInfoQVista=os.path.join(docdir,'InfoQVista.pdf')






#Per defecte desarem els arxius al directori home de l'usuari, si no ens indica una altra cosa
# Un cop desi un arxiu, qVista recordarà el directori on l'ha desat i intentarà desar el següent allà
# try:
#     pathDesarPerDefecte=str(Path.home().resolve())
# except:
#     pathDesarPerDefecte='.'


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
if not os.path.exists(configdir):
    try:
        os.mkdir(configdir)
    except:
        print('ERROR. No he pogut crear el directori temporal '+configdir)

if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"
    carpetaCatalegProjectesLlista = ["../dades/CatalegProjectes/"]
    estatConnexio = "Xarxa municipal: Desconnectat"

    