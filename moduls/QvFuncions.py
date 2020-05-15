import os
import sys
import time
import inspect
from moduls.QvVideo import QvVideo
from moduls.QvImports import *
from moduls.QvConstants import QvConstants
import moduls.QvApp

if sys.platform == 'win32':
    from moduls.QvFuncionsWin32 import *

def setDPI():
    from qgis.PyQt import QtCore
    from qgis.PyQt.QtWidgets import QApplication
    
    setDPIScaling()
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

def cronometra(func):
    """Funció decoradora que cronometra la funció passada com a paràmetre i imprimeix el temps per pantalla
    Aquesta funció està pensada per ser utilitzada per cronometraDebug i evitar ser invasiva amb prints

    Arguments:
        func {Callable} -- Funció que volem cronometrar
        
    Returns:
        Callable -- Una funció que internament executa func i retorna el mateix resultat, però imprimint per pantalla el temps requerit per executar-la
    """
    def embolcall(*args, **kwargs):
        t=time.time()
        res=func(*args, **kwargs)
        print(f'DEBUG: Temps per executar {str(func)}: {time.time()-t}')
        return res
    return embolcall

def cronometraDebug(func):
    """Funció decoradora pensada per ajudar-nos en el debug.
    Si estem en mode debug retorna la funció func decorada perquè imprimeixi per pantalla el temps requerit per executar-la.
    Si no estem en mode debug, retorna la pròpia funció

    Exemple d'us:

    @cronometraDebug
    def funcio_molt_lenta(...):
        ...

    Arguments:
        func {Callable} -- La funció que volem que sigui cronometrada si estem en mode debug

    Returns:
        Callable -- Una funció que internament executa func i retorna el mateix resultat. Si el mode debug està desactivat, no fa res més. Si està activat, imprimeix per pantalla el temps requerit per executar-la
    """
    if moduls.QvApp.QvApp().paramCfg('Debug','False')=='True':
        return cronometra(func)
    return func

def mostraSpinner(func):
    """Funció decoradora que mostra un spinner de càrrega mentre l'executa

    Arguments:
        func {Callable} -- Funció que volem executar mostrant el spinner

    Returns:
        Callable -- Una funció que internament executa func i retorna el mateix resultat, però mostrant un spinner durant l'execució
    """
    def embolcall(*args, **kwargs):
        player = startMovie()
        res=func(*args, **kwargs)
        stopMovie(player)
        return res
    return embolcall

def createFolder(directory):
    """Crea la carpeta al directori indicat

    Arguments:
        directory {str} -- Directori que volem crear
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)

@mostraSpinner
def carregarLayerCSV(nfile, project, llegenda):
    """Carrega una capa des d'un csv. Obre un diàleg per triar com el carreguem

    Arguments:
        nfile {str} -- Ruta de l'arxiu a carregar
        project {QgsMapProject} -- Projecte amb el que estem treballant
        llegenda {QvLlegenda} -- Llegenda que estem fent servir
    """
    from moduls.QvCSV import QvCarregaCsv
    if nfile: 
        qApp.setOverrideCursor(Qt.WaitCursor)

        assistent=QvCarregaCsv(nfile, project, llegenda)

        qApp.restoreOverrideCursor()
        assistent.show()

def startMovie():
    """Mostra un spinner de càrrega flotant

    Returns:
        QvVideo -- Spinner que s'està mostrant (important guardar-lo en algun lloc)
    """
    player = QvVideo(os.path.join(imatgesDir,"Spinner_2.gif"), 160, 160)
    QvConstants.afegeixOmbraWidget(player)
    player.setModal(True)
    player.activateWindow()
    player.mediaPlayer.play()
    player.show()
    return player

def stopMovie(player):
    """Oculta el spinner de càrrega

    Arguments:
        player {QvVideo} -- Spinner que volem ocultar
    """
    player.hide()
    player.mediaPlayer.pause()

def escollirNivellQlr(projecte, llegenda):
    """Carrega una capa Qlr escollida amb el diàleg que s'obre

    Arguments:
        project {QgsMapProject} -- Projecte amb el que estem treballant
        llegenda {QvLlegenda} -- Llegenda que estem fent servir
    """
    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer QLR", ".", "QLR (*.qlr)")

    if nfile:
        afegirQlr(nfile)

def afegirQlr(nom, project, llegenda): 
    """Afegeix la capa del Qlr indicat

    Arguments:
        nom {str} -- Nom de l'arxiu que volem carregar
        project {QgsMapProject} -- Projecte amb el que estem treballant
        llegenda {QvLlegenda} -- Llegenda que estem fent servir
    """
    #per raons que escapen al meu coneixement la funció loadLayerDefinition canvia el directori de treball
    #Com que no el volem canviar i a la funció li és igual, el que fem és desar-lo i tornar-lo a posar
    dir=os.getcwd()

    ok, txt = QgsLayerDefinition().loadLayerDefinition(nom, project, llegenda.root)
    os.chdir(dir)

def afegirNivellSHP(project):
    """Afegeix capa SHP triant-la des del

    Arguments:
        project {QgsMapProject} -- Projecte amb el que estem treballant
    """
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

# Funcio per carregar problemes a GITHUB
def reportarProblema(titol: str, descripcio: str=None):
    if moduls.QvApp.QvApp().bugUser(titol, descripcio):
        print ('Creat el problema {0:s}'.format(titol))
        return True
    else:
        print ('Error al crear el problema {0:s}'.format(titol))
        return False
