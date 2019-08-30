from moduls.QvImports import * 
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty
from PyQt5 import QtCore, QtWidgets
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvVisorHTML import QvVisorHTML

class QvCatalegCapes(QWidget):
    def __init__(self,qV,parent=None):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.layout=QVBoxLayout()
        self.setFont(QvConstants.FONTTEXT)
        self.setStyleSheet('color: %s; background: %s; border: none'%(QvConstants.COLORFOSCHTML,QvConstants.COLORBLANCHTML))
        # self.layout.setContentsMargins(10,10,10,10)
        self.qV=qV
        self.setLayout(self.layout)

        #Afegir el cercador

        self.treeCataleg=QTreeView() #posar-li alçada mínima de 400
        self.treeCataleg.setFixedSize(300,400)
        self.layout.addWidget(self.treeCataleg)
        self.model=QFileSystemModel()
        rootPath=self.model.setRootPath(carpetaCataleg)

        self.treeCataleg.doubleClicked.connect(self.afegirQlr)
        self.treeCataleg.clicked.connect(self.actualitzaMetadades)
        self.model.setNameFilters(['*.qlr'])
        self.model.setNameFilterDisables(False)
        self.treeCataleg.setModel(self.model)
        self.treeCataleg.setRootIndex(rootPath)
        for i in range (1,4):
            self.treeCataleg.header().hideSection(i)
        self.model.setHeaderData(0,Qt.Horizontal,'hola')
        self.treeCataleg.setIndentation(20)
        self.treeCataleg.setSortingEnabled(False)
        self.treeCataleg.setWindowTitle("Catàleg d'Informació Territorial")
        self.treeCataleg.adjustSize()
        self.treeCataleg.setHeaderHidden(True)

        self.preview=Preview(self)
        self.layout.addWidget(self.preview)



    def afegirQlr(self):
        index = self.treeCataleg.currentIndex()
        path=self.model.fileInfo(index).absoluteFilePath()
        # self.qV.afegirQlr(path)

        #Copio el codi de la funció afegirQlr de l'arxiu qVista.py, ja que no se m'acudeix cap manera de cridar-la des d'aquí que no sigui barroera
        layers = QgsLayerDefinition.loadLayerDefinitionLayers(path)
        self.qV.project.addMapLayers(layers, True)
        self.qV.canvisPendents=True
        self.qV.botoDesarProjecte.setIcon(self.qV.iconaAmbCanvisPendents)
    def actualitzaMetadades(self):
        index = self.treeCataleg.currentIndex()
        # print('Index: ', index)
        # nom=self.model.fileInfo(index).baseName()
        path=self.model.fileInfo(index).absoluteFilePath()
        if os.path.isfile(path):
            self.preview.setCapa(path)
        pass

class Preview(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.layout=QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.widgetPreview=QWidget()
        self.layout.addWidget(self.widgetPreview)
    def setCapa(self,capa):
        self.layout.removeWidget(self.widgetPreview)
        self.widgetPreview=PreviewCapa(capa,self)
        self.layout.addWidget(self.widgetPreview)
        #Cal afegir el widget al layout???

class PreviewCapa(QWidget):
    def __init__(self,capa,parent=None):
        super().__init__(parent)
        self.setStyleSheet('border: none')
        self.layout=QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setFixedWidth(300)
        self.setLayout(self.layout)
        # self.setFixedSize(300,180)
        self.nomBase=capa[:-4]

        self.imatge=QPixmap(self.nomBase+'.png')
        self.lblImatge=QLabel()
        self.lblImatge.setPixmap(self.imatge)
        self.layout.addWidget(self.lblImatge)
        try:
            with open(self.nomBase+'.txt') as arxiu:
                self.titol=arxiu.readline()
                self.text=arxiu.read()
        except:
            self.titol="Títol no disponible"
            self.text="Text no disponible"
        self.lblText=QLabel('<p><strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 10pt;">%s<br /></span></strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 8pt;">%s</span></p>'%(self.titol,self.text))
        self.layout.addWidget(self.lblText)