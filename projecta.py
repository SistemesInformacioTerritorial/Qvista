# coding:utf-8

from moduls.QvImports import *
import random

adreca_test = "D:/colegis3.qgs"

class Projecta(QWidget):
    def __init__(self, adreca_proj = adreca_test):
        QWidget.__init__(self)
        self.adreca_projecte = adreca_proj
        self.carregaProjecte()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
        # self.boto1 = QPushButton()
        # self.boto1.setText("testeja escala")
        # self.layout.addWidget(self.boto1)
        # self.boto1.clicked.connect(self.actualitzaVista)

    def carregaProjecte(self):
        self.canvas = QgsMapCanvas()
        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.bridge = QgsLayerTreeMapCanvasBridge(self.root,self.canvas)
        self.bridge.setCanvasLayers()
        self.project.read(self.adreca_projecte)

    def actualitzaVista(self):
        #self.carregaProjecte()
        
        escala = random.random() * 30000 + 500
        posX = random.uniform(426000.0,433973.0)
        posY = random.uniform(4578800.0,4588525.0)
        punt = QgsPointXY(posX,posY)
        
        self.canvas.setCenter(punt)
        self.canvas.zoomScale(escala)
        self.canvas.refresh()
        app.processEvents()
        #self.size = canvas.size()
        #self.image = QImage(size, QImage.Format_RGB32)
    
    def modeAleatori(self):
        self.lastChange = time.time()
        i = 0
        while i < 5:
            if time.time() > self.lastChange + 2:
                self.actualitzaVista
                self.lastChange = time.time()
                i = i + 1
        
class FaderWidget(QWidget):

    def __init__(self, old_widget, new_widget):
    
        QWidget.__init__(self, new_widget)
        
        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.5
        
        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(1000)
        self.timeline.start()
        
        self.resize(new_widget.size())
        self.show()
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()
    
    def animate(self, value):
    
        self.pixmap_opacity = 1.0 - value
        self.repaint()

class StackedWidget(QStackedWidget):

    def __init__(self, parent = None):
        QStackedWidget.__init__(self, parent)
        self.index = True
    
    def setCurrentIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def canviPagina(self):
        for i in range (1,5):
            time.sleep(5)
            if self.index:
                self.setCurrentIndex(1)
                self.index = not self.index
                widgetP1.actualitzaVista()
            else:
                self.setCurrentIndex(0)
                self.index = not self.index
                widgetP2.actualitzaVista()

            


with qgisapp() as app:

    finestraPrincipal = QMainWindow()
    widgetP1 = Projecta("D:/colegis3.qgs")
    widgetP2 = Projecta("D:/colegis3.qgs")
    #widgetP1.modeAleatori()

    window = QWidget()
    
    stack = StackedWidget()
    stack.addWidget(widgetP1)
    stack.addWidget(widgetP2)

    page1Button = QPushButton("Canvi Pàgina")
    page1Button.clicked.connect(stack.canviPagina)
    
    layout = QGridLayout(window)
    layout.addWidget(stack)
    layout.addWidget(page1Button)

    finestraPrincipal.setCentralWidget(window)
    finestraPrincipal.showMaximized()

    lastChange = time.time() 

    #widgetP.canvas.zoomScale(500)
    #widgetP.actualitzaVista()