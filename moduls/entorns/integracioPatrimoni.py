from moduls.QvImports import *
from moduls.QvCanvas import QvCanvas
from moduls.QvPushButton import QvPushButton
from qgis.PyQt.QtGui import QFont, QDesktopServices

class IntegracioPatrimoni(QDockWidget):
    def __init__(self, parent):
        self.parent = parent
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

        bBIPE = QvPushButton('BIPE ',flat=True)
        bBIPE.setStyleSheet("Text-align: left")

        # bBIPE.clicked.connect(lambda : self.temaBIPE('BIPE'))
        bBIPE.clicked.connect(lambda : self.canvas.setTheme('BIPE'))

        bBIPS = QvPushButton('BIPS ',flat=True)
        bBIPS.setStyleSheet("Text-align: left")

        bBIPS.clicked.connect(lambda : self.canvas.setTheme('BIPS'))

        bBILS = QvPushButton('BILS ',flat=True)
        bBILS.setStyleSheet("Text-align: left")

        bBILS.clicked.connect(lambda : self.canvas.setTheme('BILS'))

        
        bCessio = QvPushButton('Cessió',flat=True)
        bCessio.setStyleSheet("Text-align: left")

        bCessio.clicked.connect(lambda : self.canvas.setTheme('Cessió'))


        fPatrimoni.layout().addWidget(bBIPE)
        fPatrimoni.layout().addWidget(bBIPS)
        fPatrimoni.layout().addWidget(bBIPE)
        fPatrimoni.layout().addWidget(bBIPS)
        
        fPatrimoni.layout().addItem(spacer)

        self.canvas = QvCanvas()        
        project = QgsProject.instance()
        root = QgsProject.instance().layerTreeRoot()
        self.canvas.setTheme('BIPE')

        QgsLayerTreeMapCanvasBridge(root, self.canvas)

        fPatrimoni.layout().addWidget(self.canvas)
 
        self.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.setWidget(fPatrimoni)
        self.setContentsMargins ( 0, 0, 0, 0 )
        self.show()

    def canviTema(self, tema):
        print(tema)
        # self.parent.project.mapThemeCollection().applyTheme(tema, self.parent.root, self.parent.llegenda.layerTreeModel())
        self.canvas.setTheme(tema)
        # self.canvas.refresh()
  
    def temaBIPS(self):
        print('BIPS') 
        self.parent.project.mapThemeCollection().applyTheme('Tema 2', self.parent.root, self.parent.llegenda.layerTreeModel())
        self.canvas.setTheme('Tema 2')
        self.canvas.refresh()
   