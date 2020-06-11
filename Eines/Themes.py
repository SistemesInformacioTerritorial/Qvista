# -*- coding: utf-8 -*-

import configuracioQvista
from qgis.core import QgsRectangle
from qgis.core import QgsProject, QgsLayerTreeModel
from qgis.gui import QgsLayerTreeView
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtWidgets import QFrame, QSpinBox, QLineEdit, QApplication, QHBoxLayout,QColorDialog
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QSize, QTimer
from time import sleep
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QDockWidget, QTreeView

import win32api
import sys
import os
from moduls.QvImports  import *
import math


class Qv_ControlesThemes(QWidget):
    """Clase para:\n

    * Gestionar themes (añadir, quitar, ver catalogo) de un proyecto y 
    * Asignarlos a canvas principal y auxiliar
    """
    def __init__(self):        
        """
        Definición de botones, combo, lineedit.... 
        """
        self.color= QColor(121,144,155)
        self.tempdir=configuracioQvista.tempdir 
        QWidget.__init__(self)

        # region Definición de botones  y componentes
        self.botoTocanvasPral = QPushButton("TocanvasPral")
        self.botoTocanvasPral.clicked.connect(self.TocanvasPral)
        self.botoTocanvasPral.setFixedWidth(85) 
        self.botoTocanvasPral.setToolTip("Aplicar CurrentTheme a canvas principal")

        self.botoToCanvasAux = QPushButton('ToCanvasAux')
        self.botoToCanvasAux.clicked.connect(self.ToCanvasAux)
        self.botoToCanvasAux.setFixedWidth(85) 
        self.botoToCanvasAux.setToolTip("Aplicar CurrentTheme a canvas auxiliar")

        self.botoGuardar = QPushButton('SaveTheme')
        self.botoGuardar.clicked.connect(self.Guardar)
        self.botoGuardar.setFixedWidth(85)  
        self.botoGuardar.setToolTip("Guardar CurrentTheme en catalogo") 

        self.comboThemes = QComboBox()
        self.comboThemes.setToolTip("Ver catalogo de themes") 

        coleccionThemes = project.mapThemeCollection()
        themesDeColeccion = coleccionThemes.mapThemes()
        self.comboThemes.addItems(themesDeColeccion)
        self.comboThemes.currentTextChanged.connect(self.on_combobox_changed)

        self.botoSav = QPushButton('SaveProj')
        self.botoSav.clicked.connect(self.SaveProject)
        self.botoSav.setFixedWidth(85)   
        self.botoSav.setToolTip("Salvar proyecto Qgis") 
        
        self.botoDel = QPushButton('DelTheme')
        self.botoDel.clicked.connect(self.DelTheme)
        self.botoDel.setFixedWidth(85) 
        self.botoDel.setToolTip("Eliminar tema de catalogo") 

        self.botoClear = QPushButton('ResetThemes')
        self.botoClear.clicked.connect(self.ClearTheme)
        self.botoClear.setFixedWidth(85)    
        self.botoClear.setToolTip("Quitar themes de canvas") 

        self.botoShowCanvasAux = QPushButton('ShwCanvasAux')
        self.botoShowCanvasAux.clicked.connect(self.ShowCanvasAux)
        self.botoShowCanvasAux.setFixedWidth(85)                 
        self.botoShowCanvasAux.setToolTip("Mostrar/Ocultar canvas auxiliar") 

        self.eti = QLineEdit()
        try:
            self.eti.setText(self.comboThemes.currentText())
        except Exception as ee:
            self.eti.setText('NOM_THEME')
        
        self.eti.setFixedWidth(100)
        self.eti.setToolTip("CurrentTheme (selección desde combo o propuesto por usuario)") 

        # endregion Definición de botones y componentes
        self.layGrid=QGridLayout()
        # region Botones en GridLayout
        self.layGrid.setColumnStretch(1, 1);
        self.layGrid.addWidget(self.comboThemes,0,0)
        self.layGrid.addWidget(self.eti,0,1) 
        self.layGrid.addWidget(self.botoTocanvasPral,1,0)
        self.layGrid.addWidget(self.botoToCanvasAux,1,1)
        self.layGrid.addWidget(self.botoGuardar,2,0)
        self.layGrid.addWidget(self.botoDel,2,1)
        self.layGrid.addWidget(self.botoClear,3,0)
        self.layGrid.addWidget(self.botoSav,3,1)        
        self.layGrid.addWidget(self.botoShowCanvasAux,4,0)
        # endregion Botones en GridLayout
        self.setLayout(self.layGrid)
    def ShowCanvasAux(self):
        '''
        Muestra/oculta canvas auxiliar
        '''
        if dwCanvasAux.isHidden():
            dwCanvasAux.show()
        else:
            dwCanvasAux.hide()
    def on_combobox_changed(self):
        self.eti.setText(self.comboThemes.currentText())
    def DelTheme(self):
        """Borra de catalogo el Theme current (está en lineedit)
        """
        coleccionThemes = project.mapThemeCollection()
        coleccionThemes.removeMapTheme(self.eti.text())
        self.comboThemes.clear()
        themesDeColeccion = coleccionThemes.mapThemes()
        self.comboThemes.addItems(themesDeColeccion)        
    def TocanvasPral(self):
        """Asigna Theme current a canvas principal
        """
        canvasPral.setTheme(self.eti.text())
        windowTest.setWindowTitle("Canvas principal Theme: " + self.eti.text()) 
    def ToCanvasAux(self):
        """Asigna Theme current a canvas auxiliar
        """
        dwCanvasAux.setWindowTitle("CanvasAux Theme: "+ self.eti.text())
        canvasAux.setTheme(self.eti.text())
    def ClearTheme(self):
        """Limpia canvas principal y auxiliar de Themes.\n
        Se activa de nuevo la leyenda
        """
        canvasPral.setTheme("")   
        canvasAux.setTheme("")  
        dwCanvasAux.setWindowTitle("CanvasAux")  
        windowTest.setWindowTitle("Canvas principal")     
    def Guardar(self):

        # atencion
        # project.mapThemeCollection().appyTheme(tema,self.root,self.llegenda.layerTreeModel()
        """Guardar estado leyenda con el nombre de theme current
        """
        coleccionThemes = project.mapThemeCollection()
        themesDeColeccion = coleccionThemes.mapThemes()

        # print(themesDeColeccion)
        # hay= project.mapThemeCollection().hasMapTheme('DISTRITOS')
        # print(hay)

        root = project.layerTreeRoot() 
        model = QgsLayerTreeModel(root)
        
        themeCreated = coleccionThemes.createThemeFromCurrentState(root, model)
        # for r in themesDeColeccion:
        #     if coleccionThemes.mapThemeState(r) == themeCreated :
        #         print("si: ",r)
        #     else:
        #         print("no: ",r)

        # Se da nombre al theme creado
        coleccionThemes.insert(self.eti.text(),themeCreated)
        self.comboThemes.clear()
        themesDeColeccion = coleccionThemes.mapThemes()
        self.comboThemes.addItems(themesDeColeccion)
    def Ver(self):
        """Ver todos los temas
                """
        coleccionThemes = project.mapThemeCollection()
        themesDeColeccion = coleccionThemes.mapThemes()

        # print(themesDeColeccion)
        # hay= project.mapThemeCollection().hasMapTheme('DISTRITOS')
        # print(hay)


        # root = project.layerTreeRoot() 
        # model = QgsLayerTreeModel(root)
        # # themeCreated= el guardado (o current ? )
        # themeCreated = coleccionThemes.createThemeFromCurrentState(root, model)
        # for r in themesDeColeccion:
        #     if coleccionThemes.mapThemeState(r) == themeCreated :
        #         print("si: ",r)
        #     else:
        #         print("no: ",r)
        # coleccionThemes.insert(self.eti.text(),themeCreated)
        print(coleccionThemes.mapThemes())
    def SaveProject(self):
        """Save pro
        """
        try:
            project.write()
        except Exception  as ee:
            pass   
            


