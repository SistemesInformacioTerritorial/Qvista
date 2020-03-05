#!/usr/bin/env python
from moduls.QvImports import * 
from PyQt5 import QtWidgets
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from typing import Callable

class QvSuggeriments(QDialog):
    def __init__(self, acceptAction: Callable[[str,str],None]=QWidget.close, parent: QtWidgets.QWidget=None):
        super().__init__(parent)
        #Layout gran. Tot a dins
        self.layout=QVBoxLayout(self)

        #FILA SUPERIOR
        self.layoutCapcalera=QHBoxLayout()
        self.widgetSup=QWidget(objectName='layoutFosc')
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblLogo=QLabel()
        self.lblLogo.setPixmap(QPixmap(imatgesDir+'bug_cap_sugg.png'))
        self.lblCapcalera=QLabel(objectName='fosca')
        self.lblCapcalera.setText(' Problemes? Suggeriments?')
        self.lblCapcalera.setStyleSheet('background-color: %s' %QvConstants.COLORFOSCHTML)
        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)

        #info
        self.info = QLabel()
        self.info.setContentsMargins(20,20,20,20)
        self.info.setText("Heu trobat algun problema? Voleu fer-nos algun suggeriment? \nSi us plau, descriviu-lo breument a continuació. El vostre suport ens ajudarà a millorar.")
        self.info.setWordWrap(True)
        self.layout.addWidget(self.info)

        #TITOL + DESCRIPCIO
        self.layoutTiD = QVBoxLayout()
        self.layout.addLayout(self.layoutTiD)
        self.layoutTitolReport = QHBoxLayout()
        self.lblTitle = QLabel()
        self.offset1 = QLabel()
        self.leTitle = QtWidgets.QTextEdit()
        self.layoutTitolReport.addWidget(self.lblTitle)
        self.layoutTitolReport.addWidget(self.offset1)
        self.layoutTitolReport.addWidget(self.leTitle)
        self.layoutTiD.addLayout(self.layoutTitolReport)

        self.layoutDescripcio = QHBoxLayout()
        self.lblContent = QLabel()
        self.lblContent.setText("Descripció:")
        self.caixaText=QtWidgets.QTextEdit()
        self.layoutDescripcio.addWidget(self.lblContent)
        self.layoutDescripcio.addWidget(self.caixaText)
        self.layoutTiD.addLayout(self.layoutDescripcio)


        #Botons
        self.layoutBoto=QHBoxLayout()
        self.hSpacerL = QSpacerItem(80, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.acceptButton=QvPushButton('Enviar',destacat=True)
        self.acceptAction=acceptAction
        self.acceptButton.clicked.connect(self.acceptar)
        self.leTitle.textChanged.connect(lambda: self.acceptButton.setEnabled(self.leTitle.toPlainText()!=''))
        self.exitButton=QvPushButton('Cancel·lar')
        self.exitButton.clicked.connect(self.close)
        self.hSpacerR = QSpacerItem(80, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.offsetUp = QLabel()
        self.offsetUp.setFixedHeight(10)
        self.layout.addWidget(self.offsetUp)
        
        self.layout.addLayout(self.layoutBoto)
        self.layoutBoto.addItem(self.hSpacerL)
        self.layoutBoto.addWidget(self.acceptButton)
        #self.layoutBoto.addWidget(self.offsetM) ##afegir espai entre botons
        self.layoutBoto.addWidget(self.exitButton)
        self.layoutBoto.addItem(self.hSpacerR)

        self.offsetDown = QLabel()
        self.offsetUp.setFixedHeight(10)
        self.layout.addWidget(self.offsetDown)
        
        self.formata()

    def acceptar(self):
        self.acceptAction(self.leTitle.toPlainText(),self.caixaText.toPlainText())
        self.close()

    #determina el format dels diferents components de la window
    def formata(self): 
        self.layoutTiD.setContentsMargins(20,0,20,0)
        self.layoutTiD.setSpacing(20)
        self.lblTitle.setText("Títol:")
        self.leTitle.setFixedHeight(26)
        self.caixaText.viewport().setAutoFillBackground(False)
        self.caixaText.setEnabled(True) #Millor que es pugui seleccionar el text? O que no es pugui?
        #self.caixaText.setFrameStyle(QFrame.NoFrame)
        self.caixaText.setViewportMargins(3,3,3,3)
        self.leTitle.setViewportMargins(3,0,3,0)
        self.offset1.setFixedWidth(17)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.lblLogo.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        
        self.lblCapcalera.setFont(QvConstants.FONTCAPCALERES)
        self.lblCapcalera.setFixedHeight(40)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layoutCapcalera.setContentsMargins(0,0,0,0)
        self.layoutCapcalera.setSpacing(0)
        self.layoutBoto.setContentsMargins(0,0,0,0)
        self.layoutBoto.setSpacing(0)

        self.widgetSup.setGraphicsEffect(QvConstants.ombraHeader(self))
        self.widgetSup.setStyleSheet('color: %s; background-color: solid %s; border: 0px;'%(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML))
        
        self.setWindowTitle("qVista - Problemes i Suggeriments")
        self.setFixedSize(520, 360)
        self.oldPos=self.pos()
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        #print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self,event):
        super().keyPressEvent(event)
        if event.key()==Qt.Key_Escape:
            self.close()
        elif event.key()==Qt.Key_Return:
            self.acceptar()
    def show(self):
        self.leTitle.setText('')
        self.caixaText.setText('')
        super().show()




if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    news=QvSuggeriments(lambda x: print(x))
    news.show()
    sys.exit(app.exec_())