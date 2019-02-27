# -*- coding: utf-8 -*-
"""
Módulo de drop de ficheros sobre un widget
"""

from qgis.PyQt.QtGui import QDropEvent, QDragEnterEvent, QDragMoveEvent, QDragLeaveEvent
from qgis.PyQt.QtCore import QObject, pyqtSignal, QUrl

import os

class QvDropFiles(QObject):
    """Permite recibir a un widget cualquiera una lista de ficheros procedente de
       un drag&drop. Se puede definir dos listas de extensiones de archivos:
       - La primera especifica las extensiones permitidas si se quiere recibir un solo archivo
       - La segunda enunera las extensiones permitidas para poder recibir varios archivos
    """

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
        """ Comprueba si se han definido las listas de extensiones de archivos que permiten que
        funcione el filtro del drag&drop

        Returns:
            Bool -- Drop activo o no
        """
        if self.extsUn or self.extsMolts:
            return True
        else:
            return False

    def llistesExts(self, extsUn=None, extsMolts=None):
        """Define las listas de extensiones para único fichero o multiples ficheros

        Keyword Arguments:
            extsUn {[string]} -- Extensiones permitidas para archivo único (default: {None})
            extsMolts {[string]} -- Extensiones permitidas para varios archivos (default: {None})
        """
        if extsUn is None:
            extsUn = []
        if extsMolts is None:
            extsMolts = []
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
        """Sobreescritura de evento de entrada de drag. Realiza el filtro de extensiones
        de archivo, según sean para uno o para varios

        Arguments:
            event {QDragEnterEvent} -- Evento
        """
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
        """Sobreescritura de evento de movimiento de drag. Se actúa solo si se pasó el filtro
        en dragEnterEvent

        Arguments:
            event {QDragMoveEvent} -- Evento
        """
        if self.dropping:
            event.acceptProposedAction()
        else:
            self.widgetDragMoveEvent(event)

    def dragLeaveEvent(self, event):
        """Sobreescritura de evento de abandonar de drag. Se actúa solo si se pasó el filtro
        en dragEnterEvent

        Arguments:
            event {QDragLeaveEvent} -- Evento
        """
        if self.dropping:
            event.accept()
        else:
            self.widgetDragLeaveEvent(event)

    def dropEvent(self, event):
        """Sobreescritura de evento de drop. Se actúa solo si se pasó el filtro en dragEnterEvent

        Arguments:
            event {QDropEvent} -- Evento
        """
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
