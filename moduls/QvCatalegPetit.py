
# from moduls.QvImports import * 

from qgis.core import QgsRectangle, QgsProject
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QScrollArea
from qgis.PyQt.QtGui import QFont, QPixmap
from qgis.PyQt.QtCore import Qt
from botoInfoMapaPetit import Ui_BotoInfoMapa

from multiprocessing import Process,Queue,Pipe

from qgis.core.contextmanagers import qgisapp

import threading
import pickle
import os


carpetaCataleg = "N:/9SITEB/Publicacions/qVista/CATALEG/Projectes/"
if not os.path.isdir(carpetaCataleg):
    carpetaCataleg = "../dades/CatalegProjectes/"

longitudPathCataleg = len(carpetaCataleg)-1

class QvColumnaCataleg(QWidget):
    """
        Crea una columna de fichas per cada projecte de la llista amb que s'inicialitza.
 
    Cada columna porta el títol amb que s'ha inicilitzat.
    Es un widget amb el que és pot fer el que és vulgui, sempre que sigui legal.
    """

    def __init__(self, qV, titol, projectes, projectQgis = None, labelProjecte = None, textCerca = ''):

        QWidget.__init__(self)

        self.qV = qV
        self.titol = titol
        self.projectes = projectes
        self.projectQgis = projectQgis
        self.labelProjecte = labelProjecte
        self.textCerca = textCerca

        self.scroll = QScrollArea()
        self.frame1 = QFrame()

        self.frame1.setMinimumWidth(250)
        self.frame1.setMaximumWidth(250)

        self.layoutScroll = QVBoxLayout(self.frame1)
        self.layoutScroll.setContentsMargins(8,8,8,8)
        self.frame1.setLayout(self.layoutScroll)

        self.numeroBotons = 0
        
        fnt = QFont("Segoe UI", 18, weight=QFont.Normal)

        lblTitol = QLabel(self.titol)
        lblTitol.setFont(fnt)
        # self.layoutScroll.addWidget(lblTitol)


        for projecte in projectes:      
            if self.textCerca.lower() in projecte.lower():  
                botoInfoMapa = QWidget()
                botoInfoMapa.ui = Ui_BotoInfoMapa()
                botoInfoMapa.ui.setupUi(botoInfoMapa)

                self.numeroBotons = self.numeroBotons + 1

                self.layoutScroll.addWidget(botoInfoMapa)

                botoInfoMapa.ui.lblTitol.setText(projecte)
                imatge = QPixmap(carpetaCataleg+self.titol+'/'+projecte+".png")
                imatge = imatge.scaledToWidth(200)
                imatge = imatge.scaledToHeight(200)
                
                botoInfoMapa.ui.lblImatge.setPixmap(imatge)

                # botoInfoMapa.ui.b4.clicked.connect(lambda: self.obrirEnQgis('c:/qVista/dades/projectes/'+projecte+'.qgs'))

                nomProjecte=carpetaCataleg+self.titol+'/'+projecte+'.qgs'
                # project = QgsProject()
                # project.read(nomProjecte)

                # botoInfoMapa.ui.label_3.setText('Autor: '+project.metadata().author())
                botoInfoMapa.ui.b1.clicked.connect(self.obrirEnQVista(nomProjecte))
                botoInfoMapa.ui.b2.clicked.connect(self.obrirEnQgis(nomProjecte))    
                botoInfoMapa.ui.b3.clicked.connect(self.miniCanvas(nomProjecte))    
                # doc=QTextDocument()
                # doc.setHtml('c:/qVista/dades/'+projecte+'.htm')
                # botoInfoMapa.ui.textEdit.setDocument(doc)
                # botoInfoMapa.ui.label_3.hide()
                # try:
                #     text=open('c:/qVista/dades/projectes/'+projecte+'.htm').read()
                #     botoInfoMapa.ui.textEdit.setHtml(text)
                # except:
                #     # print ('Error carrega HTML')
                #     pass

        # for i in range(1,30):
        #     botoInfoMapa = QWidget()
        #     botoInfoMapa.ui = Ui_BotoInfoMapa()
        #     botoInfoMapa.ui.setupUi(botoInfoMapa)
        #     self.layoutScroll.addWidget(botoInfoMapa)
        
        self.scroll.setWidget(self.frame1)
        self.layoutWidget = QVBoxLayout(self)
        self.layoutWidget.setContentsMargins(0,0,0,0)
        self.setLayout(self.layoutWidget)

        self.layoutWidget.addWidget(lblTitol)
        self.layoutWidget.addWidget(self.scroll)
        # self.viewport().installEventFilter(self.frame1)
        self.scroll.setMaximumWidth(270)
        self.scroll.setMinimumWidth(270)
        self.setMaximumWidth(270)
        self.setMinimumWidth(270)
        if self.numeroBotons == 0:
        #     self.show()
        # else:
            self.hide()
        
    # def obrirEnQgis(self, projecte):
    #     QDesktopServices().openUrl(QUrl('d:/dropbox/qvistaProd/'+projecte))


    def obrirEnQgis(self, projecte):
        
        def obertura():
            try:
                QDesktopServices().openUrl(QUrl(projecte)) 
            except:
                pass
        return obertura

    
    def miniCanvas(self, projecte):
        def obertura():
            try:
                instruccio = "python-qgis.bat miniCanvas.py {}".format(projecte)
                os.system(instruccio)
            except:
                pass
        return obertura

    def obrirEnQVista(self, projecte):
        def obertura():
            try:
                rang = self.qV.canvas.extent()
                self.projectQgis.read(projecte)
                self.qV.lblProjecte.setText(self.project.baseName())
                if rang is not None:
                    self.qV.canvas.setExtent(rang)
                self.labelProjecte.setText(self.projectQgis.title())
                self.parent().parent().parent().parent().hide()
            except:
                pass
        return obertura


    def obrirCanvasTemp(self, child_conn, prj):
        with qgisapp() as app:      
            self.tcanvas = QgsMapCanvas()
            self.tproject = QgsProject.instance()
            self.troot = QgsProject.instance().layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(self.troot, self.tcanvas)
            self.tcanvas.show()
            self.tproject.read(prj)

    def canvasProvisional(self, projecte):
        
        def obertura():
            try:
                self.parent_conn,self.child_conn = Pipe()
                self.p = Process(target=self.obrirCanvasTemp, args=(self.child_conn,projecte,))
                self.p.start()
            except:
                pass
        return obertura




