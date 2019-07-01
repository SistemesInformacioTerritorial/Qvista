#!/usr/bin/env python
from moduls.QvImports import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor
import os
import tempfile
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
import errno


class QvNews(QtWidgets.QAction):
    '''Acció de les notícies. Ella mateixa comprova si hi ha notícies noves, i si hi són, les mostra'''

    def __init__(self, parent: QWidget = None):
        self.ICONA = QIcon('Imatges/News.png')
        self.ICONADESTACADA = QIcon('Imatges/NewsDestacada.png')
        # QtWidgets.QAction.__init__(self,self.ICONA,'Notícies',parent)
        super().__init__(self.ICONA, 'Notícies', parent)
        if self.calNoticiaNova():
            self.timer = QTimer()
            self.timer.timeout.connect(self.blink)
            self.timer.start(200)
        self.setStatusTip('Notícies')
        self.triggered.connect(self.mostraNoticies)

    def blink(self):
        '''Acció de parpadejar. Compta quants cops ha parpadejat, i quan arriba a la quantitat fixada esborra el comptador'''
        if not hasattr(self, 'light'):
            self.light = False
            self.numBlinks = 0

        if self.light:
            self.setIcon(self.ICONADESTACADA)
            self.numBlinks += 1
        else:
            self.setIcon(self.ICONA)

        if self.numBlinks == 4:
            delattr(self, 'timer')
            # self.setVisible(True)
            delattr(self, 'numBlinks')

        self.light = not self.light

    def mostraNoticies(self):
        '''Obre l'arxiu de notícies i les mostra'''
        if not os.path.isfile(arxiuNews):
            msg=QMessageBox()
            msg.setText("No s'ha pogut accedir a les notícies      ")
            msg.setWindowTitle('qVista')
            msg.exec_()
            return
        self.news = QvNewsFinestra(arxiuNews)
        self.news.exec_()
        self.setIcon(self.ICONA)
        with open(arxiuTmpNews, 'w') as arxiu:
            # Escrivim alguna cosa. Realment no caldria que fos el temps
            import time
            arxiu.write(str(time.time()))

    def calNoticiaNova(self) -> bool:
        '''Comprova si hi ha notícies noves. 
            Returns: x{Bool} -- Booleà que indica si hi ha una notícia nova o no
        '''
        # Si no existeix l'arxiu temporal vol dir que mai hem obert notícies :(
        if not os.path.isfile(arxiuNews):
            return False
        if not os.path.isfile(arxiuTmpNews):
            return True
        return os.path.getmtime(arxiuTmpNews) < os.path.getmtime(arxiuNews)

# QFrame no permet fer exec. QDialog sí


class QvNewsFinestra(QDialog):
    '''Diàleg per visualitzar les notícies (que, per extensió, podem usar sempre que vulguem per visualitzar arxius HTML)'''

    def __init__(self, file: str, titol: str = 'Novetats qVista', parent: QWidget = None):
        '''Crea una instància de QvNewsFinestra
        Arguments:
            file {str} -- adreça de l'arxiu HTML que volem visualitzar
        Keyword Arguments:
            parent {QWidget} -- Pare del diàleg (default: {None})
        '''
        super().__init__(parent)
        # Layout gran. Tot a dins
        self.layout = QVBoxLayout(self)

        # FILA SUPERIOR
        self.layoutCapcalera = QHBoxLayout()
        self.widgetSup = QWidget(objectName='layout')
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblLogo = QLabel()
        self.lblLogo.setPixmap(
            QPixmap('imatges/QVistaLogo_40_32.png'))
        self.lblCapcalera = QLabel(objectName='Fosca')
        self.lblCapcalera.setText('  '+titol)
        # self.lblCapcalera.setStyleSheet(
        #     'color: %s' % QvConstants.COLORFOSCHTML)
        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)

        # Text de la notícia
        self.caixaText = QtWidgets.QTextEdit()
        self.caixaText.setHtml(open(file).read())
        self.layout.addWidget(self.caixaText)

        # Botó de sortida
        self.layoutBoto = QHBoxLayout()
        self.layout.addLayout(self.layoutBoto)
        self.layoutBoto.addItem(QSpacerItem(
            20, 5, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.exitButton = QvPushButton('Tancar')
        self.exitButton.clicked.connect(self.close)
        self.layoutBoto.addWidget(self.exitButton)

        self.formata()

    def formata(self):
        '''Dóna format al diàleg de notícies'''
        self.caixaText.viewport().setAutoFillBackground(False)
        self.caixaText.setReadOnly(True)
        # Millor que es pugui seleccionar el text? O que no es pugui?
        self.caixaText.setEnabled(True)
        self.caixaText.setFrameStyle(QFrame.NoFrame)
        # Comentar si volem que s'oculti la scrollbar quan no s'utilitza
        self.caixaText.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #self.caixaText.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.caixaText.setViewportMargins(20, 20, 20, 0)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.lblLogo.setStyleSheet(
            'background-color: %s; border: 0px' % QvConstants.COLORFOSCHTML)
        self.lblLogo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lblCapcalera.setStyleSheet('background-color: %s; color: %s; border: 0px' % (
            QvConstants.COLORFOSCHTML, QvConstants.COLORBLANCHTML))
        self.lblCapcalera.setFont(QvConstants.FONTCAPCALERES)
        self.lblCapcalera.setFixedHeight(40)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layoutCapcalera.setContentsMargins(0, 0, 0, 0)
        self.layoutCapcalera.setSpacing(0)
        self.layoutBoto.setContentsMargins(0, 0, 0, 0)
        self.layoutBoto.setSpacing(0)
        self.widgetSup.setGraphicsEffect(QvConstants.ombraHeader(self.widgetSup))
        # self.ombraHeader=QvConstants.afegeixOmbraHeader(self.widgetSup)
        # self.ombraHeader.setEnabled(True)

        self.setWindowTitle("qVista - Noticies")
        self.resize(640, 480)
        self.oldPos = self.pos()
        # QvConstants.afegeixOmbraWidget(self)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        # print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Return:
            self.close()
    


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    news = QvNews()
    menu = QMenu()
    menu.addAction(news)
    menu.show()
    sys.exit(app.exec_())
