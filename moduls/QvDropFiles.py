# -*- coding: utf-8 -*-
"""
Módulo de drop de ficheros sobre un widget
"""

from qgis.PyQt.QtGui import QDropEvent, QDragEnterEvent, QDragMoveEvent, QDragLeaveEvent
from qgis.PyQt.QtCore import QObject, pyqtSignal, QUrl

import os

class QvDropFiles(QObject):
    """Permite que un widget reciba una lista de ficheros procedente de un drag & drop
       Se pueden definir como filtro dos listas de extensiones de archivos:
       - La primera especifica las extensiones permitidas si se quiere recibir un solo archivo
       - La segunda enunera las extensiones permitidas para poder recibir varios archivos

       Dispara una señal cuando se realiza el drop con la lista de ficheros a tratar
    """

    arxiusPerProcessar = pyqtSignal(list)

    def __init__(self, widget, extsUn=None, extsMolts=None):
        """Constructor del objeto que maneja el drop de ficheros

        Arguments:
            widget (QWidget) -- Widget en el que se activará la opción de dropping
            extsUn (List[String]) -- Extensiones permitidas para archivo único (default: None)
            extsMolts (List[String]) -- Extensiones permitidas para varios archivos (default: None)
        """
        QObject.__init__(self)
        self.widget = widget
        self.widget.setAcceptDrops(True)
        self.widgetDragEnterEvent = self.widget.dragEnterEvent
        self.widgetDragMoveEvent = self.widget.dragMoveEvent
        self.widgetDragLeaveEvent = self.widget.dragLeaveEvent
        self.widgetDropEvent = self.widget.dropEvent
        self.llistaArxius = []
        self.dropping = False
        self.llistesExts(extsUn, extsMolts)

    def llistesExts(self, extsUn=None, extsMolts=None):
        """Define las listas de extensiones para único fichero o multiples ficheros

        Arguments:
            extsUn (List[String]) -- Extensiones permitidas para archivo único (default: None)
            extsMolts (List[String]) -- Extensiones permitidas para varios archivos (default: None)
        """
        self.extsUn = extsUn
        if self.extsUn is not None:
            self.extsUn = [x.lower() for x in self.extsUn]
        self.extsMolts = extsMolts
        if self.extsMolts is not None:
            self.extsMolts = [x.lower() for x in self.extsMolts]
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

    def dropActiu(self):
        """Comprueba si se ha definido al menos una de las listas de extensiones de archivos que
        permiten que funcione el filtro del drag & drop

        Returns:
            Bool -- Drop activo o no
        """
        if self.extsUn is None and self.extsMolts is None:
            return False
        else:
            return True

    def dropOk(self, num1, num2):
        """Comprueba si se permite o no el drop de ficheros, verificando si hay uno de la primera
        lista de extensiones o bien uno o varios de la segunda lista

        Arguments:
            num1 (Int) -- Número de ficheros encontrados cuya extensión está en la primera lista
            num2 (Int) -- Número de ficheros encontrados cuya extensión está en la segunda lista

        Returns:
            Bool -- Permite o no el drop de ficheros
        """
        return (num1 == 0 and num2 > 0) or (num1 == 1 and num2 == 0)

    def dragEnterEvent(self, event):
        """Sobreescritura de evento de entrada de drag. Realiza el filtro de extensiones
        de archivo, según sean para uno o para varios

        Arguments:
            event (QDragEnterEvent) -- Evento a manejar
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
                    fext = fext.lower()
                    if self.extsUn is not None and fext in self.extsUn:
                        nUn += 1
                        self.llistaArxius.append(fich)
                    if self.extsMolts is not None and fext in self.extsMolts:
                        nMolts += 1
                        self.llistaArxius.append(fich)
            self.dropping = self.dropOk(nUn, nMolts)
        if self.dropping:
            event.acceptProposedAction()
        else:
            self.widgetDragEnterEvent(event)

    def dragMoveEvent(self, event):
        """Sobreescritura de evento de movimiento de drag. Actúa solo si se pasó el filtro
        en dragEnterEvent

        Arguments:
            event (QDragMoveEvent) -- Evento a manejar
        """
        if self.dropping:
            event.acceptProposedAction()
        else:
            self.widgetDragMoveEvent(event)

    def dragLeaveEvent(self, event):
        """Sobreescritura de evento de abandonar de drag. Actúa solo si se pasó el filtro
        en dragEnterEvent

        Arguments:
            event (QDragLeaveEvent) -- Evento a manejar
        """
        if self.dropping:
            event.accept()
        else:
            self.widgetDragLeaveEvent(event)

    def dropEvent(self, event):
        """Sobreescritura de evento de drop. Actúa solo si se pasó el filtro en dragEnterEvent

        Arguments:
            event (QDropEvent) -- Evento a manejar
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
    from qgis.gui import QgsMapCanvas
    # from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvApp import QvApp

    gui = True
    with qgisapp(guienabled=gui) as app:

    # with qgisapp(sysexit=False) as app:

        qApp = QvApp()
        qApp.carregaIdioma(app, 'ca')

        # 1.- Crear widget donde aplicar el drag & drop de ficheros
        canvas = QgsMapCanvas()
        # 2.- Crear el objeto QvDropFiles pasándole el widget
        drop = QvDropFiles(canvas)
        # 3.- Definir dos listas de extensiones: fichero único (proyecto) o varios ficheros (capas)
        drop.llistesExts(['.QGS', '.qgz'], ['.QLR', '.shp', '.csv'])
        # 4.- Asociar evento de drop a función que maneje la lista de archivos soltados
        drop.arxiusPerProcessar.connect(lambda nomFich: print('Dropped:', nomFich))
        # 5.- El evento recibirá o bien un fichero de la primera lista o varios de la segunda

        llegenda = QvLlegenda(canvas)

        ok = llegenda.project.read('mapesOffline/qVista default map.qgs')

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)
        canvas.show()
