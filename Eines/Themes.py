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
    '''
    '''
    def __init__(self):        
        '''
        '''
        self.color= QColor(121,144,155)
        self.tempdir=configuracioQvista.tempdir 
        QWidget.__init__(self)

        #defino botones y las funciones de su click
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

        # self.botoVer = QPushButton('Ver')
        # self.botoVer.clicked.connect(self.Ver)
        # self.botoVer.setFixedWidth(85) 
        # self.botoVer.setToolTip("Ver catalogo de themes")   

        self.comboVer = QComboBox()
        self.comboVer.setToolTip("Ver catalogo de themes") 

        mTC = project.mapThemeCollection()
        mTs = mTC.mapThemes()
        self.comboVer.addItems(mTs)
        self.comboVer.currentTextChanged.connect(self.on_combobox_changed)

        self.botoSav = QPushButton('SaveProj')
        self.botoSav.clicked.connect(self.SaveProject)
        self.botoSav.setFixedWidth(85)   
        self.botoSav.setToolTip("Salvar proyecto Qgis") 
        
        self.botoDel = QPushButton('DelTheme')
        self.botoDel.clicked.connect(self.DelTheme)
        self.botoDel.setFixedWidth(85) 
        self.botoDel.setToolTip("Eliminar tema de catalogo") 

        self.botoClear = QPushButton('ResetTheme')
        self.botoClear.clicked.connect(self.ClearTheme)
        self.botoClear.setFixedWidth(85)    
        self.botoClear.setToolTip("Quitar themes de canvas") 

        self.botoShowCanvasAux = QPushButton('ShwCanvasAux')
        self.botoShowCanvasAux.clicked.connect(self.ShowCanvasAux)
        self.botoShowCanvasAux.setFixedWidth(85)                 
        self.botoShowCanvasAux.setToolTip("Mostrar/Ocultar canvas auxiliar") 

        self.eti = QLineEdit()
        try:
            self.eti.setText(self.comboVer.currentText())
        except Exception as ee:
            self.eti.setText('NOM_THEME')
        
        self.eti.setFixedWidth(100)
        self.eti.setToolTip("CurrentTheme (selección desde combo o propuesto por usuario)") 
        self.layGrid=QGridLayout()
        self.layGrid.setColumnStretch(1, 1);
        self.layGrid.addWidget(self.comboVer,0,0)
        self.layGrid.addWidget(self.eti,0,1) 
        self.layGrid.addWidget(self.botoTocanvasPral,1,0)
        self.layGrid.addWidget(self.botoToCanvasAux,1,1)
        self.layGrid.addWidget(self.botoGuardar,2,0)
        self.layGrid.addWidget(self.botoDel,2,1)
        self.layGrid.addWidget(self.botoClear,3,0)
        self.layGrid.addWidget(self.botoSav,3,1)        
        self.layGrid.addWidget(self.botoShowCanvasAux,4,0)
        self.setLayout(self.layGrid)
    def ShowCanvasAux(self):
        if dwCanvasAux.isHidden():
            dwCanvasAux.show()
        else:
            dwCanvasAux.hide()
    def on_combobox_changed(self):
        self.eti.setText(self.comboVer.currentText())
    def DelTheme(self):
        mTC = project.mapThemeCollection()
        mTs = mTC.mapThemes()

        
        mTC.removeMapTheme(self.eti.text())
        print(mTC.mapThemes())
        self.comboVer.clear()

        mTs = mTC.mapThemes()
        self.comboVer.addItems(mTs)        
    def TocanvasPral(self):
        """To canvas 1
        """
        canvasPral.setTheme(self.eti.text())
        windowTest.setWindowTitle("Canvas principal Theme: " + self.eti.text()) 
    def ToCanvasAux(self):
        """To canvasAux
        """
        dwCanvasAux.setWindowTitle("CanvasAux Aux Theme: "+ self.eti.text())
        canvasAux.setTheme(self.eti.text())
    def ClearTheme(self):
        """To canvasAux
        """
        canvasPral.setTheme("")   
        canvasAux.setTheme("")  
        dwCanvasAux.setWindowTitle("CanvasAux Aux")  
        windowTest.setWindowTitle("Canvas principal")     
    def Guardar(self):
        """Guardar
        """
        mTC = project.mapThemeCollection()
        mTs = mTC.mapThemes()

        # print(mTs)
        # hay= project.mapThemeCollection().hasMapTheme('DISTRITOS')
        # print(hay)

        root = project.layerTreeRoot() 
        model = QgsLayerTreeModel(root)
        # goodTheme= el guardado (o current ? )
        goodTheme = mTC.createThemeFromCurrentState(root, model)
        # for r in mTs:
        #     if mTC.mapThemeState(r) == goodTheme :
        #         print("si: ",r)
        #     else:
        #         print("no: ",r)
        mTC.insert(self.eti.text(),goodTheme)
        print(mTC.mapThemes())
        self.comboVer.clear()

        mTs = mTC.mapThemes()
        self.comboVer.addItems(mTs)
    def Ver(self):
        """Ver todos los temas
                """
        mTC = project.mapThemeCollection()
        mTs = mTC.mapThemes()

        # print(mTs)
        # hay= project.mapThemeCollection().hasMapTheme('DISTRITOS')
        # print(hay)


        # root = project.layerTreeRoot() 
        # model = QgsLayerTreeModel(root)
        # # goodTheme= el guardado (o current ? )
        # goodTheme = mTC.createThemeFromCurrentState(root, model)
        # for r in mTs:
        #     if mTC.mapThemeState(r) == goodTheme :
        #         print("si: ",r)
        #     else:
        #         print("no: ",r)
        # mTC.insert(self.eti.text(),goodTheme)
        print(mTC.mapThemes())
    def SaveProject(self):
        """Save pro
        """
        try:
            project.write()
        except Exception  as ee:
            pass   
            


