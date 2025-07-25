import inspect
import os
import sys
import time
import unicodedata
from pathlib import Path

from qgis.core import (QgsGeometry, QgsLayerDefinition,
                       QgsMapRendererParallelJob, QgsMapSettings, QgsProject,
                       QgsVectorLayer)
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtWidgets import QDockWidget, QFileDialog, QMessageBox, qApp

import configuracioQvista
from moduls import QvApp
from moduls.QvConstants import QvConstants
from moduls.QvVideo import QvVideo

if sys.platform == 'win32':
    from moduls.QvFuncionsWin32 import *

def debugging():
    # True si se está ejecutando el programa en modo debug
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 12:
        return sys.monitoring.get_tool(sys.monitoring.DEBUGGER_ID) is not None
    else:
        return sys.gettrace() is not None

def getPythonPath():
    for p in os.environ.get('PYTHONPATH', '').split(os.pathsep):
        if p.split('\\')[-1] == 'python':
            return p
    return ''

def setDPI():
    from qgis.PyQt import QtCore
    from qgis.PyQt.QtWidgets import QApplication

    #setDPIScaling()
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1" #QT < 5.14
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1" #QT >= 5.14

    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.RoundPreferFloor)
    except AttributeError:
        # la versió de Qt que tenim encara no incorpora aquesta característica
        pass
    
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

def modeDebug():
    return QvApp.QvApp().paramCfg('Debug','False')=='True'

def printDebug(*args, **kwargs):
    """Funció equivalent al print, però que només imprimeix si qVista està en mode debug
    Es poden utilitzar tots els paràmetres del print, i funcionen exactament igual
    """
    if modeDebug():
        print(*args, **kwargs)

def eliminaAccents(txt):
    # https://stackoverflow.com/a/518232/19238937
   return ''.join(c for c in unicodedata.normalize('NFD', txt)
                  if unicodedata.category(c) != 'Mn')

def cronometra(func):
    """Funció decoradora que cronometra la funció passada com a paràmetre i imprimeix el temps per pantalla
    Aquesta funció està pensada per ser utilitzada per cronometraDebug i evitar ser invasiva amb prints

    Arguments:
        func {Callable} -- Funció que volem cronometrar
        
    Returns:
        Callable -- Una funció que internament executa func i retorna el mateix resultat, però imprimint per pantalla el temps requerit per executar-la
    """
    def embolcall(*args, **kwargs):
        t=time.process_time()
        t2 = time.time()
        res=func(*args, **kwargs)
        print(f'DEBUG: Temps de processador per executar {str(func)}: {time.process_time()-t}')
        print(f'DEBUG: Temps total per executar {str(func)}: {time.time()-t2}')
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
    if modeDebug():
        return cronometra(func)
    return func

# Una aproximació millor seria utilitzant metaclasses.
# El problema de les metaclasses és que és més difícil posar-les i treure-les, 
#  i això permet decorar la classe que veiem que és lenta i treure-li el decorador quan lcoalitzem el problema
def cronometraFuncionsLlargues(temps):
    """Equivalent al cronometraDebug, però pensat per decorar les funcions d'una classe
    Permet obtenir totes les funcions que triguen X segons o més en executar-se
    Està pensat per poder examinar quines són les funcions que triguen en un codi

    NOTA: si una funció és modal (espera una interacció de l'usuari per acabar) també poden aparèixer

        EXEMPLE:
        cronometraFuncionsLlargues(5)
        class Foo:
            def __init__(self):
                self.funcio_llarga()
            def funcio_llarga(self):
                time.sleep(10)
            def funcio_curta(self):
                print(':D')
        
        foo = Foo()
        foo.funcio_curta()

        RESULTAT:
            DEBUG: Temps de processador per executar Foo.funcio_llarga: 5.0001
            DEBUG: Temps total per executar Foo.funcio_llarga: 5.0005
            DEBUG: Temps de processador per executar Foo.__init__: 5.0002
            DEBUG: Temps total per executar Foo.__init__: 5.0006

    Args:
        temps (float): temps que han de superar o igualar les funcions per ser tingudes en compte
    """
    def decorador(f):
        def embolcall(*args, **kwargs):
            t=time.process_time()
            t2 = time.time()
            res=f(*args, **kwargs)
            t = time.process_time()-t
            t2 = time.time()-t2
            if t2>=temps:
                printDebug(f'DEBUG: Temps de processador per executar {str(f)}: {t}')
                printDebug(f'DEBUG: Temps total per executar {str(f)}: {t2}')
            return res
        return embolcall

    # inspirada en https://stackoverflow.com/a/6307868
    def decorate(cls):
        if QvApp.QvApp().paramCfg('Debug','False')=='True':
            # for attr in cls.__dict__:
            for attr, _ in inspect.getmembers(cls,inspect.isfunction):
                setattr(cls, attr, decorador(getattr(cls, attr)))
        return cls
    return decorate

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

