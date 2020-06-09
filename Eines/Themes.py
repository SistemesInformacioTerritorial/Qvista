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

class Qv_prueba(QWidget):
    '''
    '''
    def __init__(self, canvas,pare=None):
        '''
        '''
        self.canvas=canvas
        self.color= QColor(121,144,155)
        self.tempdir=configuracioQvista.tempdir 
        QWidget.__init__(self)
        # self.dadesdir=configuracioQvista.dadesdir
        self.setParent(pare)
        self.pare = pare


        #defino botones y las funciones de su click
        self.botoToCanvas1 = QPushButton("ToCanvas1")
        self.botoToCanvas1.clicked.connect(self.ToCanvas1)
        self.botoToCanvas1.setFixedWidth(60) 
        self.botoToCanvas1.setToolTip("Aplicar CurrentTheme a canvas principal")

        self.botoToCanvas2 = QPushButton('ToCanvas2')
        self.botoToCanvas2.clicked.connect(self.ToCanvas2)
        self.botoToCanvas2.setFixedWidth(60) 
        self.botoToCanvas2.setToolTip("Aplicar CurrentTheme a canvas auxiliar")

        self.botoGuardar = QPushButton('Guardar')
        self.botoGuardar.clicked.connect(self.Guardar)
        self.botoGuardar.setFixedWidth(60)  
        self.botoGuardar.setToolTip("Guardar CurrentTheme en catalogo") 

        self.botoVer = QPushButton('Ver')
        self.botoVer.clicked.connect(self.Ver)
        self.botoVer.setFixedWidth(60) 
        self.botoVer.setToolTip("Ver catalogo de themes")   

        self.comboVer = QComboBox()
        self.comboVer.setToolTip("Ver catalogo de themes") 

        mTC = project.mapThemeCollection()
        mTs = mTC.mapThemes()
        self.comboVer.addItems(mTs)
        self.comboVer.currentTextChanged.connect(self.on_combobox_changed)


        self.botoSav = QPushButton('SaveProj')
        self.botoSav.clicked.connect(self.SaveProject)
        self.botoSav.setFixedWidth(60)   
        self.botoSav.setToolTip("Salvar proyecto Qgis") 

        
        self.botoDel = QPushButton('DelTheme')
        self.botoDel.clicked.connect(self.DelTheme)
        self.botoDel.setFixedWidth(60) 
        self.botoDel.setToolTip("Eliminar tema de catalogo") 

        self.botoClear = QPushButton('ResetTheme')
        self.botoClear.clicked.connect(self.ClearTheme)
        self.botoClear.setFixedWidth(60)    
        self.botoClear.setToolTip("Quitar themes de canvas") 

        self.botoShowCanvas2 = QPushButton('ShwCan2')
        self.botoShowCanvas2.clicked.connect(self.ShowCanvas2)
        self.botoShowCanvas2.setFixedWidth(60)                 
        self.botoShowCanvas2.setToolTip("Mostrar/Ocultar canvas auxiliar") 

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

        self.layGrid.addWidget(self.botoToCanvas1,1,0)
        self.layGrid.addWidget(self.botoToCanvas2,1,1)

        
        self.layGrid.addWidget(self.botoGuardar,2,0)
        self.layGrid.addWidget(self.botoDel,2,1)
        
        self.layGrid.addWidget(self.botoClear,3,0)
        self.layGrid.addWidget(self.botoSav,3,1)        

        self.layGrid.addWidget(self.botoShowCanvas2,4,0)

        
   
        self.setLayout(self.layGrid)

    def ShowCanvas2(self):
        if dwCanvas2.isHidden():
            dwCanvas2.show()
        else:
            dwCanvas2.hide()



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


    def ToCanvas1(self):
        """To canvas 1
        """
        canvas1.setTheme(self.eti.text())
        windowTest.setWindowTitle("Canvas principal Theme: " + self.eti.text()) 

    def ToCanvas2(self):
        """To canvas2
        """
        dwCanvas2.setWindowTitle("Canvas2 Aux Theme: "+ self.eti.text())
        canvas2.setTheme(self.eti.text())

    def ClearTheme(self):
        """To canvas2
        """
        canvas1.setTheme("")   
        canvas2.setTheme("")  
        dwCanvas2.setWindowTitle("Canvas2 Aux")  
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

    with qgisapp() as app:
        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
        from qgis.utils import iface
        from moduls.QvAtributs import QvAtributs
        from moduls.QvCanvas import QvCanvas

     
        # Canvas, projecte i bridge
        # canvas=QgsMapCanvas()
        canvas1=QvCanvas()
        canvas2=QvCanvas()
       
        canvas1.show()
        # canvas2.show()
        # canvas1.setTheme("DISTRITOS")

        atributos1 = QvAtributs(canvas1)
        atributos2 = QvAtributs(canvas2)
        project = QgsProject.instance()

        projecteInicial1='./mapesOffline/qVista default map.qgs'
        # projecteInicial2 = os.path.abspath('mapesOffline/00 Mapa TM - Situació rr QPKG.qgs')

        # se carga el proyecto qgs
        if project.read(projecteInicial1):
            
            
            windowTest = QMainWindow()
            windowTest.setCentralWidget(canvas1)
            windowTest.setWindowTitle("Canvas principal") 

            leyenda1 = QvLlegenda(canvas1, atributos1)
            # leyenda1.show()

            leyenda2 = QvLlegenda(canvas2, atributos2)
            # leyenda2.show()

            dwleyenda = QDockWidget( "Leyenda", windowTest )
            dwleyenda.setContextMenuPolicy(Qt.PreventContextMenu)
            dwleyenda.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwleyenda.setContentsMargins ( 1, 1, 1, 1 )
            
            dwleyenda.setWidget(leyenda1)

            # Coloquem el dockWidget al costat esquerra de la finestra

            windowTest.addDockWidget( Qt.RightDockWidgetArea, dwleyenda)
            # Fem visible el dockWidget
            dwleyenda.show()  #atencion

            # Instanciamos la classe QvcrearMapetaConBotones
            caso_canvas1 = Qv_prueba(canvas1)
            caso_canvas1.show()

            # Creem un dockWdget i definim les característiques
            dwcaso_canvas1 = QDockWidget( "Controles", windowTest )
            dwcaso_canvas1.setContextMenuPolicy(Qt.PreventContextMenu)
            dwcaso_canvas1.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwcaso_canvas1.setContentsMargins ( 1, 1, 1, 1 )
            dwcaso_canvas1.setWidget(caso_canvas1)

            windowTest.addDockWidget( Qt.RightDockWidgetArea, dwcaso_canvas1)
            dwcaso_canvas1.show()  #atencion            
            
            dwCanvas2 = QDockWidget( "Canvas2 Aux", windowTest )
            
            dwCanvas2.setContextMenuPolicy(Qt.PreventContextMenu)
            dwCanvas2.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwCanvas2.setContentsMargins ( 1, 1, 1, 1 )
            dwCanvas2.setWidget(canvas2) 
            dwCanvas2.hide()

            windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwCanvas2)
          
            # dwCanvas2.show()

            canvas1.show()
            # canvas2.show()

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
