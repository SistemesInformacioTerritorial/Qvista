# coding:utf-8

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

from moduls.QvPushButton import QvPushButton


# class PointTool(qgGui.QgsMapTool):
#     def __init__(self, parent, canvas):
#         qgGui.QgsMapTool.__init__(self, canvas)
#         self.parent = parent
#         self.moureBoto = False
#         self.canvas = canvas
#         self.a = qgCor.QgsTextAnnotation()
#         self.c = qtGui.QTextDocument()
#         self.puntOriginal = qgCor.QgsPointXY()
#         self.xInici = 0
#         self.yInici = 0

#     def canvasPressEvent(self, event):
#         self.puntOriginal = self.toMapCoordinates(event.pos())
#         self.pOriginal = event.pos()
#         self.xInici = self.pOriginal.x()
#         self.yInici = self.pOriginal.y()
#         # print (self.xInici, self.yInici)

#         self.a = qgCor.QgsTextAnnotation()
#         self.c = qtGui.QTextDocument()

#         self.c.setHtml(self.parent.entradaText.toPlainText())
#         self.a.setDocument(self.c)

#         self.layer = qgCor.QgsVectorLayer('Point?crs=epsg:25831', "RectanglePrint", "memory")
#         qgCor.QgsProject().instance().addMapLayer(self.layer)
#         self.a.setFrameSize(qtCor.QSizeF(100, 50))
#         self.a.setMapLayer(self.layer)
#         self.a.setFrameOffsetFromReferencePoint(qtCor.QPointF(30, 30))
#         self.a.setMapPosition(self.puntOriginal)
#         self.a.setMapPositionCrs(qgCor.QgsCoordinateReferenceSystem(25831))

#         self.i = qgGui.QgsMapCanvasAnnotationItem(self.a, self.canvas)  # ???
#         # print ('press')

#     def canvasMoveEvent(self, event):
#         self.puntFinal = event.pos()

#         xFinal = self.puntFinal.x()
#         yFinal = self.puntFinal.y()

#         self.deltaX = xFinal - self.xInici
#         self.deltaY = yFinal - self.yInici

#         self.a.setFrameOffsetFromReferencePoint(qtCor.QPointF(self.deltaX, self.deltaY))

#     def canvasReleaseEvent(self, event):
#         self.point = self.toMapCoordinates(event.pos())

#         xMon = self.point.x()  # ???
#         yMon = self.point.y()  # ???

#         self.a = qgCor.QgsTextAnnotation()
#         self.c = qtGui.QTextDocument()

#         self.c.setHtml(self.parent.entradaText.toPlainText())
#         self.a.setDocument(self.c)


class QvAnotacionsPunt(qgGui.QgsMapToolEmitPoint):
    def __init__(self, parent, canvas):
        qgGui.QgsMapToolEmitPoint.__init__(self, canvas)
        self.parent = parent
        self.canvas = canvas
        self.project = qgCor.QgsProject.instance()
        self.point = None

    def canvasPressEvent(self, event):
        self.point = self.toMapCoordinates(self.canvas.mouseLastXY())
        print('({:.4f}, {:.4f})'.format(self.point[0], self.point[1]))
        self.a = qgCor.QgsTextAnnotation()
        self.c = qtGui.QTextDocument(self.parent.entradaText.toPlainText())

        # self.c.setHtml(self.parent.entradaText.toPlainText())
        self.a.setDocument(self.c)
        self.a.setFrameSizeMm(qtCor.QSizeF(36, 12))

        # self.a.setMapLayer(self.layer)
        # self.a.setFrameOffsetFromReferencePointMm(qtCor.QPointF(6, 2))
        # self.a.setFrameOffsetFromReferencePointMm(qtCor.QPointF(0, 1))
        # self.a.setFrameOffsetFromReferencePointMm(qtCor.QPointF(-3, 3))

        self.a.setMapPosition(self.point)
        # self.a.setMapPositionCrs(qgCor.QgsCoordinateReferenceSystem(25831))

        self.project.annotationManager().addAnnotation(self.a)
        qgGui.QgsMapCanvasAnnotationItem(self.a, self.canvas)

        # for nota in self.canvas.annotationItems():
        #     nota.deleteLater()
        # for nota in self.project.annotationManager().cloneAnnotations():
        #     qgGui.QgsMapCanvasAnnotationItem(nota, self.canvas)
        # self.canvas.refresh()


class QvAnotacions(qtWdg.QWidget):
    def __init__(self, canvas):
        qtWdg.QWidget.__init__(self)
        self.layout = qtWdg.QVBoxLayout(self)
        self.setLayout = self.layout

        self.setWindowTitle('Anotacions')
        self.canvas = canvas
        # self.pt = PointTool(self, self.canvas)
        self.pt = QvAnotacionsPunt(self, self.canvas)
        self.canvas.setMapTool(self.pt)
        self.entradaText = qtWdg.QTextEdit()
        self.entradaText.show()
        self.botoBorrar = QvPushButton('Esborrar anotacions')
        self.botoBorrar.clicked.connect(self.esborrarAnotacions)
        self.layout.addWidget(self.entradaText)
        self.layout.addWidget(self.botoBorrar)

    def esborrarAnotacions(self):
        pass


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda
    import configuracioQvista as cfg

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        # canv = qgGui.QgsMapCanvas()
        canv = QvCanvas()

        leyenda = QvLlegenda(canv)

        anotacions = QvAnotacions(canv)

        leyenda.project.read(cfg.projecteInicial)

        canv.setWindowTitle('Canvas')
        canv.show()

        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

        anotacions.show()
