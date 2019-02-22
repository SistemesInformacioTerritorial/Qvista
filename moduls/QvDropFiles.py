# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtGui import QDropEvent, QDragEnterEvent, QDragMoveEvent, QDragLeaveEvent
from qgis.PyQt.QtCore import pyqtSignal, QUrl

import os

class QvDropFiles():
    
    arxiusPerProcessar = pyqtSignal(list)
    
    def __init__(self):
        self.llistaArxius = []
        self.extsUn = []
        self.extsMolts = []

    def setDropExts(self, extsUn=[], extsMolts=[]):
        self.extsUn = [x.lower() for x in extsUn]
        self.extsMolts = [x.lower() for x in extsMolts]

    def dragEnterEvent(self, event):
        if len(self.extsUn) == 0 and len(self.extsMolts) == 0:
            return
        self.llistaArxius = []
        nUn = 0
        nMolts = 0
        data = event.mimeData()
        if data.hasUrls():
            for url in data.urls():
                fich = url.toLocalFile()
                if os.path.isfile(fich):
                    _, fext = os.path.splitext(fich)
                    if fext.lower() in self.extsUn:
                        nUn += 1
                        self.llistaArxius.append(fich)
                    if fext.lower() in self.extsMolts:
                        nMolts += 1
                        self.llistaArxius.append(fich)
        if (nUn == 0 and nMolts > 0) or (nUn == 1 and nMolts == 0):
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        self.arxiusPerProcessar.emit(self.llistaArxius)
        self.llistaArxius = []
        event.acceptProposedAction()

    # # Drop files
    # self.setDropExts(['.QGS', '.qgz'], ['.QLR', '.shp', '.csv'])
    # self.arxiusPerProcessar.connect(lambda x: print(x))
