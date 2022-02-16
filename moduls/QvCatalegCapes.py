from moduls.QvImports import * 
from moduls.QvConstants import QvConstants
from moduls.QvVisorHTML import QvVisorHTML
from moduls.QvMemoria import QvMemoria
from moduls.QvPushButton import QvPushButton
from moduls import QvFuncions
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
            return QIcon(os.path.join(imatgesDir,'cc_folder.png'))
        elif fileInfo.completeSuffix()=='qlr':
            return QIcon(os.path.join(imatgesDir,'cc_layer.png'))
        return super().icon(fileInfo)


class DelegatNegreta(QStyledItemDelegate):
    '''Per donar estil al QFileSystemModel
    Si és un directori, el pinta de negreta
    Si no, fa el comportament per defecte
    '''
    def paint(self,painter,option,index):
        if self.parent().treeCataleg.model().isDir(index):
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
    afegirCapa = pyqtSignal(str)
    def __init__(self,parent=None):
        '''Construeix el catàleg de capes
        Li passem qVista com a paràmetre, per poder carregar les capes des d'aquí
        '''
        super().__init__()
        self.setCursor(QvConstants.cursorClick())
        self.setMinimumHeight(500)
        self.layout=QVBoxLayout()
        self.setFont(QvConstants.FONTTEXT)
        self.setStyleSheet('color: %s; background: %s; border: none'%(QvConstants.COLORFOSCHTML,QvConstants.COLORBLANCHTML))
        self.setLayout(self.layout)

        #Afegir el cercador
        self.leCercador=QLineEdit(self)
        self.leCercador.setStyleSheet('background: white')
        self.leCercador.setPlaceholderText('Cercar...')
        self.leCercador.textChanged.connect(self.canviaFiltre)
        self.accioEsborra=self.leCercador.addAction(QIcon(os.path.join(imatgesDir,'cc_buidar_cercar.png')),QLineEdit.TrailingPosition)
        self.accioEsborra.triggered.connect(lambda: self.leCercador.setText(''))
        self.accioEsborra.setVisible(False)

        self.treeCataleg=QTreeView()
        self.treeCataleg.setDragEnabled(True) #Per poder arrosegar
        self.treeCataleg.activated.connect(self.afegirQlr)
        self.treeCataleg.clicked.connect(self.actualitzaMetadades)
        self.treeCataleg.setItemDelegate(DelegatNegreta(self))
        self.treeCataleg.setIndentation(20)
        self.treeCataleg.setSortingEnabled(False)
        self.treeCataleg.setWindowTitle("Catàleg d'Informació Territorial")
        self.treeCataleg.adjustSize()
        self.treeCataleg.setHeaderHidden(True)
        self.treeCataleg.setStyleSheet('background: transparent')

        paths = [x for x in carpetaCatalegLlista if os.path.isdir(x)]
        self.models = []
        self.rootPaths = []
        for x in paths:
            self.models.append(ModelArxius())
            self.models[-1].setIconProvider(ProveidorIcones())
            self.rootPaths.append(self.models[-1].setRootPath(x))
            self.models[-1].setNameFilterDisables(False)
            self.models[-1].setNameFilters(['*.qlr'])
            self.models[-1].setReadOnly(True)
        # try:
        #     # Aquesta classe existeix a partir de Qt 5.13. La idea és que quan s'actualitzi a aquesta versió, funcionarà. 
        #     self.model = QConcatenateTablesProxyModel()
        #     for mod in self.models:
        #         self.model.addSourceModel(mod)
        #     self.treeCataleg.setModel(self.model)
        # except:
        #     # Estem en una versió de Qt menor de la 5.13. Farem servir una combobox per variar entre els diferents QTreeView
        if len(paths)>1:
            def canviModel(i):
                self.treeCataleg.setModel(self.models[i])
                self.treeCataleg.setRootIndex(self.rootPaths[i])
                self.canviaFiltre()
                self.models[i].layoutChanged.emit()
            cbModel = QComboBox()
            cbModel.addItems(map(os.path.basename, paths))
            cbModel.currentIndexChanged.connect(canviModel)
            self.layout.addWidget(cbModel)
        self.treeCataleg.setModel(self.models[0])
        
        self.treeCataleg.selectionModel().selectionChanged.connect(self.actualitzaMetadades)
        self.treeCataleg.setRootIndex(self.rootPaths[0])
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
        txt=txt.strip(' ')
        txt=re.sub(r'\s[\s]+',' ',txt)
        return txt

    def canviaFiltre(self):
        txt=self.leCercador.text()
        if txt=='':
            self.accioEsborra.setVisible(False)
        else:
            self.accioEsborra.setVisible(True)

        txt=self.arreglaText(txt)
        for mod in self.models:
            mod.setNameFilters(['*%s*.qlr'%txt])

    def afegirQlr(self):
        '''Si és una capa, l'afegeix a qVista
        He copiat el codi del mòdul qVista.py perquè la funció estava fora de la classe qVista i no podia cridar-la
        '''
        index = self.treeCataleg.currentIndex()
        model = self.treeCataleg.model()
        if model.isDir(index): return
        path = model.fileInfo(index).absoluteFilePath()
        self.afegirCapa.emit(path)

    def actualitzaMetadades(self):
        '''Pinta la preview de la capa
        '''
        index = self.treeCataleg.currentIndex()
        path=self.treeCataleg.model().fileInfo(index).absoluteFilePath()
        if os.path.isfile(path):
            self.preview.setCapa(path)
        else:
            self.preview.setCapa(None)

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
        self.setMinimumWidth(300)
        self.setLayout(self.layout)
        self.nomBase=capa[:-4]

        self.imatge=QPixmap(self.nomBase+'.png')
        self.lblImatge=QLabel()
        self.lblImatge.setPixmap(self.imatge)
        self.layout.addWidget(self.lblImatge)

        stylesheet='''
            QPushButton{
                background: rgba(255,255,255,0.66); 
                margin: 0px; 
                padding: 0px;
                border: 0px;
            }
        '''
        self.bAfegir=QPushButton(parent=self.lblImatge)
        self.bAfegir.setIcon(QIcon(os.path.join(imatgesDir,'cc_afegir.png')))
        self.bAfegir.setFixedSize(24,24)
        self.bAfegir.setIconSize(QSize(24,24))
        self.bAfegir.move(270,120)
        self.bAfegir.clicked.connect(self.obrir)
        self.bAfegir.setStyleSheet(stylesheet)
        self.bInfo=QPushButton(parent=self.lblImatge)
        self.bInfo.setIcon(QIcon(os.path.join(imatgesDir,'cm_info.png')))
        self.bInfo.setFixedSize(24,24)
        self.bInfo.setIconSize(QSize(24,24))
        self.bInfo.move(270,150)
        self.bInfo.clicked.connect(self.obrirInfo)
        self.bInfo.setStyleSheet(stylesheet)
        try:
            with open(self.nomBase+'.txt', encoding='cp1252') as arxiu:
                self.titol=arxiu.readline()
                self.text=arxiu.read()
        except:
            self.titol="Títol no disponible"
            self.text="Text no disponible"
        self.lblText=QLabel('<p><strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 10pt;">%s<br /></span></strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 8pt;">%s</span></p>'%(self.titol,self.text))
        self.lblText.setWordWrap(True)
        self.lblText.setStyleSheet('background: transparent')
        self.layout.addWidget(self.lblText)
    def mouseDoubleClickEvent(self,event):
        super().mouseDoubleClickEvent(event)
        self.obrir()
    def obrir(self):
        self.parentWidget().parentWidget().afegirQlr()
        self.bInfo.setIcon(QIcon(os.path.join(imatgesDir,'cm_info.png')))
    def obrirInfo(self):
        visor=QvVisorHTML(self.nomBase+'.htm','Metadades capa',True,self)
        visor.show()
    def showEvent(self,event):
        super().showEvent(event)
        self.bAfegir.show()
        self.bInfo.show()

