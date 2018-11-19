# -*- coding: utf-8 -*-

from qgis.gui import QgsMapCanvas

class QvVistaMapa(QgsMapCanvas):
    def __init__(self, llegenda):
        super().__init__()
        self.llegenda = llegenda
        self.canvas = llegenda.canvas
        self.llegenda.mapBridge(self)
        self.tema = ''
        self.factorEscala = 1.0
        self.llegenda.project.readProject.connect(self.nouProjecte)
        self._bloqueo = False

    def temes(self):
        return llegenda.temes()

    def nouProjecte(self, doc):
        self.activaTema()

    def connectaExtensio(self):
        if not self._bloqueo:
            self._bloqueo = True
            self.setRotation(self.canvas.rotation())
            self.setExtent(self.canvas.extent())
            self.zoomScale(self.canvas.scale() * self.factorEscala)
            self.setCenter(self.canvas.center())
            self._bloqueo = False

    def connectaCanvas(self):
        self.canvas.extentsChanged.connect(self.connectaExtensio)
        self.canvas.scaleChanged.connect(self.connectaExtensio)
        self.canvas.rotationChanged.connect(self.connectaExtensio)
        self.connectaExtensio()

    def activaTema(self, tema = ''):
        self.tema = tema
        self.setTheme(tema)

    def connectaTema(self, tema = '', factorEscala = 1.0):
        self.activaTema(tema)
        self.factorEscala = factorEscala
        self.connectaCanvas()

if __name__ == "__main__":
    
    from qgis.core import QgsProject
    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsMapCanvas
    from qgis.PyQt.QtWidgets import QMessageBox
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvAtributs import QvAtributs
    from qgis.PyQt.QtCore import QTranslator, QLocale, QLibraryInfo, QSettings
    
    with qgisapp() as app:
 
        # Internacionalización

        lang = 'ca'

        # qtTranslator = QTranslator()
        # path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        # qtTranslator.load("qt_" + lang, path)
        # app.installTranslator(qtTranslator)

        qgisTranslator = QTranslator()
        path = app.i18nPath()
        path = path.replace('/./', '/')
        qgisTranslator.load("qgis_" + lang, path)
        app.installTranslator(qgisTranslator)

        canvas = QgsMapCanvas()

        atributs = QvAtributs(canvas)

        llegenda = QvLlegenda(canvas, atributs)

        # Antes de abrir el proyecto
        vista1 = QvVistaMapa(llegenda)
        vista2 = QvVistaMapa(llegenda)

        llegenda.project.read('../dades/projectes/Illes.qgs')

        print(llegenda.temes())

        # Vistas

        vista1.connectaTema('Mapa1')
        vista2.connectaTema(factorEscala = 0.2)

        # Ventanas

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 25, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 25, 900, 400)
        canvas.show()

        vista1.setWindowTitle('Vista (' + vista1.tema + ')')
        vista1.setGeometry(50, 460, 600, 300)
        vista1.show()

        vista2.setWindowTitle('Vista (Factor Escala = ' + str(vista2.factorEscala) + ')')
        vista2.setGeometry(700, 460, 600, 300)
        vista2.show()

        # Abrimos una tabla de atributos
        # layer = llegenda.capaPerNom('Illes')
        # atributs.obrirTaula(layer)

        atributs.setWindowTitle('Atributs')
        atributs.setGeometry(100, 100, 1050, 600)
        llegenda.obertaTaulaAtributs.connect(atributs.show)



