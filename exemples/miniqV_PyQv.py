from qgis.core.contextmanagers import qgisapp
from moduls.QvApp import QvApp
from moduls.QvCanvas import QvCanvas
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
from moduls.QvDropFiles import QvDropFiles

projecteInicial = 'MapesOffline/qVista default map.qgs'

with qgisapp() as app:

    canvas = QvCanvas()
    QvApp().mainApp = canvas

    atributos = QvAtributs(canvas)
    leyenda = QvLlegenda(canvas, atributos)
    project = leyenda.project
    project.readProject.connect(lambda: canvas.setWindowTitle('Canvas - ' + project.fileName()))
    leyenda.readProject(projecteInicial)

    drop = QvDropFiles(canvas, ['.qgs', '.qgz'])
    drop.arxiusPerProcessar.connect(lambda lista: leyenda.readProject(lista[0]))

    canvas.show()
    leyenda.show()

