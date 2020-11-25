from moduls.QvImports import *
from moduls.QvCanvasAuxiliar import QvCanvasAuxiliar
from moduls.QvPushButton import QvPushButton
from qgis.PyQt.QtGui import QFont, QDesktopServices

class IntegracioPatrimoni(QDockWidget):
    def __init__(self, parent):
        self.parent = parent
        self.parent.canvas.renderComplete.connect(self.centraCanvas)
        super().__init__("Patrimoni")
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        
        fPatrimoni = QFrame()
        lytPatrimoni = QVBoxLayout(fPatrimoni)
        lytPatrimoni.setAlignment(Qt.AlignTop)

        fPatrimoni.setLayout(lytPatrimoni)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)
        lTema1 = QLabel('1.- Visions patrimonials')
        lTema1.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setBold(True)
        lTema1.setFont(f)
        fPatrimoni.layout().addWidget(lTema1)
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding,QSizePolicy.Maximum)
        fPatrimoni.layout().addItem(spacer)

        bBIPE = QvPushButton('BIPE ',flat=False)
        bBIPE.setStyleSheet("Text-align: left")

        # bBIPE.clicked.connect(lambda : self.temaBIPE('BIPE'))
        bBIPE.clicked.connect(lambda : self.canvas.setTheme('BIPE'))

        bBIPS = QvPushButton('BIPS ',flat=False)
        bBIPS.setStyleSheet("Text-align: left")

        bBIPS.clicked.connect(lambda : self.canvas.setTheme('BIPS'))

        bBILS = QvPushButton('BILS ',flat=False)
        bBILS.setStyleSheet("Text-align: left")

        bBILS.clicked.connect(lambda : self.canvas.setTheme('BILS'))

        
        bCessio = QvPushButton('Cessió',flat=False)
        bCessio.setStyleSheet("Text-align: left")

        bCessio.clicked.connect(lambda : self.canvas.setTheme('Cessió'))


        fPatrimoni.layout().addWidget(bBIPE)
        fPatrimoni.layout().addWidget(bBIPS)
        fPatrimoni.layout().addWidget(bBILS)
        fPatrimoni.layout().addWidget(bCessio)
        
        fPatrimoni.layout().addItem(spacer)
        
        bCentra = QvPushButton('Centra',flat=True)
        bCentra.setStyleSheet("Text-align: left")

        bCentra.clicked.connect(self.centraCanvas)
        fPatrimoni.layout().addWidget(bCentra)

        fPatrimoni.layout().addItem(spacer)

        self.canvas = QvCanvasAuxiliar(self.parent.canvas)        
        # project = QgsProject.instance()
        # root = QgsProject.instance().layerTreeRoot()
        self.canvas.setTheme('BIPE')

        # QgsLayerTreeMapCanvasBridge(root, self.canvas)

        fPatrimoni.layout().addWidget(self.canvas)
 
        self.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.setWidget(fPatrimoni)
        self.setContentsMargins ( 0, 0, 0, 0 )
        self.show()

    def centraCanvas(self):
        self.canvas.setExtent(self.parent.canvas.extent())
        self.canvas.refresh()

    def canviTema(self, tema):
        print(tema)
        self.canvas.setTheme(tema)
        # self.canvas.refresh()
