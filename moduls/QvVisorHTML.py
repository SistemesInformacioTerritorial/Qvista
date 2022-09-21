from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QPoint, Qt, QTimer, QUrl
from qgis.PyQt.QtGui import QKeySequence, QPalette, QPixmap
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.PyQt.QtWidgets import (QDialog, QHBoxLayout, QLabel, QSizePolicy,
                                 QSpacerItem, QVBoxLayout, QWidget)

from configuracioQvista import imatgesDir, os
from moduls.QvApp import QvApp
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton


class QvVisorHTML(QDialog):
    '''Diàleg per visualitzar les notícies (que, per extensió, podem usar sempre que vulguem per visualitzar arxius HTML)'''

    def __init__(self, file: str, titol: str, logo: bool=True, parent: QWidget = None):
        '''Crea una instància d'un visor HTML
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
        self.widgetSup.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblCapcalera = QLabel(objectName='Fosca')
        self.lblCapcalera.setText('  '+titol)
        self.lblLogo = QLabel()
        if logo:
            self.lblLogo.setPixmap(
                QPixmap(os.path.join(imatgesDir,'QVistaLogo_40_32.png')))
            self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)

        # Text de la notícia
        self.file=file
        self.caixaText=QWebView()
        self.setZoomFactor(QvApp().zoomFactor())
        self.caixaText.load(QUrl("file:///%s"%file))
        self.layoutCaixaText=QVBoxLayout()
        self.layoutCaixaText.addWidget(self.caixaText)
        self.layout.addLayout(self.layoutCaixaText)

        # Botó de sortida
        self.layoutBoto = QHBoxLayout()
        self.layout.addLayout(self.layoutBoto)
        self.layoutBoto.addItem(QSpacerItem(
            20, 5, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.exitButton = QvPushButton('Tancar')
        self.exitButton.clicked.connect(self.close)
        self.layoutBoto.addWidget(self.exitButton)

        self.shortcutEasterEgg=QtWidgets.QShortcut(QKeySequence('Ctrl+E'),self)
        self.shortcutEasterEgg.activated.connect(self.easterEgg)
        self.formata(titol)

    def formata(self, titol):
        '''Dóna format al diàleg de notícies'''
        pal=self.caixaText.palette()
        pal.setBrush(QPalette.Base,Qt.transparent)
        self.caixaText.page().setPalette(pal)
        self.caixaText.setAttribute(Qt.WA_OpaquePaintEvent,False)
        self.caixaText.page().currentFrame().setScrollBarPolicy(Qt.Vertical,Qt.ScrollBarAlwaysOn)
        self.caixaText.settings().setUserStyleSheetUrl(QUrl('file:///style.qss'))
        
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.lblLogo.setFixedSize(40,40)
        self.lblCapcalera.setStyleSheet('background-color: %s; color: %s; border: 0px' % (
            QvConstants.COLORFOSCHTML, QvConstants.COLORBLANCHTML))
        self.lblCapcalera.setFont(QvConstants.FONTCAPCALERES)
        self.lblCapcalera.setFixedHeight(40)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layoutCapcalera.setContentsMargins(0, 0, 0, 0)
        self.layoutCapcalera.setSpacing(0)
        self.layoutBoto.setContentsMargins(10, 0, 10, 10)
        self.layoutBoto.setSpacing(10)
        self.layoutCaixaText.setContentsMargins(10,10,2,10)
        self.widgetSup.setGraphicsEffect(QvConstants.ombraHeader(self.widgetSup))

        self.setWindowTitle(titol)
        self.resize(640, 480)
        self.oldPos = self.pos()

    def setZoomFactor(self,factor):
        self.caixaText.setZoomFactor(factor)

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
    def easterEgg(self):
        self.carrega(os.getcwd()+'/easterEgg.html')
        #Delay
        self.timer=QTimer()
        self.timer.timeout.connect(self.easterEggExit)
        self.timer.start(500)
    def easterEggExit(self):
        delattr(self,'timer')
        self.carrega()
    def carrega(self,file=None):
        if file is None:
            file=self.file
            self.caixaText.load(QUrl('file:///%s'%self.file))
        else:
            self.caixaText.load(QUrl("file:///%s"%file))
        print(file)