import sys, os, glob
from moduls.QvImports import *
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap

class QVViewer(QWidget):

    def __init__(self, carpeta):
        super().__init__()
        self.title = 'PyQt5 image - pythonspot.com'
        self.carpeta = carpeta
        self.left = 100
        self.top = 100
        self.width = 1000
        self.height = 800
        self.indexImatge = 0
        # self.carpeta = 'd:/imatgesQGIS/[%igds_text_string%]/'
        # self.carpeta = str(sys.argv[1])
        self.initUI()

    
    def initUI(self):
        self.setWindowTitle(self.carpeta)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumWidth(self.width)
        self.setMaximumHeight(self.height)
    
        # Create widget
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.label = QLabel(self)
        bEndavant = QPushButton('endavant')
        bEnrrera = QPushButton('enrrera')
        bEndavant.clicked.connect(self.endavant)
        bEnrrera.clicked.connect(self.enrrera)
        layout.addWidget(self.label)
        layout.addWidget(bEnrrera)
        layout.addWidget(bEndavant)
        llistaFitxers=os.listdir(self.carpeta)
        self.llistaImatges=[]
        for fitxer in llistaFitxers:
            if fitxer.endswith(".jpg") or fitxer.endswith(".png") or fitxer.endswith(".bmp") or fitxer.endswith(".jpeg"):
                self.llistaImatges.append(fitxer)
        pixmap = QPixmap(self.carpeta+self.llistaImatges[self.indexImatge])
        self.label.setPixmap(pixmap)
        self.label.setMaximumWidth(self.width-10)
        self.label.setMaximumHeight(self.height-10)
        pixmap = self.resize(pixmap.width(),pixmap.height())
        self.show()
        # print ('Number of arguments:', len(sys.argv), 'arguments.')
        # print ('Argument List:', str(sys.argv))

    def endavant(self):
        if self.indexImatge<=len(self.llistaImatges):
            self.indexImatge = self.indexImatge + 1
        pixmap = QPixmap(self.carpeta+self.llistaImatges[self.indexImatge])
        self.label.setPixmap(pixmap)

    def enrrera(self):
        if self.indexImatge > 0:
            self.indexImatge = self.indexImatge - 1
        pixmap = QPixmap(self.carpeta+self.llistaImatges[self.indexImatge])
        self.label.setPixmap(pixmap)


if __name__ == "__main__":
    with qgisapp() as app:
        viewer = QVViewer('d:/')
        viewer.show()