if __name__ == "__main__":
    def fuerzoCentroAux():
        """[summary]
        """
        print("fuerzoCentroAux")
        
        try:
            centro=canvasPral.center()
            canvasAux.setCenter(centro)
        except Exception as ee:
            print(str(ee))
    def fuerzoCentroPral():
        """[summary]
        """
        print("fuerzoCentroPral")
        try:
            centro=canvasAux.center()
            canvasPral.setCenter(centro)
        except Exception as ee:
            print(str(ee))

    def MeClicaPral(SuId):
        """[summary]

        Args:
            SuId ([type]): [description]
        """

        if SuId == Id_canvasPral:
            SuId ='CanvasPrincipal'
        elif SuId == Id_canvasAux:
            SuId ='CanvasAux'

        print("Themes >> MeClicaPral >> ",SuId)
        # desconecto  respuesta a modificación extensión canvasAux
        try:
            canvasAux.extentsChanged.disconnect()
            print("desconecto fuerzoCentroPral")
        except Exception as ee:
            print(str(ee))
        try:
            canvasPral.extentsChanged.connect(fuerzoCentroAux)  
            print("conecto fuerzoCentroAux")
        except Exception as ee:
            print(str(ee))

    def foo():
        pass

    def MeClicaAux(SuId):
        """[summary]

        Args:
            SuId ([type]): [description]
        """

        if SuId == Id_canvasPral:
            SuId ='CanvasPrincipal'
        elif SuId == Id_canvasAux:
            SuId ='CanvasAux'
        

        print("Themes >> MeClicaAux >> ",SuId)   
        # desconecto  respuesta a modificación extensión canvasPral
        try:
            canvasPral.extentsChanged.disconnect()
            print("desconecto fuerzoCentroAux")
        except Exception as ee:
            print(str(ee))
        try:            
            canvasAux.extentsChanged.connect(fuerzoCentroPral)
            print("conecto fuerzoCentroPral")
        except Exception as ee:
            print(str(ee))
        # conecto respuesta a modificación extension canvasAux --> Ejecutará fuerzoCentroPral

    with qgisapp() as app:
        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
        from qgis.utils import iface
        from moduls.QvAtributs import QvAtributs
        from moduls.QvCanvas import QvCanvas


        canvasPral = QvCanvas()
        # Cuando entra foco en canvasPral ejecutare MeClicaPral gracias a que QvCanvas envia señal
        # diciendo que canvas ha recibido el foco
        canvasPral.Sig_QuienMeClica.connect(MeClicaPral) 

        Id_canvasPral= str(id(canvasPral))   
        print("Themes>> canvasPral id= ",Id_canvasPral)
   
        canvasAux = QvCanvas()

        Id_canvasAux = str(id(canvasAux))
        print("Themes>> canvasAux id= ",Id_canvasAux)
        # 
        # Cuando entra foco en canvasAux ejecutare MeClicaAux
        canvasAux.Sig_QuienMeClica.connect(MeClicaAux)

        atributos1 = QvAtributs(canvasPral)
        atributos2 = QvAtributs(canvasAux)
        project = QgsProject.instance()

        projecteInicial1='./mapesOffline/qVista default map.qgs'
        # projecteInicial2 = os.path.abspath('mapesOffline/00 Mapa TM - Situació rr QPKG.qgs')

        # se carga el proyecto qgs
        if project.read(projecteInicial1):
            
            windowTest = QMainWindow()
            windowTest.setCentralWidget(canvasPral)
            windowTest.setWindowTitle("Canvas principal") 

            leyenda = QvLlegenda(canvasPral, atributos1)
            dwleyenda = QDockWidget( "Leyenda", windowTest )
            dwleyenda.setContextMenuPolicy(Qt.PreventContextMenu)
            dwleyenda.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwleyenda.setContentsMargins ( 1, 1, 1, 1 )
            dwleyenda.setWidget(leyenda)
            windowTest.addDockWidget( Qt.RightDockWidgetArea, dwleyenda)
            dwleyenda.show()  

            # controlesThemes = Qv_ControlesThemes(canvasPral)
            controlesThemes = Qv_ControlesThemes()
            controlesThemes.show()
            dwControles = QDockWidget( "Controles", windowTest )
            dwControles.setContextMenuPolicy(Qt.PreventContextMenu)
            # dwControles.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwControles.setContentsMargins ( 1, 1, 1, 1 )
            dwControles.setWidget(controlesThemes)
            dwControles.show()  #atencion            
            windowTest.addDockWidget( Qt.RightDockWidgetArea, dwControles)

            dwCanvasAux = QDockWidget( "CanvasAux", windowTest )
            dwCanvasAux.setContextMenuPolicy(Qt.PreventContextMenu)
            # dwCanvasAux.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwCanvasAux.setContentsMargins ( 1, 1, 1, 1 )
            dwCanvasAux.setWidget(canvasAux) 
            canvasAux.show()  #jnb
            dwCanvasAux.hide()
            windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwCanvasAux)
          
            windowTest.show()
        else:
            print("error en carga del proyecto qgis")



# hay= project.mapThemeCollection().hasMapTheme('DISTRITOS')
# print(project.mapThemeCollection().mapThemes())
# # https://es.gisq.net/q/como-leer-que-tema-de-mapa-se-usa-en-qgis-3-17830
       

# https://python.hotexamples.com/examples/qgis.gui/QgsMapCanvas/resize/python-qgsmapcanvas-resize-method-examples.html
        
# https://gis.stackexchange.com/questions/138266/getting-a-layer-that-is-not-active-with-pyqgis
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/cheat_sheet.html
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/composer.html#simple-rendering
# https://gis.stackexchange.com/questions/189735/iterating-over-layers-and-export-them-as-png-images-with-pyqgis-in-a-standalone           
