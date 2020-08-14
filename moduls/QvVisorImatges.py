import os
from moduls.QvImports import *
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap

from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor


class QVViewer(QWidget):
    def __init__(self, carpeta):
        super().__init__()
        self.scaleFactor = 1.0
        self.printer = QPrinter()
        self.title = 'PyQt5 image - pythonspot.com'
        self.carpeta = carpeta
        self.left = 100
        self.top = 100
        self.width = 1100
        self.height = 800

        self.indexImatge = 0
        self.initUI()

        self.createActions()        
        self.menu_bar()

    def initUI(self):
        self.setStyleSheet(" QMenuBar {background-color:transparent;color:rgb(0,0,0);}")
        self.setWindowTitle(self.title+' '+self.carpeta)
        self.setMaximumWidth(self.width)
        self.setMaximumHeight(self.height)
        # Create widget
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
    
        self.imageLabel = QLabel(self)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(True)

        # BOTONES ADELANTE/ATRAS
        icon_anterior=QIcon(os.path.join(imatgesDir,'qv_vista_anteriorG.png'))
        bEnrrera = QPushButton(icon_anterior,"")
        bEnrrera.setIconSize(QSize(50,50))
        bEnrrera.setStyleSheet('background-color:transparent ;color:#000000;')  
        bEnrrera.clicked.connect(self.enrrera)

        icon_seguent=QIcon(os.path.join(imatgesDir,'qv_vista_seguentG.png'))
        bEndavant = QPushButton(icon_seguent,"")
        bEndavant.setIconSize(QSize(50,50));
        bEndavant.clicked.connect(self.endavant)
        bEndavant.setStyleSheet('background-color:transparent ;color:#000000;')  

        self.layout.addWidget(bEnrrera)
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(bEndavant)
        self.installEventFilter(self)

        llistaFitxers=os.listdir(self.carpeta)
        self.llistaImatges=[]
        for fitxer in llistaFitxers:
            if fitxer.endswith(".jpg") or fitxer.endswith(".png") or fitxer.endswith(".bmp") or fitxer.endswith(".jpeg"):
                self.llistaImatges.append(fitxer)
        
        self.cual= self.carpeta+self.llistaImatges[self.indexImatge]
        self.pixmap = QPixmap(self.cual)
        self.imageLabel.setPixmap(self.pixmap)
        self.normalSize()
        
        self.show()
        self.setWindowTitle( 'Zoom:  ' + str(round(self.scaleFactor,2)*100)+ " %    "+str(self.indexImatge +1)+" de "+ str(len(self.llistaImatges)))   
        self.resize(self.imageLabel.width()+229,self.imageLabel.height()+30)

    def eventFilter(self, obj, event):
        if event.type() == 51:
            self.keyPressEvent(event)
        return False        

    def keyPressEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == 16777234:   # flecha izquierda
            self.enrrera()
        if key == 16777236:   # flecha derecha
            self.endavant()

    def createActions(self):
        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P", enabled=True, triggered=self.print_)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=True, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=True, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=True, triggered=self.normalSize)
        self.infoAct = QAction("&Info", self, shortcut="F1", enabled=True, triggered=self.info)
        
    def menu_bar (self) : 
        self.menuBar = qtWdg.QMenuBar (self)
        self.menuBar.setToolTip("més accions")
        self.menuBar.resize(40,30)
        self.fileMenu = self.menuBar.addMenu (QIcon(os.path.join(imatgesDir,'qv_more.png')),"")
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.zoomInAct)
        self.fileMenu.addAction(self.zoomOutAct)
        self.fileMenu.addAction(self.normalSizeAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.infoAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addAction(self.exitAct)
        
        self.menuBar.show()
   
    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())
    
    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.pixmap = QPixmap(self.cual)
        self.imageLabel.setPixmap(self.pixmap)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0
        self.setWindowTitle( 'Zoom:  ' + str(round(self.scaleFactor,2)*100)+ " %    "+str(self.indexImatge +1)+" de "+ str(len(self.llistaImatges)))    

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        medida= self.imageLabel.pixmap().size()
        redimension= self.scaleFactor * medida
        self.imageLabel.resize(redimension)
        self.imageLabel.setScaledContents(True)
        
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 4.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.25)        

        self.setWindowTitle( 'Zoom:  ' + str(round(self.scaleFactor,2)*100)+ " %    "+str(self.indexImatge +1)+" de "+ str(len(self.llistaImatges)))   

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def endavant(self):
        if self.indexImatge<len(self.llistaImatges)-1:
            self.indexImatge = self.indexImatge + 1
        elif self.indexImatge ==len(self.llistaImatges)-1:
            self.indexImatge=0
        self.cual= self.carpeta+self.llistaImatges[self.indexImatge]
        self.pixmap = QPixmap(self.cual)
        self.imageLabel.setPixmap(self.pixmap)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.normalSize()
        self.setWindowTitle( 'Zoom:  ' + str(round(self.scaleFactor,2)*100)+ " %    "+str(self.indexImatge +1)+" de "+ str(len(self.llistaImatges)))   
        self.resize(self.imageLabel.width()+229,self.imageLabel.height()+30)

    def enrrera(self):
        if self.indexImatge > 0:
            self.indexImatge = self.indexImatge - 1
        elif self.indexImatge == 0:
            self.indexImatge = len(self.llistaImatges)-1
        self.cual= self.carpeta+self.llistaImatges[self.indexImatge]
        self.pixmap = QPixmap(self.cual)
        self.imageLabel.setPixmap(self.pixmap)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.normalSize()
        self.setWindowTitle( 'Zoom:  ' + str(round(self.scaleFactor,2)*100)+ " %    "+str(self.indexImatge +1)+" de "+ str(len(self.llistaImatges)))             
        self.resize(self.imageLabel.width()+229,self.imageLabel.height()+30)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))

    def info(self):
        info_carpeta= "<b>Carpeta:  </b>"+ self.carpeta +"<br>"
        fitxer=  "<b>Fitxer:  </b>" + os.path.basename(self.cual) +"<br>" 
        tamany = "<b>Size: </b>" +str(self.pixmap.width())+' x '+str(self.pixmap.height())
        QMessageBox.about(self, "Info ",
                info_carpeta+ '  '+ fitxer +'  '+ tamany
        )
                          
                          

if __name__ == "__main__":
    with qgisapp() as app:
        viewer = QVViewer('d:/tmp/fotos/')
        viewer.show()