# Plantilla on posarem les metadades del projecte, escrites per l'usuari
plantillaMetadades = '''<html>
<head>
<meta http-equiv=Content-Type content="text/html; charset=windows-1252">
<meta name=Generator content="Microsoft Word 14 (filtered)">
<style>
<!--
 /* Font Definitions */
 @font-face
	{font-family:Calibri;
	panose-1:2 15 5 2 2 2 4 3 2 4;}
 /* Style Definitions */
 p.MsoNormal, li.MsoNormal, div.MsoNormal
	{margin-top:0cm;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:0cm;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
a:link, span.MsoHyperlink
	{font-family:"Times New Roman","serif";
	color:blue;
	text-decoration:underline;}
a:visited, span.MsoHyperlinkFollowed
	{color:purple;
	text-decoration:underline;}
p.MsoListParagraph, li.MsoListParagraph, div.MsoListParagraph
	{margin-top:0cm;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:36.0pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msolistparagraphcxspfirst, li.msolistparagraphcxspfirst, div.msolistparagraphcxspfirst
	{mso-style-name:msolistparagraphcxspfirst;
	margin-top:0cm;
	margin-right:0cm;
	margin-bottom:0cm;
	margin-left:36.0pt;
	margin-bottom:.0001pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msolistparagraphcxspmiddle, li.msolistparagraphcxspmiddle, div.msolistparagraphcxspmiddle
	{mso-style-name:msolistparagraphcxspmiddle;
	margin-top:0cm;
	margin-right:0cm;
	margin-bottom:0cm;
	margin-left:36.0pt;
	margin-bottom:.0001pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msolistparagraphcxsplast, li.msolistparagraphcxsplast, div.msolistparagraphcxsplast
	{mso-style-name:msolistparagraphcxsplast;
	margin-top:0cm;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:36.0pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msochpdefault, li.msochpdefault, div.msochpdefault
	{mso-style-name:msochpdefault;
	margin-right:0cm;
	margin-left:0cm;
	font-size:12.0pt;
	font-family:"Calibri","sans-serif";}
p.msopapdefault, li.msopapdefault, div.msopapdefault
	{mso-style-name:msopapdefault;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:0cm;
	line-height:115%%;
	font-size:12.0pt;
	font-family:"Times New Roman","serif";}
.MsoChpDefault
	{font-size:10.0pt;
	font-family:"Calibri","sans-serif";}
.MsoPapDefault
	{margin-bottom:10.0pt;
	line-height:115%%;}
@page WordSection1
	{size:595.3pt 841.9pt;
	margin:70.85pt 3.0cm 70.85pt 3.0cm;}
div.WordSection1
	{page:WordSection1;}
-->
</style>

</head>

<body lang=CA link=blue vlink=purple>

<div class=WordSection1>

<p class=MsoNormal><b><span style='font-family:"Arial","sans-serif";color:#595959'>%s</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Format</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Resum</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Escales de visibilitat</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s </span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Contingut</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s </span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Propietari</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s </span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

</div>

</body>

</html>'''

