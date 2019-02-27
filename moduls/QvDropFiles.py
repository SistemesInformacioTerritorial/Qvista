# -*- coding: utf-8 -*-

from qgis.PyQt.QtGui import QDropEvent, QDragEnterEvent, QDragMoveEvent, QDragLeaveEvent
from qgis.PyQt.QtCore import QObject, pyqtSignal, QUrl

import os
class QvDropFiles(QObject): 
    
    arxiusPerProcessar = pyqtSignal(list)
    
    def __init__(self, widget):
        QObject.__init__(self)
        self.widget = widget
        self.extsUn = []
        self.extsMolts = []
        self.llistaArxius = []
        self.dropping = False
        self.widgetDragEnterEvent = self.widget.dragEnterEvent
        self.widgetDragMoveEvent = self.widget.dragMoveEvent
        self.widgetDragLeaveEvent = self.widget.dragLeaveEvent
        self.widgetDropEvent = self.widget.dropEvent

    def dropActiu(self):
        if len(self.extsUn) == 0 and len(self.extsMolts) == 0:
            return False
        else:
            return True

    def llistesExts(self, extsUn=[], extsMolts=[]):
        self.extsUn = [x.lower() for x in extsUn]
        self.extsMolts = [x.lower() for x in extsMolts]
        if self.dropActiu():
            self.widget.dragEnterEvent = self.dragEnterEvent
            self.widget.dragMoveEvent = self.dragMoveEvent
            self.widget.dragLeaveEvent = self.dragLeaveEvent
            self.widget.dropEvent = self.dropEvent
        else:
            self.widget.dragEnterEvent = self.widgetDragEnterEvent
            self.widget.dragMoveEvent = self.widgetDragMoveEvent
            self.widget.dragLeaveEvent = self.widgetDragLeaveEvent
            self.widget.dropEvent = self.widgetDropEvent

    def dragEnterEvent(self, event):
        self.dropping = False
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
                self.dropping = True
        if self.dropping:
            event.acceptProposedAction()
        else:
            self.widgetDragEnterEvent(event)
            
    def dragMoveEvent(self, event):
        if self.dropping:
            event.acceptProposedAction()
        else:
            self.widgetDragMoveEvent(event)

    def dragLeaveEvent(self, event):
        if self.dropping:
            event.accept()
        else:
            self.widgetDragLeaveEvent(event)

    def dropEvent(self, event):
        if self.dropping:
            self.arxiusPerProcessar.emit(self.llistaArxius)
            self.dropping = False
            self.llistaArxius = []
            event.acceptProposedAction()
        else:
            self.widgetDropEvent(event)

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    # from qgis.gui import QgsMapCanvas
    from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvApp import QvApp

    with qgisapp(sysexit=False) as app:
 
        qApp = QvApp()
        qApp.carregaIdioma(app, 'ca')

        # 1.- Crear widget donde aplicar el drag & drop de ficheros
        canvas = QvCanvas()
        # 2.- Crear el objeto QvDropFiles pasándole el widget
        drop = QvDropFiles(canvas)
        # 3.- Definir dos listas de extensiones: fichero único (proyecto) o varios ficheros (capas)
        drop.llistesExts(['.QGS', '.qgz'], ['.QLR', '.shp', '.csv'])
        # 4.- Asociar evento de drop a función que maneje la lista de archivos soltados
        drop.arxiusPerProcessar.connect(lambda nomFich: print('Dropped:', nomFich))
        # 5.- El evento recibirá o bien un fichero de la primera lista o varios de la segunda

        llegenda = QvLlegenda(canvas)

        llegenda.project.read('../Dades/Projectes/BCN11.qgs')

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)
        canvas.show()



