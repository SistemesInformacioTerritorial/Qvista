from moduls.QvImports import * 
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty
from PyQt5 import QtCore, QtWidgets
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvVisorHTML import QvVisorHTML

#Hi ha una classe que es diu QFileIconProvider que el que fa és retornar la icona corresponent
#Sobrecarregant la funció icon podem donar icones diferents
class ProveidorIcones(QFileIconProvider):
    def icon(self,fileInfo):
        if fileInfo.isDir():
            return QIcon('Imatges/cc_folder.png')
        elif fileInfo.completeSuffix()=='qlr':
            return QIcon('Imatges/cc_layer.png')
            pass
        return super().icon(fileInfo)


class DelegatNegreta(QStyledItemDelegate):
    def paint(self,painter,option,index):
        if self.parent().model.isDir(index):
            option.font.setWeight(QFont.Bold)
        super().paint(painter,option,index)


class QvCatalegCapes(QWidget):
    def __init__(self,qV,parent=None):
        '''Construeix el catàleg de capes
        Li passem qVista com a paràmetre, per poder carregar les capes des d'aquí
        '''
        super().__init__()
        # self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
        self.setCursor(QvConstants.cursorClick())
        self.setMinimumHeight(500)
        self.layout=QVBoxLayout()
        self.setFont(QvConstants.FONTTEXT)
        self.setStyleSheet('color: %s; background: %s; border: none'%(QvConstants.COLORFOSCHTML,QvConstants.COLORBLANCHTML))
        self.qV=qV
        self.setLayout(self.layout)

        #Afegir el cercador

        self.treeCataleg=QTreeView()
        self.treeCataleg.setFixedWidth(300)
        self.treeCataleg.setDragEnabled(True) #Per poder arrosegar
        # self.treeCataleg.doubleClicked.connect(self.afegirQlr)
        self.treeCataleg.activated.connect(self.afegirQlr)
        self.treeCataleg.clicked.connect(self.actualitzaMetadades)
        self.treeCataleg.setItemDelegate(DelegatNegreta(self))
        self.treeCataleg.setIndentation(20)
        self.treeCataleg.setSortingEnabled(False)
        self.treeCataleg.setWindowTitle("Catàleg d'Informació Territorial")
        self.treeCataleg.adjustSize()
        self.treeCataleg.setHeaderHidden(True)

        self.model=QFileSystemModel()
        self.model.setIconProvider(ProveidorIcones())
        self.model.setNameFilters(['*.qlr'])
        self.model.setNameFilterDisables(False)
        self.model.setReadOnly(True)
        # self.model.selectionChanged.connect(self.actualitzaMetadades)
        rootPath=self.model.setRootPath(carpetaCataleg)
        self.treeCataleg.setModel(self.model)
        self.treeCataleg.selectionModel().selectionChanged.connect(self.actualitzaMetadades)
        self.treeCataleg.setRootIndex(rootPath)
        for i in range (1,4):
            self.treeCataleg.header().hideSection(i)

        self.preview=Preview(self)

        self.layout.addWidget(self.treeCataleg)
        self.layout.addWidget(self.preview)



    def afegirQlr(self):
        '''Si és una capa, l'afegeix a qVista
        He copiat el codi del mòdul qVista.py perquè la funció estava fora de la classe qVista i no podia cridar-la
        '''
        index = self.treeCataleg.currentIndex()
        if self.model.isDir(index): return
        path=self.model.fileInfo(index).absoluteFilePath()
        # self.qV.afegirQlr(path)

        #Copio el codi de la funció afegirQlr de l'arxiu qVista.py, ja que no se m'acudeix cap manera de cridar-la des d'aquí que no sigui barroera
        layers = QgsLayerDefinition.loadLayerDefinitionLayers(path)
        self.qV.project.addMapLayers(layers, True)
        self.qV.canvisPendents=True
        self.qV.botoDesarProjecte.setIcon(self.qV.iconaAmbCanvisPendents)
    def actualitzaMetadades(self):
        '''Pinta la preview de la capa
        '''
        index = self.treeCataleg.currentIndex()
        # print('Index: ', index)
        # nom=self.model.fileInfo(index).baseName()
        path=self.model.fileInfo(index).absoluteFilePath()
        if os.path.isfile(path):
            self.preview.setCapa(path)
        else:
            self.preview.setCapa(None)
    # def keyPressEvent(self,event):
    #     if event.key()==Qt.Key_Up or event.key()==Qt.Key_Down():
    #         self.actualitzaMetadades()

class Preview(QWidget):
    '''Classe que gestiona la preview que es mostra.
    S'ocupa de que si ja se'n mostrava alguna, s'oculti abans de mostrar la nova
    Bàsicament conté un layout amb un únic widget a dins. El widget de dins és la preview que estem mostrant
    '''
    def __init__(self,parent=None):
        super().__init__()
        self.layout=QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.widgetPreview=QWidget()
        self.layout.addWidget(self.widgetPreview)
    def setCapa(self,capa):
        self.widgetPreview.hide()
        self.layout.removeWidget(self.widgetPreview)
        if capa is None:
            self.widgetPreview=QWidget()
        else:
            self.widgetPreview=PreviewCapa(capa,self)
        self.layout.addWidget(self.widgetPreview)
        self.update() #Crec que no cal
        #Cal afegir el widget al layout???

class PreviewCapa(QWidget):
    '''La preview concreta que mostrem
    Bàsicament conté una imatge i el text
    La imatge ha de tenir el mateix nom que la capa amb extensió png
    El títol surt d'un arxiu de text amb el mateix nom. Ha de contenir una primera línia amb el títol, i la resta amb el text
    '''
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
        self.lblText.setWordWrap(True)
        self.layout.addWidget(self.lblText)