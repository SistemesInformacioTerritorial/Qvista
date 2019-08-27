from moduls.QvImports import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty #???
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor, QKeySequence
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
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblCapcalera = QLabel(objectName='Fosca')
        self.lblCapcalera.setText('  '+titol)
        self.lblLogo = QLabel()
        if logo:
            self.lblLogo.setPixmap(
                QPixmap('imatges/QVistaLogo_40_32.png'))
            self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)

        # Text de la notícia
        # self.caixaText = QtWidgets.QTextEdit()
        # self.caixaText.setHtml(open(file).read())
        # self.layout.addWidget(self.caixaText)
        self.file=file
        self.caixaText=QWebView()
        # caixaText.onLoadingChanged: {
        #     if (loadRequest.status == WebView.LoadFailedStatus) 
        #     console.log("Load failed! Error code: " + loadRequest.errorCode)
        # }
        self.caixaText.load(QUrl("file:///%s"%file))
        self.caixaText.loadHtml("no s'ha pogut trobar la informació")
        self.layoutCaixaText=QVBoxLayout()
        self.layoutCaixaText.addWidget(self.caixaText)
        self.layout.addLayout(self.layoutCaixaText)
        # self.layout.addWidget(self.caixaText)

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
        self.formata()

    def formata(self):
        '''Dóna format al diàleg de notícies'''
        pal=self.caixaText.palette()
        pal.setBrush(QPalette.Base,Qt.transparent)
        self.caixaText.page().setPalette(pal)
        self.caixaText.setAttribute(Qt.WA_OpaquePaintEvent,False)
        # self.caixaText.setFrameStyle(QFrame.NoFrame)
        self.caixaText.page().currentFrame().setScrollBarPolicy(Qt.Vertical,Qt.ScrollBarAlwaysOn)
        # self.caixaText.setViewportMargins(20, 20, 20, 0)
        # self.caixaText.setStyleSheet('''margin: 0px 0px 0px 10px''')
        self.caixaText.settings().setUserStyleSheetUrl(QUrl('file:///style.qss'))
        
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        # self.lblLogo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
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
    def easterEgg(self):
        self.carrega(os.getcwd()+'/easterEgg.htm')
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
            self.caixaText.setText("No s'ha pogut trobar l'arxiu")
        else:
            self.caixaText.load(QUrl("file:///%s"%file))
        print(file)