def ignoraArgs(func):
    """Funció decoradora per ignorar els arguments que se li passen a una altra funció.
    És útil per quan per culpa dels decoradors se li passen paràmetres a una funció que no n'hauria de rebre
    És una "chapuza", però d'alguna manera s'havia de fer

    Arguments:
        func {Callable} -- Funció que no rep cap argument i volem que ignori els arguments
    """
    def embolcall(*args, **kwargs):
        func()
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
        assistent=None
        # En teoria no hauria de donar-se el cas, però si el separador inferit no és vàlid llença TypeError
        try:
            assistent=QvCarregaCsv(nfile, project, llegenda)
        except TypeError as e:
            print(e)
        except Exception as e:
            # Quan el carregador no pugui carregar un csv, informem
            msg = QMessageBox(QMessageBox.Warning,'Atenció', 'La càrrega de csv ha fallat. Si no sabeu per què, contacteu amb el vostre informàtic de referència i mostreu-li el següent missatge d\'error:',QMessageBox.Ok)
            msg.setInformativeText(f'{type(e).__name__}: {str(e)}')
            msg.exec()
            pass

        qApp.restoreOverrideCursor()
        if assistent is not None:
            assistent.show()

def startMovie():
    """Mostra un spinner de càrrega flotant

    Returns:
        QvVideo -- Spinner que s'està mostrant (important guardar-lo en algun lloc)
    """
    player = QvVideo(os.path.join(configuracioQvista.imatgesDir,"Spinner_2.gif"), 160, 160)
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

def escollirNivellQlr(llegenda):
    """Carrega una capa Qlr escollida amb el diàleg que s'obre

    Arguments:
        llegenda {QvLlegenda} -- Llegenda que estem fent servir
    """
    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer QLR", ".", "QLR (*.qlr)")

    if nfile:
        afegirQlr(nfile, llegenda)

def afegirQlr(nom, llegenda): 
    """Afegeix la capa del Qlr indicat

    Arguments:
        nom {str} -- Nom de l'arxiu que volem carregar
        llegenda {QvLlegenda} -- Llegenda que estem fent servir
    """
    #per raons que escapen al meu coneixement la funció loadLayerDefinition canvia el directori de treball
    #Com que no el volem canviar i a la funció li és igual, el que fem és desar-lo i tornar-lo a posar
    dir=os.getcwd()
    ok, txt = QgsLayerDefinition().loadLayerDefinition(nom, llegenda.project, llegenda.root)
    os.chdir(dir)

    msg = llegenda.msgErrorlayers()
    if msg:
        QMessageBox.warning(llegenda, "Capes amb errors", msg)


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
    for file in os.scandir(configuracioQvista.tempdir):
        try:
            #Si no podem esborrar un arxiu, doncs és igual. Deu estar obert. Ja s'esborrarà en algun moment
            os.unlink(file.path)
        except:
            pass

# Funcio per carregar problemes a GITHUB
def reportarProblema(titol: str, descripcio: str=None):
    if QvApp.QvApp().bugUser(titol, descripcio):
        print ('Creat el problema {0:s}'.format(titol))
        return True
    else:
        print ('Error al crear el problema {0:s}'.format(titol))
        return False

