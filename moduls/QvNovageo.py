import sys
from qgis.core import    QgsProject, QgsVectorLayer, QgsLayoutExporter, QgsPointXY, QgsGeometry, QgsVector, QgsLayout, QgsReadWriteContext
from qgis.gui import QgsMapCanvas,QgsLayerTreeMapCanvasBridge,  QgsVertexMarker
# import pickle
from collections import deque
import os.path
from qgis.core.contextmanagers import qgisapp


from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QPushButton, QDockWidget
from PyQt5.QtCore import Qt

from  Ui_NG_Consultes import *       # Todas las consultas..
from  Ui_NG_Selec_adreca import *    # Pide calle y numero
from  Ui_NG_Adreca import *
from moduls.QVCercadorAdreca import QCercadorAdreca



projecteInicial='mapesOffline/qVista default map.qgs'

global vial, numero


class QvNovageo(QtWidgets.QWidget, Ui_Form):
    """  

    """
    def __init__(self, canvas, pare = None):
        """[summary]
        Arguments:
            canvas {[QgsMapCanvas]} -- [El canvas que es vol gestionar]

        """
        self.pare= pare
        self.canvas = canvas
        QWidget.__init__(self)
        self.setupUi(self)

        # self.abrirBBDD()

        # ventana peticion direccion
        self.pushButton_10.clicked.connect(self.adreces)
        # ventana peticion calle
        self.pushButton_7.clicked.connect(self.vials)


        self.dialogAdreces = QDialog()
        self.dialogAdreces.ui = Ui_Dialog()
        self.dialogAdreces.ui.setupUi(self.dialogAdreces)
        self.dialogAdreces.ui.buttonBox.accepted.connect(self.accepAdress1)
        self.dialogAdreces.ui.buttonBox.rejected.connect(self.rejectAdress1)




        self.dialogConsultaAdreces = QDialog()
        self.dialogConsultaAdreces.ui = Ui_DialogConsultaAdreca()
        self.dialogConsultaAdreces.ui.setupUi(self.dialogConsultaAdreces)
        self.dialogConsultaAdreces.ui.buttonBox.accepted.connect(self.accepAdress)
        self.dialogConsultaAdreces.ui.buttonBox.rejected.connect(self.rejectAdress)

        self.cAdrec=QCercadorAdreca(self.dialogConsultaAdreces.ui.leVial, self.dialogConsultaAdreces.ui.leNumero,'SQLITE')    # SQLITE o CSV
          
        # self.cAdrec.sHanTrobatCoordenades.connect(self.trobatNumero_oNo) 
        self.cAdrec.sHanTrobatCoordenades.connect(self.kk) 


    def kk(self):   
        pass

    # def abrirBBDD(self):
    #     pass
       


       
    def accepAdress(self):
        print('acepto')  

        self.dialogAdreces.show()
        self.dialogAdreces.ui.lineEdit_15.setText('kk')





    
    def accepAdress1(self):
        print('acepto1')
 

    def rejectAdress1(self):
        print('No acepto1')
            


    def rejectAdress(self):
        print('No acepto')



    def adreces(self):
        self.dialogConsultaAdreces.show()



    def vials(self):
        print('vials')        







        
    



# Demo d'ús quan es crida el fitxer de la classe per separat
if __name__ == "__main__":
    
    with qgisapp() as app:
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        # canvas.show()
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)

        # Instanciem la classe QvNovageo
        Novageo = QvNovageo(canvas)

        """
        Amb aquesta linia:
        Novageo.show()
        es veuria el widget suelto, separat del canvas.

        Les següents línies mostren com integrar el widget 'Novageo' com a dockWidget.
        """
        
        windowTest = QMainWindow()

        # Posem el canvas com a element central
        windowTest.setCentralWidget(canvas)

        # Creem un dockWdget i definim les característiques
        dwNovageo = QDockWidget( "Consultas Novageo", windowTest )
        dwNovageo.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        dwNovageo.setContentsMargins ( 1, 1, 1, 1 )

        # Afegim el widget Novageo al dockWidget
        dwNovageo.setWidget(Novageo)

        # Coloquem el dockWidget al costat esquerra de la finestra
        windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwNovageo)

        # Fem visible el dockWidget
        dwNovageo.show()  #atencion


        # Fem visible la finestra principal
        canvas.show()
        windowTest.show()


        pass  




        