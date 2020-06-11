from moduls.QvImports import *
from moduls.QvCanvas import QvCanvas
from moduls.QvConstants import QvConstants

class QvCanvasAuxiliar(QvCanvas):
    def __init__(self, canvas, *args, temaInicial = None, sincronitzaExtensio=False, sincronitzaZoom=False, sincronitzaCentre=False, **kwargs):
        """Canvas auxiliar, pensat per afegir funcionalitats al QvCanvas.

        Permet rebre tots els arguments que rebi QvCanvas, més uns quants extra

        Args:
            canvas (QgsMapCanvas): Canvas principal
            temaInicial (str, optional): Nom del tema inicial, si n'hi ha. Defaults to None
            sincronitzaExtensio (bool, optional): [description]. Defaults to False.
            sincronitzaZoom (bool, optional): [description]. Defaults to False.
        """
        super().__init__(*args, **kwargs)
        self.canvas = canvas
        self.sincronitzaExtensio = sincronitzaExtensio
        self.sincronitzaZoom = sincronitzaZoom
        self.sincronitzaCentre = sincronitzaCentre
        self.preparaCbTemes(temaInicial)
        self.botons()
        self.setupSincronia()
    
    def preparaCbTemes(self, temaInicial):
        self.temes = QgsProject.instance().mapThemeCollection().mapThemes()
        if len(self.temes)>0:
            self.cbTemes = QComboBox()
            self.cbTemes.addItem('Tema per defecte')
            self.cbTemes.addItems(self.temes)
            self.cbTemes.currentIndexChanged.connect(self.canviTema)
            self.layoutBotoneraMapa.insertWidget(0,self.cbTemes)

            if temaInicial in self.temes:
                self.cbTemes.setCurrentIndex(self.temes.index(temaInicial)+1)
    
    def botons(self):
        self.bSincronia = self._botoMapa(os.path.join(imatgesDir,'sync.png'))
        self.bSincronia.setToolTip('Pantalla completa (F11)')
        self.layoutBotoneraMapa.insertWidget(1,self.bSincronia)
        self.bSincronia.setCursor(QvConstants.cursorFletxa()) 
        self.bSincronia.setCheckable(False)

        # Definició del menú desplegable
        menuBoto = QMenu(':D')
        actSincExt = menuBoto.addAction('Sincronitza extensió')
        actSincZoom = menuBoto.addAction('Sincronitza zoom')
        actSincCentre = menuBoto.addAction('Sincronitza centre')

        actSincExt.setCheckable(True)
        actSincExt.setChecked(False)
        actSincZoom.setCheckable(True)
        actSincZoom.setChecked(False)
        actSincCentre.setCheckable(True)
        actSincCentre.setChecked(False)

        actSincExt.triggered.connect(self.swapSincroniaExtensio)
        actSincZoom.triggered.connect(self.swapSincroniaZoom)
        actSincCentre.triggered.connect(self.swapSincroniaCentre)

        self.bSincronia.setMenu(menuBoto)

    def canviTema(self, i):
        if i==0:
            self.setTheme('')
        else:
            self.setTheme(self.temes[i-1])
            
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
    
    def syncExtensio(self):
        if self.sincronitzaExtensio:
            self.setExtent(self.canvas.extent())
    def syncZoom(self):
        if self.sincronitzaZoom:
            escala=self.canvas.scale()
            self.zoomScale(int(self.canvas.scale()))
    def syncCentre(self):
        if self.sincronitzaCentre:
            self.setCenter(self.canvas.center())
    
    def swapSincroniaExtensio(self,check):
        self.sincronitzaExtensio = check
    
    def swapSincroniaZoom(self,check):
        self.sincronitzaZoom = check
    
    def swapSincroniaCentre(self,check):
        self.sincronitzaCentre = check