if __name__ == "__main__":
    def cambio1():
        """[summary]
        """
        print("cambio1")
        
        try:
            centro=canvasPral.center()
            canvasAux.setCenter(centro)
        except Exception as ee:
            print(str(ee))
    def cambio2():
        """[summary]
        """
        print("cambio2")
        try:
            centro=canvasAux.center()
            canvasPral.setCenter(centro)
        except Exception as ee:
            print(str(ee))
    def MeClica1(SuId):
        """[summary]

        Args:
            SuId ([type]): [description]
        """
        print("Themes >> MeClica1 >> ",SuId)
        # desconecto  respuesta a modificación extensión canvasAux
        try:
            canvasAux.extentsChanged.disconnect(cambio2)
            print("desconecto cambio2")
        except Exception as ee:
            print(str(ee))
        try:
            canvasPral.extentsChanged.connect(cambio1)  
            print("conecto cambio1")
        except Exception as ee:
            print(str(ee))


    def MeClica2(SuId):
        """[summary]

        Args:
            SuId ([type]): [description]
        """

        print("Themes >> MeClica2 >> ",SuId)   
        # desconecto  respuesta a modificación extensión canvasPral
        try:
            canvasPral.extentsChanged.disconnect(cambio1)
            print("desconecto cambio1")
        except Exception as ee:
            print(str(ee))
        try:            
            canvasAux.extentsChanged.connect(cambio2)
            print("conecto cambio2")
        except Exception as ee:
            print(str(ee))
        # conecto respuesta a modificación extension canvasAux --> Ejecutará cambio2

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
        # Cuando entra foco en canvasPral ejecutare MeClica1 gracias a que QvCanvas envia señal
        # diciendo que canvas ha recibido el foco
        canvasPral.Sig_QuienMeClica.connect(MeClica1)    
        print("Themes>> canvasPral id= ",str(id(canvasPral)))
        # Id_canvasPral= str(id(canvasPral))
        canvasAux = QvCanvas()
        print("Themes>> canvasAux id= ",str(id(canvasAux)))
        # Id_canvasAux = str(id(canvasAux))
        # Cuando entra foco en canvasAux ejecutare MeClica2
        canvasAux.Sig_QuienMeClica.connect(MeClica2)

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

            dwCanvasAux = QDockWidget( "CanvasAux Aux", windowTest )
            dwCanvasAux.setContextMenuPolicy(Qt.PreventContextMenu)
            # dwCanvasAux.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwCanvasAux.setContentsMargins ( 1, 1, 1, 1 )
            dwCanvasAux.setWidget(canvasAux) 
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
