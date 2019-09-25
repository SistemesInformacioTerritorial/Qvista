from moduls.QvImports import * 
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty
from PyQt5 import QtCore, QtWidgets
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvVisorHTML import QvVisorHTML
import re

#Hi ha una classe que es diu QFileIconProvider que el que fa és retornar la icona corresponent
#Sobrecarregant la funció icon podem donar icones diferents
class ProveidorIcones(QFileIconProvider):
    '''Classe que serveix per proveir d'icones al QFileSystemModel
    Tenim les nostres icones, que són Material Design
    '''
    def icon(self,fileInfo):
        '''Retorna la icona de la carpeta si és un directori.
        Retorna la icona de la capa si és una capa'''
        if fileInfo.isDir():
            return QIcon('Imatges/cc_folder.png')
        elif fileInfo.completeSuffix()=='qlr':
            return QIcon('Imatges/cc_layer.png')
            pass
        return super().icon(fileInfo)


class DelegatNegreta(QStyledItemDelegate):
    '''Per donar estil al QFileSystemModel
    Si és un directori, el pinta de negreta
    Si no, fa el comportament per defecte
    '''
    def paint(self,painter,option,index):
        if self.parent().model.isDir(index):
            option.font.setWeight(QFont.Bold)
        super().paint(painter,option,index)


class ModelArxius(QFileSystemModel):
    '''Quan ens posem a cercar, no ens interessa mostrar les carpetes buides
    Fent una subclasse de QFileSystemModel podem comprovar quines carpetes quedarien buides cada vegada que actualitzem el filtre, i no mostrar-les
    '''
    def setNameFilters(self,filters):
        super().setNameFilters(filters)
        self.actualitzaFiltre()
        
    def actualitzaFiltre(self):
        '''Crea un set que es diu self.cosesAMostrar que conté totes les coses que mostrarem
        Coses que es mostraran:
        -Capa que passi el filtre
        -Directori que contingui quelcom que es mostrarà

        Per fer-ho, primer itera pels arxius que passen el filtre i els desa en un set
        Aleshores es recorre tots els directoris i, per cada un d'ells, comprova si té algun arxiu que pengi d'ell, desant-los en un set auxiliar

        '''
        self.cosesAMostrar=set()
        noSeSap=set()
        it=QDirIterator(self.rootDirectory(),QDirIterator.Subdirectories)
        while it.hasNext():
            it.next()
            fInfo=it.fileInfo()
            if fInfo.isFile():
                self.cosesAMostrar.add(fInfo.dir().path()) #Desem el path del directori del qual penja
            else:
                noSeSap.add(fInfo.filePath())
        dirsAMostrar=set()
        for x in noSeSap:
            #Si el directori està a self.cosesAMostrar, afegim també el seu pare (ja que el pare també el mostrarem)
            #Si no hi és, comprovem si hi ha algun arxiu que en pengi
            #La segona comprovació és una mica més costosa, però gairebé mai la farem
            if x in self.cosesAMostrar:
                self.cosesAMostrar.add(os.path.dirname(x))
            else:
                for y in self.cosesAMostrar:
                    if x in y:
                        dirsAMostrar.add(x)
                        break
        self.cosesAMostrar|=dirsAMostrar
    def data(self,index,role=Qt.DisplayRole):
        if self.isDir(index):
            if self.filePath(index) not in self.cosesAMostrar:
                #Si poses un QVariant buit et mostra una fila buida
                #Si poses qualsevol text, mostra buit però no sé per què
                return QVariant(':(')
        return super().data(index,role)

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
        self.leCercador=QLineEdit(self)
        self.leCercador.setStyleSheet('background: white')
        self.leCercador.setPlaceholderText('Cercar...')
        self.leCercador.textChanged.connect(self.canviaFiltre)
        self.accioEsborra=self.leCercador.addAction(QIcon('Imatges/cc_buidar_cercar.png'),QLineEdit.TrailingPosition)
        self.accioEsborra.triggered.connect(lambda: self.leCercador.setText(''))
        self.accioEsborra.setVisible(False)

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

        self.model=ModelArxius()
        self.model.setIconProvider(ProveidorIcones())
        self.model.setNameFilterDisables(False)
        # self.model.setNameFilters(['*.qlr'])
        self.model.setReadOnly(True)
        # self.model.selectionChanged.connect(self.actualitzaMetadades)
        rootPath=self.model.setRootPath(carpetaCataleg)
        # self.treeCataleg.setModel(self.model)
        self.treeCataleg.setModel(self.model)
        self.treeCataleg.selectionModel().selectionChanged.connect(self.actualitzaMetadades)
        self.treeCataleg.setRootIndex(rootPath)
        self.canviaFiltre()
        for i in range (1,4):
            self.treeCataleg.header().hideSection(i)

        self.preview=Preview(self)

        self.layout.addWidget(self.leCercador)
        self.layout.addWidget(self.treeCataleg)
        self.layout.addWidget(self.preview)

    def arreglaText(self,txt):
        trans=str.maketrans('ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöü·ºª.',
                            'AEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOU.   ')
        txt=txt.translate(trans)
        # txt=txt.upper()
        txt=txt.strip(' ')
        txt=re.sub('\s[\s]+',' ',txt)
        return txt

    def canviaFiltre(self):
        txt=self.leCercador.text()
        if txt=='':
            self.accioEsborra.setVisible(False)
        else:
            self.accioEsborra.setVisible(True)

        txt=self.arreglaText(txt)
        self.model.setNameFilters(['*%s*.qlr'%txt])


    def afegirQlr(self):
        '''Si és una capa, l'afegeix a qVista
        He copiat el codi del mòdul qVista.py perquè la funció estava fora de la classe qVista i no podia cridar-la
        '''
        index = self.treeCataleg.currentIndex()
        if self.model.isDir(index): return
        path=self.model.fileInfo(index).absoluteFilePath()
        # self.qV.afegirQlr(path)

        #Copio el codi de la funció afegirQlr de l'arxiu qVista.py, ja que no se m'acudeix cap manera de cridar-la des d'aquí que no sigui barroera
        # layers = QgsLayerDefinition.loadLayerDefinitionLayers(path)
        # self.qV.project.addMapLayers(layers, True)

        ok, txt = QgsLayerDefinition().loadLayerDefinition(path, self.qV.project, self.qV.llegenda.root)
        if ok:
            self.qV.canvisPendents=True
            self.qV.botoDesarProjecte.setIcon(self.qV.iconaAmbCanvisPendents)
        else:
            print('No se pudo importar capas', txt)


        # self.qV.canvisPendents=True
        # self.qV.botoDesarProjecte.setIcon(self.qV.iconaAmbCanvisPendents)

    def actualitzaMetadades(self):
        '''Pinta la preview de la capa
        '''
        index = self.treeCataleg.currentIndex()
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