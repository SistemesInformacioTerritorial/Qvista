#!/usr/bin/env python
import os

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtGui import QIcon

from configuracioQvista import arxiuNews, imatgesDir
from moduls.QvMemoria import QvMemoria
from moduls.QvVisorHTML import QvVisorHTML


class QvNews(QtWidgets.QAction):
    '''Acció de les notícies. Ella mateixa comprova si hi ha notícies noves, i si hi són, les mostra'''

    def __init__(self, parent: QtWidgets.QWidget = None):
        self.ICONA = QIcon(os.path.join(imatgesDir,'News.png'))
        self.ICONADESTACADA = QIcon(os.path.join(imatgesDir,'NewsDestacada.png'))
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
            msg=QtWidgets.QMessageBox()
            msg.setText("No s'ha pogut accedir a les notícies      ")
            msg.setWindowTitle('qVista')
            msg.exec_()
            return
        self.news = QvVisorHTML(arxiuNews, 'Novetats qVista')
        self.news.exec_()
        self.setIcon(self.ICONA)
        QvMemoria().setUltimaNew()

    def calNoticiaNova(self) -> bool:
        '''Comprova si hi ha notícies noves. 
            Returns: x{Bool} -- Booleà que indica si hi ha una notícia nova o no
        '''
        # Si no existeix l'arxiu temporal vol dir que mai hem obert notícies :(
        if not os.path.isfile(arxiuNews):
            return False
        return QvMemoria().getUltimaNew() < os.path.getmtime(arxiuNews)

# QFrame no permet fer exec. QDialog sí



    


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    news = QvNews()
    menu = QtWidgets.QMenu()
    menu.addAction(news)
    menu.show()
    sys.exit(app.exec_())