class QvCreadorCatalegCapes(QDialog):
    def __init__(self,capes,canvas,project,cataleg=None,parent=None):
        super().__init__(parent)
        self.setWindowTitle('Afegir capa al catàleg')
        self._capes = capes
        self._project = project
        self._canvas = canvas
        self._canvas.xyCoordinates.connect(self._mouMouse)
        self._tool = PointTool(self,self._canvas)
        self._tool.click.connect(self.puntClick)
        self._toolSet = False
        self.incX = 300
        self.incY = 180
        self._layer = QgsVectorLayer(
            'Point?crs=epsg:25831', "Capa temporal d'impressió", "memory")
        project.addMapLayer(self._layer, False)

        self._lay = QVBoxLayout()
        self.setLayout(self._lay)
        lblCapcalera = QLabel('Afegir capa al catàleg')
        lblCapcalera.setFont(QvConstants.FONTTITOLS)
        self._lay.addWidget(lblCapcalera)

        layTitCat = QVBoxLayout()
        frameTitCat = self.getFrame(layTitCat)
        self._lay.addWidget(frameTitCat)

        layTitol = QHBoxLayout()
        layTitCat.addLayout(layTitol)
        layTitol.addWidget(QLabel('Títol: ', self))
        self._leTitol = QLineEdit(self)
        self._leTitol.textChanged.connect(self.actualitzaEstatBDesar)
        self._leTitol.setPlaceholderText(
            'Títol que es visualitzarà al catàleg')
        layTitol.addWidget(self._leTitol)

        lblText = QLabel('Descripció:')
        layTitCat.addWidget(lblText)
        self._teText = QTextEdit(self)
        self._teText.setPlaceholderText(
            'Descripció del projecte que es visualitzarà al catàleg.\nIntenteu no sobrepassar els 150 caràcters, ja que el text es podria veure tallat')
        self._teText.textChanged.connect(self.actualitzaEstatBDesar)
        layTitCat.addWidget(self._teText)

        self._layImatge = QVBoxLayout()
        frameImatge = self.getFrame(self._layImatge)
        self._layImatge.addWidget(QLabel('Vista prèvia escollida:'))
        self._imatge = QWidget()
        self._imatge.setFixedSize(self.incX, self.incY)
        self._layImatge.addWidget(self._imatge)
        self._lay.addWidget(frameImatge)

        # layCat = QVBoxLayout()
        # frameCat = self.getFrame(layCat)
        # self._lay.addWidget(frameCat)
        # lblCatalegs = QLabel('Trieu el catàleg on desarem el resultat')
        # self._cbCatalegs = QComboBox()
        # self._cbCatalegs.addItems(QvMemoria().getCatalegsLocals())
        # self._cbCatalegs.addItem('Un altre catàleg')
        # self._cbCatalegs.activated.connect(self._cbCatalegsCanviat)
        # layCat.addWidget(lblCatalegs)
        # layCat.addWidget(self._cbCatalegs)

        # lblSubcarpeta = QLabel('Trieu la categoria on desarem el resultat')
        # self._cbSubcarpetes = QComboBox()
        # self._cbSubcarpetes.currentIndexChanged.connect(
        #     self._cbSubCarpetesCanviat)
        # self._leNovaCat = QLineEdit()
        # self._populaSubCarpetes()
        # self._leNovaCat.setPlaceholderText('Nom de la nova categoria')
        # self._leNovaCat.textChanged.connect(self.actualitzaEstatBDesar)
        # layCat.addWidget(lblSubcarpeta)
        # layCat.addWidget(self._cbSubcarpetes)
        # layCat.addWidget(self._leNovaCat)
        # self._cbSubCarpetesCanviat(0)

        layBotons = QHBoxLayout()
        self._bGenerarImatge = QvPushButton('Capturar vista prèvia')
        self._bGenerarImatge.clicked.connect(self._swapCapturar)
        self._bDesar = QvPushButton('Desar', destacat=True)
        self._bDesar.clicked.connect(self._desar)
        layBotons.addWidget(self._bGenerarImatge)
        layBotons.addWidget(self._bDesar)
        self._lay.addLayout(layBotons)

        self._rubberband = QgsRubberBand(self._canvas)
        self._rubberband.setColor(QvConstants.COLORDESTACAT)
        self._rubberband.setWidth(2)
        self.pintarRectangle(self._canvas.extent())
        self._rubberband.hide()

        self.actualitzaEstatBDesar()
    def _mouMouse(self, p):
        if not self.isVisible() or not self._toolSet:
            self._rubberband.hide()
        else:
            p = self._canvas.mapFromGlobal(QCursor.pos())
            points = [QgsPoint(self._canvas.getCoordinateTransform().toMapCoordinates(*x)) for x in ((p.x()+self.incX, p.y(
            )+self.incY), (p.x()+self.incX, p.y()), (p.x(), p.y()), (p.x(), p.y()+self.incY), (p.x()+self.incX, p.y()+self.incY))]
            self._requadre = QgsGeometry.fromPolyline(points)
            self._rubberband.setToGeometry(self._requadre, self._layer)
            self._rubberband.show()
    def puntClick(self, p):
        self._p = p
        self.imprimirPlanol(
            p.x(), p.y(), self._canvas.scale(), self._canvas.rotation())
    def getFrame(self, l):
        f = QFrame(self)
        f.setLayout(l)
        f.setFrameStyle(QFrame.Box)
        return f
    def actualitzaEstatBDesar(self):
        b = isinstance(self._imatge, QLabel) and self._leTitol.text(
        ) != '' and self._teText.toPlainText() != ''
        if not b:
            self._bDesar.setEnabled(False)
            return

        # if self._cbSubcarpetes.currentIndex() < self._cbSubcarpetes.count()-1:
        #     self._bDesar.setEnabled(True)
        # else:
        #     self._bDesar.setEnabled(self._leNovaCat.text() != '')

        self._bDesar.setEnabled(True)
    def pintarRectangle(self, poligon):
        points = [QgsPointXY(0, 0), QgsPointXY(0, 10), QgsPointXY(
            10, 10), QgsPointXY(0, 10), QgsPointXY(0, 0)]
        poligono = QgsGeometry.fromRect(poligon)
        self._rubberband.setToGeometry(poligono, self._layer)
    def _swapCapturar(self):
        if self._toolSet:
            self._bGenerarImatge.setText('Capturar imatge')
            self._canvas.unsetMapTool(self._tool)
        else:
            self._bGenerarImatge.setText('Desplaçar mapa')
            self._canvas.setMapTool(self._tool)
        self._toolSet = not self._toolSet
    def _desar(self):
        ret, _ = QFileDialog.getSaveFileName(None,"Guardar capa catàleg", carpetaCatalegLocal, "Capes de QGIS (*.qlr)")
        fRes = ret.replace('.qlr','')

        # Comprovem si existeix l'arxiu de text. Si existeix, assumim que tenim tot el projecte, i retornem
        if os.path.isfile(fRes+'.txt'):
            r = QMessageBox.question(self, 'Aquest projecte ja existeix',
                                     'Aquest projecte ja existeix. Voleu substituir-lo?', QMessageBox.Yes, QMessageBox.No)
            if r == QMessageBox.No:
                return

        # Desem l'arxiu de text
        with open(fRes+'.txt', 'w', encoding='cp1252') as f:
            f.write(self._leTitol.text()+'\n')
            f.write(self._teText.toPlainText())
        # Desem el projecte
        QgsLayerDefinition().exportLayerDefinition(fRes, self._capes)
        # Desem la imatge
        self._pixmap.save(fRes+'.png')

        # A partir d'aquí, creem un diàleg per obtenir les metadades i generar un HTML a partir d'elles
        wid = QDialog()
        lay = QVBoxLayout()
        wid.setLayout(lay)
        titol = QLabel('Introduïu les metadades associades al projecte')
        titol.setFont(QvConstants.FONTTITOLS)
        lay.addWidget(titol)

        layFormat = QVBoxLayout()
        frameFormat = self.getFrame(layFormat)
        layFormat.addWidget(QLabel('Format'))
        teFormat = QTextEdit()
        layFormat.addWidget(teFormat)
        lay.addWidget(frameFormat)

        layResum = QVBoxLayout()
        frameResum = self.getFrame(layResum)
        layResum.addWidget(QLabel('Resum'))
        teResum = QTextEdit()
        layResum.addWidget(teResum)
        lay.addWidget(frameResum)

        layEscales = QVBoxLayout()
        frameEscales = self.getFrame(layEscales)
        layEscales.addWidget(QLabel('Escales de visualització'))
        teEscales = QTextEdit()
        layEscales.addWidget(teEscales)
        lay.addWidget(frameEscales)

        layContingut = QVBoxLayout()
        frameContingut = self.getFrame(layContingut)
        layContingut.addWidget(QLabel('Contingut'))
        teContingut = QTextEdit()
        layContingut.addWidget(teContingut)
        lay.addWidget(frameContingut)

        layPropietari = QVBoxLayout()
        framePropietari = self.getFrame(layPropietari)
        layPropietari.addWidget(QLabel('Propietari'))
        tePropietari = QTextEdit()
        layPropietari.addWidget(tePropietari)
        lay.addWidget(framePropietari)

        bDesar = QvPushButton('Desar', destacat=True)
        lay.addWidget(bDesar, alignment=QtCore.Qt.AlignRight)

        def desarMetadades():
            with open(fRes+'.htm', 'w', encoding='cp1252') as f:
                dades = (teFormat, teResum, teEscales, teContingut, tePropietari)
                dades = (x.toPlainText().replace('\n','<br>') for x in dades)
                f.write(plantillaMetadades %
                        (self._leTitol.text(), *dades))

            wid.close()
        bDesar.clicked.connect(desarMetadades)
        wid.exec()
        self.close()
    def imprimirPlanol(self, x, y, escala, rotacion):
        # Preguntar on desem
        # Crear document de text
        # Crear metadades
        
        image_location = QvFuncions.capturarImatge(self._rubberband.asGeometry(), self._canvas, QSize(300,180))
        self._pixmap = QPixmap(str(image_location))
        lblImatge = QLabel()
        lblImatge.setPixmap(self._pixmap)
        self._layImatge.replaceWidget(self._imatge, lblImatge)
        self._imatge = lblImatge
        self.actualitzaEstatBDesar()
    def hideEvent(self,event):
        super().hideEvent(event)
        self._canvas.unsetMapTool(self._tool)


class PointTool(QgsMapTool):
    click = pyqtSignal(QgsPointXY)

    def __init__(self, parent, canvas):
        QgsMapTool.__init__(self, canvas)
        self.parent = parent

    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.click.emit(point)
