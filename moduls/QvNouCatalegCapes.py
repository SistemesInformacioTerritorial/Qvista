from moduls.QvNouCataleg import QvNouCataleg, DraggableLabel
from moduls.QvImports import *
from moduls.QvVisorHTML import QvVisorHTML
from moduls.QvConstants import QvConstants

class QvNouCatalegCapes(QvNouCataleg):
    #ENTRADACATALEG=CapaCataleg
    EXT='.qlr'
    DIRSCATALEGS=[x for x in carpetaCatalegLlista if os.path.isdir(x)]
    FAVORITS=False
    WINDOWTITLE='Catàleg de capes'
    afegirCapa=pyqtSignal(str)
    def __init__(self,*args, **kwargs):
        self.ENTRADACATALEG=CapaCataleg
        super().__init__(*args, **kwargs)
    def afegeixCapa(self, nomCapa):
        self.afegirCapa.emit(nomCapa)



class CapaCataleg(QFrame):
    '''La preview concreta que mostrem
    Bàsicament conté una imatge i el text
    La imatge ha de tenir el mateix nom que la capa amb extensió png
    El títol surt d'un arxiu de text amb el mateix nom. Ha de contenir una primera línia amb el títol, i la resta amb el text
    '''
    def __init__(self,capa,parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel)
        self.cataleg=parent
        self.checked = False
        self.setStyleSheet('border: none')
        self.layout=QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(300)
        self.setLayout(self.layout)
        self.nomBase=capa

        self.imatge=QPixmap(self.nomBase+'.png')
        # self.lblImatge=QLabel()
        lbl = QLabel()
        self.lblImatge=DraggableLabel(lbl,self.imatge,self.nomBase+'.qlr')
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
        self.bAfegir.setCursor(QvConstants.cursorClick())
        self.bInfo=QPushButton(parent=self.lblImatge)
        self.bInfo.setIcon(QIcon(os.path.join(imatgesDir,'cm_info.png')))
        self.bInfo.setFixedSize(24,24)
        self.bInfo.setIconSize(QSize(24,24))
        self.bInfo.move(270,150)
        self.bInfo.setCursor(QvConstants.cursorClick())
        self.bInfo.clicked.connect(self.obrirInfo)
        self.bInfo.setStyleSheet(stylesheet)
        try:
            with open(self.nomBase+'.txt', encoding='cp1252') as arxiu:
                self.titol=arxiu.readline()
                self.text=arxiu.read()
        except Exception as e:
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
        self.cataleg.afegeixCapa(self.nomBase+'.qlr')
        self.bInfo.setIcon(QIcon(os.path.join(imatgesDir,'cm_info.png')))
    def obrirInfo(self):
        visor=QvVisorHTML(self.nomBase+'.htm','Metadades capa',True,self)
        visor.show()
    def showEvent(self,event):
        super().showEvent(event)
        # self.bAfegir.show()
        # self.bInfo.show()
    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.cataleg.seleccionaElement(self)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.cataleg.seleccionaElement(self)

    def setChecked(self, checked: bool):
        self.checked = checked
        if checked:
            self.setStyleSheet(
                'CapaCataleg{border: 4px solid %s;}' % QvConstants.COLORCLARHTML)
            self.bAfegir.show()
            self.bInfo.show()

        else:
            self.setStyleSheet('CapaCataleg{border: 4px solid white;}')
            self.bAfegir.hide()
            self.bInfo.hide()
        self.update()
    
    def conteText(self,txt):
        # pensada per si en algun moment es vol incloure als filtres algun contingut diferent del títol i la descripció
        # EXEMPLE: 
        # nomMetadades=self.nomBase+'.htm'
        # if os.path.isfile(nomMetadades):
        #     with open(nomMetadades) as f:
        #         cont = f.read()
        #         return txt in self.cataleg.arregla(cont)
        return False


if __name__ == "__main__":
    import configuracioQvista
    from moduls.QvCanvas import QvCanvas
    from moduls.QvAtributs import QvAtributs
    from moduls.QvLlegenda import QvLlegenda
    with qgisapp() as app:
        with open('style.qss') as f:
            app.setStyleSheet(f.read())
        # canvas = QvCanvas(
        #     llistaBotons=["panning", "zoomIn", "zoomOut", "streetview"])
        # canvas.show()
        # atributs = QvAtributs(canvas)
        projecte = QgsProject.instance()
        # root = projecte.layerTreeRoot()
        # bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        # projecte.read(configuracioQvista.projecteInicial)
        # llegenda = QvLlegenda(canvas, atributs)
        # llegenda.show()
        cataleg = QvNouCatalegCapes()
        cataleg.showMaximized()
        cataleg.obrirProjecte.connect(lambda x: projecte.read(x))
        # creador = QvCreadorCataleg(canvas, projecte, cataleg)
        # creador.show()