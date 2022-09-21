import os

from qgis.core import QgsProject
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import Qt, pyqtSignal, pyqtSlot
from qgis.PyQt.QtWidgets import QActionGroup, QComboBox, QMenu

import configuracioQvista
from moduls.QvCanvas import QvCanvas
from moduls.QvConstants import QvConstants


class QvCanvasAuxiliar(QvCanvas):


    Sig_canviTema = pyqtSignal('QString','QString')    #JNB

    def __init__(self, canvas, *args, temaInicial = None, sincronitzaExtensio=False, sincronitzaZoom=False, sincronitzaCentre=True, sincronitzaRotacio=True, volemCombo=True, **kwargs):
        """Canvas auxiliar, pensat per afegir funcionalitats al QvCanvas.

        Permet rebre tots els arguments que rebi QvCanvas, més uns quants extra

        Args:
            canvas (QgsMapCanvas): Canvas principal
            temaInicial (str, optional): Nom del tema inicial, si n'hi ha. Defaults to None
            sincronitzaExtensio (bool, optional): [description]. Defaults to True.
            sincronitzaZoom (bool, optional): [description]. Defaults to False.
            sincronitzaCentre (bool, optional): [description]. Defaults to False.
            sincronitzaRotacio (bool, optional): [description]. Defaults to True.
            volemCombo (bool, optional): Indica si volem que hi hagi una combobox per canviar de tema. Defaults to True
        """
        super().__init__(*args, **kwargs)
        self.canvas = canvas

        self.sincronitzaExtensio = sincronitzaExtensio
        self.sincronitzaZoom = sincronitzaZoom
        self.sincronitzaCentre = sincronitzaCentre
        self.sincronitzaRotacio = sincronitzaRotacio
        self.botons()
        self.currentTeme = ''   #JNB
        self.setExtent(self.canvas.extent())
        self.refresh()


        if volemCombo:
            self.preparaCbTemes(temaInicial)
        self.setupSincronia()
    


    def preparaCbTemes(self, temaInicial):
        self.temes = QgsProject.instance().mapThemeCollection().mapThemes()
        if len(self.temes)>0:
            self.cbTemes = QComboBox()
            self.cbTemes.addItem('Sense tema')
            self.cbTemes.addItems(self.temes)
            self.cbTemes.currentIndexChanged.connect(self.canviTema)
            self.layoutBotoneraMapa.insertWidget(0,self.cbTemes)

            if temaInicial in self.temes:
                self.cbTemes.setCurrentIndex(self.temes.index(temaInicial)+1)
    def botons(self):
        self.bSincronia = self._botoMapa(os.path.join(configuracioQvista.imatgesDir,'sync.png'))
        self.bSincronia.setToolTip('Sincronia amb el mapa principal')
        self.layoutBotoneraMapa.insertWidget(0,self.bSincronia)
        self.bSincronia.setCursor(QvConstants.cursorFletxa()) 
        self.bSincronia.setCheckable(False)

        # Definició del menú desplegable
        menuBoto = QMenu(':D')
        grup = QActionGroup(menuBoto)
        self.actNoSinc = menuBoto.addAction('Sense sincronia')
        self.actSincExt = menuBoto.addAction('Sincronitza extensió')
        self.actSincZoom = menuBoto.addAction('Sincronitza zoom')
        self.actSincCentre = menuBoto.addAction('Sincronitza centre')
        menuBoto.addSeparator()
        self.actSincRotacio = menuBoto.addAction('Sincronitza rotació')
        


        grup.addAction(self.actNoSinc)
        grup.addAction(self.actSincExt)
        grup.addAction(self.actSincZoom)
        grup.addAction(self.actSincCentre)

                
        # no afegim self.actSincRotacio perquè volem que la rotació sigui independent

        self.actNoSinc.setCheckable(True)
        self.actNoSinc.setChecked(True)

        self.actSincExt.setCheckable(True)
        self.actSincExt.setChecked(self.sincronitzaExtensio)
        
        self.actSincZoom.setCheckable(True)
        self.actSincZoom.setChecked(self.sincronitzaZoom)
        
        self.actSincCentre.setCheckable(True)
        self.actSincCentre.setChecked(self.sincronitzaCentre)
        # self.actSincCentre.setChecked(True)     #JNB
        
        self.actSincRotacio.setCheckable(True)
        self.actSincRotacio.setChecked(self.sincronitzaRotacio)

        self.actNoSinc.triggered.connect(self.swapSincronies)
        self.actSincExt.triggered.connect(self.swapSincronies)
        self.actSincZoom.triggered.connect(self.swapSincronies)
        self.actSincCentre.triggered.connect(self.swapSincronies)
        self.actSincRotacio.triggered.connect(self.swapSincroniaRotacio)

        self.bSincronia.setMenu(menuBoto)


    def canviTema(self, i):
        if i==0:
            self.setTheme('')
            elTema = 'Sense Tema'
        else:
            self.setTheme(self.temes[i-1])
            elTema = self.temes[i-1]

       





        self.currentTeme = elTema
        elIdCanvas = str(id(self))
        try:
            self.Sig_canviTema.emit(elIdCanvas, elTema)
        except Exception as ee:
            pass
            
            
    def sincronitzaExtensio(self, canv: QgsMapCanvas):
        """Sincronitza els paràmetre implícit amb el canvas passat com a paràmetre

        Args:
            canv (QgsMapCanvas): [description]
        """
        def sync():
            canv.setExtent(self.extent())
            canv.refresh()
        canv.extentsChanged.connect(sync)
    
    def setupSincronia(self):
        self.canvas.extentsChanged.connect(self.syncExtensio)
        self.canvas.scaleChanged.connect(self.syncZoom)
        self.canvas.extentsChanged.connect(self.syncCentre)
        self.canvas.rotationChanged.connect(self.syncRotacio)

        self.extentsChanged.connect(self.syncExtensioOut)
        self.scaleChanged.connect(self.syncZoomOut)
        self.extentsChanged.connect(self.syncCentreOut)
    
    def syncExtensio(self):
        if self.sincronitzaExtensio and not self.underMouse():
            self.setExtent(self.canvas.extent())
            self.refresh()
    def syncZoom(self):
        if self.sincronitzaZoom and not self.underMouse():
            centre = self.center()
            self.setExtent(self.canvas.extent())
            self.setCenter(centre)
            self.refresh()
    def syncCentre(self):
        if self.sincronitzaCentre and not self.underMouse():
            self.setCenter(self.canvas.center())
            self.refresh()
    
    # Els moviments de la rodeta a vegades es fan sense tenir el focus en el canvas. Per si de cas, fem servir underMouse i no focus
    def syncExtensioOut(self):
        if self.sincronitzaExtensio and self.underMouse():
            self.canvas.setExtent(self.extent())
            self.canvas.refresh()
    def syncZoomOut(self):
        if self.sincronitzaZoom and self.underMouse():
            centre = self.canvas.center()
            self.canvas.setExtent(self.extent())
            self.canvas.setCenter(centre)
            self.canvas.refresh()
    def syncCentreOut(self):
        if self.sincronitzaCentre and self.underMouse():
            self.canvas.setCenter(self.center())
            self.canvas.refresh()
    def syncRotacio(self):
        if self.sincronitzaRotacio:
            self.setRotation(self.canvas.rotation())

    def swapSincronies(self):
        self.swapSincroniaExtensio(self.actSincExt.isChecked())
        self.swapSincroniaZoom(self.actSincZoom.isChecked())
        self.swapSincroniaCentre(self.actSincCentre.isChecked())
    def swapSincroniaExtensio(self,check):
        self.sincronitzaExtensio = check
        self.syncExtensio()
    def swapSincroniaZoom(self,check):
        self.sincronitzaZoom = check
        self.syncZoom()
    def swapSincroniaCentre(self,check):
        self.sincronitzaCentre = check
        self.syncCentre()
    def swapSincroniaRotacio(self,check):
        self.sincronitzaRotacio = check
        self.syncRotacio()