@cronometraDebug
def capturarImatge(geom: QgsGeometry, canvas: QgsMapCanvas, mida: QSize = None, nfile: str = None) -> Path:
    """Captura una imatge d'un canvas, garantint que contingui una geometria donada

    Args:
        geom (QgsGeometry): [description]
        canvas (QgsMapCanvas): [description]
        mida (QSize, optional): [description]. Defaults to None.
        nfile (str, optional): [description]. Defaults to None.

    Returns:
        Path: [description]
    """
    if nfile is None:
        nfile='render.png'
    if mida is None:
        # mida = QSize(geom.boundingBox().height(), geom.boundingBox().width())
        amplada = 1920 # L'amplada d'una pantalla FullHD
        alçada = amplada*geom.boundingBox().height()/geom.boundingBox().width()
        mida = QSize(amplada, alçada)
    else:
        print(geom.boundingBox().height(), geom.boundingBox().width())
    path = Path(configuracioQvista.tempdir, nfile).with_suffix('.png')

    # rotem la geometria
    geom.rotate(canvas.rotation(),geom.centroid().asPoint())

    options = QgsMapSettings()
    options.setLayers(canvas.layers())
    options.setDestinationCrs(QgsProject.instance().crs())
    # options.setBackgroundColor(QColor(255, 255, 255))
    options.setOutputSize(mida)
    options.setExtent(geom.boundingBox())
    options.setRotation(canvas.rotation())

    render = QgsMapRendererParallelJob(options)
    render.start()
    render.waitForFinished()
    img = render.renderedImage()
    img.save(str(path), "png")
    return path

class creaEina:
    """Cridable (callable) per decorar la declaració d'una subclasse de QWidget i crear un QDockWidget que el contingui.
    Està pensat per fer-se servir com un decorador, i passar-li com a paràmetre
    Exemple d'ús:

    @QvFuncions.creaEina(titol='Hola')
    class Hola(QDockWidget):
        ...
    
    Això farà que la classe Hola sigui una classe del tipus QDockWidget que contindrà el QWidget definit

    IMPORTANT: si executem el mòdul com a main, no es generarà el QDockWidget. Això és per permetre'ns tenir el QWidget amb un main d'exemple
    """
    def __init__(self,**kwargs):
        """Inicialitza el decorador amb els atributs que vulguem que tingui la classe

        def funcioExemple(self):
            print('Sóc un exemple')
            print('De debò, no faig res útil')
        @QvFuncions.creaEina('func1':funcioExemple, titol="Hola")
        class DockWidget(QWidget):
            ...


        Això serà equivalent al codi següent:
        class Widget(QWidget):
            ...
        class DockWidget(QDockWidget):
            titol = "Hola"
            def func1(self):
                print('Sóc un exemple')
                print('De debò, no faig res útil')

        """
        self.kwargs=kwargs

    def __call__(self,classeWidOrig):
        """Funció que rep un QWidget i crea una classe del tipus QDockWidget que el conté, pensat per crear entorns

        Args:
            classeWidOrig (type(QWidget)): Classe del widget que volem que contingui l'entorn

        Returns:
            type: Una subclasse de QDockWidget (no instanciada)
        """
        context = inspect.stack()[1]
        modul = inspect.getmodule(context[0])

        # Si ho hem invocat des del main, no generem el QDockWidget, sinó que retornem el propi QWidget
        if modul.__name__=='__main__':
            return classeWidOrig
        
        # Obtenim el nom que posarem a la classe
        try:
            nomClasse = Path(context.filename).stem
        except:
            # Per evitar que peti, si tot ha fallat, posarem un nom qualsevol
            nomClasse = 'EntornCustom'
        
        # Funció __init__ pel QDockWidget
        def init_classe(self,parent):
            titol = self.titol if hasattr(self,'titol') else nomClasse
            super(QDockWidget,self).__init__(titol,parent)
            self.wid = classeWidOrig(parent)
            self.setWidget(self.wid)
        def showEvent(self,event):
            super(QDockWidget,self).showEvent(event)
            # tot això no hauria de caldre, però no funcionava :(
            self.wid.show()
            if hasattr(self,'mida'): 
                self.setMinimumSize(self.midaMin)
                self.setMaximumSize(self.midaMax)
                self.resize(self.mida)
        def hideEvent(self,event):
            # Això tampoc hauria de caldre
            self.mida = self.size()
            self.midaMin = self.minimumSize()
            self.midaMax = self.maximumSize()
            super(QDockWidget,self).hideEvent(event)
        atributs = {'__init__':init_classe, 'showEvent':showEvent, 'hideEvent':hideEvent,**self.kwargs}

        # type permet construir una classe. 
        # Com a primer argument li passem el nom que tindrà aquesta (com a str)
        # Com a segon argument, una tupla amb les classes de les que hereta
        # Com a tercer argument, un diccionari amb els atributs de la classe.
        #  En el nostre cas, els atributs seran els que rebem com a arguments amb nom,
        #  més una funció __init__ pròpia, que és la creada a sobre.
        classe = type(nomClasse,(QDockWidget,), atributs)
        return classe
