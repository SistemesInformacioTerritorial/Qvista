import os
from configuracioQvista import *
from moduls.QvVideo import QvVideo
from moduls.QvConstants import QvConstants
from moduls.QvImports import *
from moduls.QvCSV import QvCarregaCsv

player=None # l'agafem com a global

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

def carregarLayerCSV(nfile, project, llegenda):
    if nfile: 
        startMovie()
        qApp.setOverrideCursor(Qt.WaitCursor)

        assistent=QvCarregaCsv(nfile,project, llegenda)

        qApp.restoreOverrideCursor()
        stopMovie()
        assistent.show()

def startMovie():
    global player
    player = QvVideo(os.path.join(imatgesDir,"Spinner_2.gif"), 160, 160)
    QvConstants.afegeixOmbraWidget(player)
    player.setModal(True)
    player.activateWindow()
    player.mediaPlayer.play()
    player.show()

def stopMovie():
    player.hide()
    player.mediaPlayer.pause()

def escollirNivellQlr():
    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer QLR", ".", "QLR (*.qlr)")

    if nfile:
        afegirQlr(nfile)

def afegirQlr(nom, project, llegenda): 
    #per raons que escapen al meu coneixement la funció loadLayerDefinition canvia el directori de treball
    #Com que no el volem canviar i a la funció li és igual, el que fem és desar-lo i tornar-lo a posar
    dir=os.getcwd()

    ok, txt = QgsLayerDefinition().loadLayerDefinition(nom, project, llegenda.root)
    os.chdir(dir)

def afegirNivellSHP(project):
    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir SHP", ".", "Fitxers Shape (*.shp)")
    layer = QgsVectorLayer(nfile, os.path.basename(nfile), "ogr")
    if not layer.isValid():
        return
    project.addMapLayer(layer)

def esborraCarpetaTemporal():
    '''Esborra el contingut de la carpeta temporal en iniciar qVista
    '''
    #Esborrarem el contingut de la carpeta temporal
    for file in os.scandir(tempdir):
        try:
            #Si no podem esborrar un arxiu, doncs és igual. Deu estar obert. Ja s'esborrarà en algun moment
            os.unlink(file.path)
        except:
            pass