class QvCataleg(QWidget):
    
    def __init__(self, qV, projectQgis = None, labelProjecte = None):
        self.projectQgis = projectQgis
        self.qV = qV
        self.labelProjecte = labelProjecte
        QWidget.__init__(self)
        layoutWidgetPrincipal = QVBoxLayout(self)
        self.setLayout(layoutWidgetPrincipal)

        frameCapcalera = QFrame()
        frameCapcalera.setMaximumHeight(70)
        frameCapcalera.setMinimumHeight(70)
        #frameCapcalera.setStyleSheet('QFrame {background-color: #aaaaaa')

        lytCapcalera = QVBoxLayout(frameCapcalera)
        frameCapcalera.setLayout(lytCapcalera)
        lytCapcalera.setContentsMargins(0,0,0,0)

        fnt = QFont("Segoe UI", 22, weight=QFont.Normal)
        titol = QLabel("Catàleg d'Informació Territorial")
        titol.setFont(fnt)
        self.liniaCerca = QLineEdit()
        self.liniaCerca.setMaximumWidth(300)
        self.liniaCerca.setClearButtonEnabled(True)
        self.liniaCerca.returnPressed.connect(self.filtra)

        lytCapcalera.addWidget(titol)
        lytCapcalera.addWidget(self.liniaCerca)

        scrollFull = QScrollArea()
        frame = QFrame()
        scrollFull.setWidget(frame)
        self.layoutFrame = QHBoxLayout(frame)
        self.layoutFrame.setAlignment(Qt.AlignLeft)
        frame.setLayout(self.layoutFrame)

        frame.setGeometry(10,10,4000,900)
        frame.setMaximumHeight(900)
        frame.setMinimumHeight(900)

        # frame.show()
        self.temesCataleg = []
        temes = []
        self.dictProjectes = {}
        contingutCarpetes = os.walk(carpetaCataleg)
        for carpeta in contingutCarpetes:
            tema = carpeta[0][longitudPathCataleg+1:]
            if tema !='':
                self.temesCataleg.append(tema)
                projectes = []
                for fitxer in carpeta[2]:
                    projectes.append(fitxer[0:-4])
                self.dictProjectes[tema] = sorted(set(projectes))
        
        self.columnes = []
        for tema in self.dictProjectes:
            columna = QvColumnaCataleg(self.qV,tema, self.dictProjectes[tema], self.projectQgis, self.labelProjecte)
            self.columnes.append(columna)

        # self.qvColumnaCataleg = QvColumnaCataleg(self.qV,'Mapes generals', self.projectes, self.projectQgis, self.labelProjecte)
        # self.qvColumnaCataleg2 = QvColumnaCataleg(self.qV,'Urbanisme', self.projectesUrb, self.projectQgis, self.labelProjecte)
        # self.qvColumnaCataleg3 = QvColumnaCataleg(self.qV,'Infraestructures', self.projectesInf, self.projectQgis, self.labelProjecte)
        # self.qvColumnaCataleg4 = QvColumnaCataleg(self.qV,'AMB', self.projectesAMB, self.projectQgis, self.labelProjecte)
        # qvColumnaCataleg82 = QvColumnaCataleg('Animals, gats i fures', projectes)
        # qvColumnaCataleg83 = QvColumnaCataleg('Obres de ciutat', projectes)
        # qvColumnaCataleg9 = QvColumnaCataleg('Topografia', projectes)
        # qvColumnaCataleg92 = QvColumnaCataleg('Cosmologiade ciutat', projectes)

        for columna in self.columnes:
            self.layoutFrame.addWidget(columna)



        layoutWidgetPrincipal.addWidget(frameCapcalera)
        layoutWidgetPrincipal.addWidget(scrollFull)
        self.show()


    def filtra(self): 
        # Maravilloses dues línies que esborren columnes i botons
        for i in reversed(range(self.layoutFrame.count())): 
            self.layoutFrame.itemAt(i).widget().setParent(None)

        self.columnes=[]
        for tema in self.dictProjectes:
            columna = QvColumnaCataleg(self.qV,tema, self.dictProjectes[tema], self.projectQgis, self.labelProjecte, textCerca=self.liniaCerca.text())
            self.columnes.append(columna)
        
        for columna in self.columnes:
            self.layoutFrame.addWidget(columna)



if __name__ == "__main__":
    with qgisapp() as app:

        cataleg = QvCataleg(None)
        cataleg.showMaximized()

