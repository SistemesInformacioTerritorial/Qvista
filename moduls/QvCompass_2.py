from moduls.QvImports  import *
from qgis.core import QgsRectangle
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from configuracioQvista import *
from PyQt5.QtWidgets import QFrame, QSpinBox, QLineEdit
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon
import numpy as np


# https://wiki.python.org/moin/PyQt/Compass%20widget


class QvCompass(QFrame):
    
    angleChanged = pyqtSignal(float)
    """La classe que defineix "el Compass"  que controla un canvas."""
    def __init__(self, canvas,  pare = None):
        """Inicialització del Compass.
        
        Arguments:
            QFrame {[self]} -- [QvCompass]
            canvas {[QgsMapCanvas]} -- [El canvas que gesrtionarà el mapeta.]
        
        Keyword Arguments:
           
            pare {[QWidget]} -- [El widget sobre el que es pintarà el mapeta. No és obligatori.] (default: {None})
        """

        QFrame.__init__(self)

        # Assigno el mapeta al parent  JNB
        self.setParent(pare)
        self.pare = pare

        self._angle = 0.0
        self.position_old = QPoint(0,0)

        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S",
                           225: "SO", 270: "O", 315: "NO"}

        self.canvas=canvas
        self.setParent(pare)
        self.pare= pare
        self.colorMarcasCompass= QColor(243,90,14)

 
        # Dimensions i fons del mapeta segosn si és gran o petit
        # atencion
        # self.xTamany = 150
        # self.yTamany = 150     

        self.xTamany = 500
        self.yTamany = 500   
        # Definim la geometria del frame del mapeta
        # self.setGeometry(20,20,self.xTamany,self.yTamany)
        self.setGeometry(0,0,self.xTamany,self.yTamany)
        # self.setStyleSheet('''border-image: url("imagen.jpg")'''
        # atencion
        # self.setStyleSheet('QFrame {opacity: 0; background-image: url("D:/qVista/mio/tra/base_redonda.png");}')

        self.begin = QPoint()
        self.end = QPoint()
        self.setToolTip('Doble click per angle 0')

       
        self.spinBox = QDoubleSpinBox(self)
        self.spinBox.setGeometry(100,133,50,17)
        self.spinBox.setRange(0, 359.999)
        self.spinBox.setSingleStep(0.5)
        
        self.spinBox.valueChanged.connect(self.setAngle)
        self.spinBox.setDecimals(1)
        # self.spinBox.show()
        self.spinBox.hide()
    
    def drawMarkings(self, painter):
        """
        Las referencias
        """
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)

        painter.scale(scale, scale)
        
        font = QFont(self.font())
        # font.setPixelSize(10)
        font.setPixelSize(5)
        metrics = QFontMetricsF(font)
        painter.setFont(font)

        painter.setPen(self.colorMarcasCompass)
        i = 0
        while i < 360:
            if i % 45 == 0:
                painter.drawLine(0, -48, 0, -50)

                painter.drawText(-metrics.width(self._pointText[i])/2.0, -52,
                                 self._pointText[i])
            else:
                # painter.drawLine(0, -45, 0, -50)
                pass
            painter.rotate(15)
            i += 15       
        painter.restore()

    def drawNeedle(self, painter):
        """
        Aguja, (fondo y punta)
        """
    
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        painter.setPen(QPen(Qt.NoPen))

        painter.setBrush(self.palette().brush(QPalette.Shadow))
        painter.drawPolygon(
            QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0),
                        QPoint(0, 45), QPoint(-10, 0)])
            )
        

        # painter.setBrush(self.palette().brush(QPalette.Highlight))
        painter.setBrush(self.colorMarcasCompass)
        painter.drawPolygon(
            # QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
            #             QPoint(0, -30), QPoint(-5, -25)])
            QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0),
                        QPoint(-10,0)])            
            )
        
        painter.restore()



    def paintEvent(self, event):
        # print("paintEvent")
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # painter.fillRect(event.rect(), self.palette().brush(QPalette.Window))
        self.drawMarkings(painter) # resto
        self.drawNeedle(painter)   # aguja
        
        painter.end()        

    def dobleClick(self):
        angulo=0
        self.setAngle(angulo)
        self.spinBox.setValue(angulo)
        self.position_old =QPoint(0,0)


    def gestionoPnt(self, data):
        # print("Compass >> gestionoPnt>>",data)   

        self.position = data

        lin=QLine(self.position, self.position_old)
        if abs(lin.dx())<=1 and abs(lin.dy())<=1:
            self.dobleClick()
        else:
            xcent= self.width()/2;  ycent= self.height()/2
            # p0 = [xcent, ycent-150]
            p0 = [xcent, 0]
            p1 = [xcent, ycent]
            p2 = [self.position.x(), self.position.y()]

            ''' 
            compute angle (in degrees) for p0p1p2 corner
            Inputs:
                p0,p1,p2 - points in the form of [x,y]
            '''
            v0 = np.array(p0) - np.array(p1);   v1 = np.array(p2) - np.array(p1)
            angulo= np.degrees(np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1)))
            if angulo < 0:
                angulo= 360+angulo

            self.setAngle(angulo)
            self.spinBox.setValue(angulo)

        self.position_old = self.position



    def mousePressEvent(self, event):
       if event.buttons() & Qt.LeftButton:
            self.position = QPoint( event.pos().x(),  event.pos().y())

            lin=QLine(self.position, self.position_old)
            if abs(lin.dx())<=1 and abs(lin.dy())<=1:
                self.dobleClick()
            else:
                xcent= self.width()/2;  ycent= self.height()/2
                # p0 = [xcent, ycent-150]
                p0 = [xcent, 0]
                p1 = [xcent, ycent]
                p2 = [self.position.x(), self.position.y()]

                ''' 
                compute angle (in degrees) for p0p1p2 corner
                Inputs:
                    p0,p1,p2 - points in the form of [x,y]
                '''
                v0 = np.array(p0) - np.array(p1);   v1 = np.array(p2) - np.array(p1)
                angulo= np.degrees(np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1)))
                if angulo < 0:
                    angulo= 360+angulo

                self.setAngle(angulo)
                self.spinBox.setValue(angulo)

            self.position_old = self.position
            # self.lineEdit.setText(angulo)



    
    # def reciboPnt(self,pnt):
    #     print("en compass, recibo pnt")

    def mouseMoveEvent(self, event):
        # print("mouseMoveEvent")
        pass

    def enterEvent(self, event):
        """
        Cursor entra en area mapeta\n
        Pongo cursor cruz
        """
        self.setCursor(QCursor(QPixmap(imatgesDir+'/cruz.cur')))     

    def leaveEvent(self, event):
        # print("leaveEvent")
        pass


    def mouseReleaseEvent(self, event):
        # print("mouseReleaseEvent")
        pass
    def sizeHint(self):
        return QSize(150, 150)
    
    def angle(self):
        return self._angle

    # def kk(self):
    #     print("kk")
    
    @pyqtSlot(float)
    def setAngle(self, angle):
        if angle != self._angle:
            self._angleOld= self._angle
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()
            self.canvas.setRotation(self._angle)
            self.canvas.refresh()
    
    angle = pyqtProperty(float, angle, setAngle)

        

import math

if __name__ == "__main__":

    with qgisapp() as app:

        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
     
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)
        project = QgsProject.instance()
        projecteInicial='D:/qVista/Codi/mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
            qvCompass = QvCompass(canvas,  pare=canvas)
            qvCompass.show()


        else:
            print("error en carga del proyecto qgis")
