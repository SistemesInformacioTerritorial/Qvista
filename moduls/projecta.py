# coding:utf-8

from moduls.QvImports import *
import random
from moduls.QvPushButton import QvPushButton

adreca_test = "D:/qVista_tests/Dades/Projectes/prova2.qgs"

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
        time.sleep(3)
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
        print("FADING")
        
        self.resize(new_widget.size())
        self.show()
        app.processEvents()
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0,0,self.old_pixmap)
        painter.end()
    
    def animate(self, value):
    
        self.pixmap_opacity = 1.0 - value
        self.repaint()

class StackedWidget(QStackedWidget):

    def __init__(self, parent = None):
        QStackedWidget.__init__(self, parent)
        self.index = True
    
    def setCurrentIndex(self, index):
        
        print("index ",index)
        print("current ", self.currentWidget())
        print("new ", self.widget(index))
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def canviPagina(self):
        for i in range (1,5):
            if self.index:
                self.setCurrentIndex(0)
                print("de 0 a 1")
                self.index = not self.index
                widgetP2.actualitzaVista()
            else:
                self.setCurrentIndex(1)
                print("de 1 a 0")
                self.index = not self.index
                widgetP1.actualitzaVista()
            app.processEvents()
            time.sleep(3)
            print(i)

    def setPage1(self):
        self.setCurrentIndex(0)
        widgetP2.actualitzaVista()
        self.setCurrentIndex(1)
        widgetP1.actualitzaVista()
        self.setCurrentIndex(0)
        widgetP2.actualitzaVista()
        self.setCurrentIndex(1)
        widgetP1.actualitzaVista()
        print("---------")
    
    def setPage2(self):
        if self.index:
            self.setCurrentIndex(1)    
            self.index = not self.index
        else:
            self.setCurrentIndex(0)    
            self.index = not self.index
            
def seguentProjecte():
    # widgetP1.destroy()
    # widgetP2.destroy()
    # widgetP1 = Projecta(pathCarpeta + "/" + llistaProjectes[punterFitxer])
    # widgetP2 = Projecta(pathCarpeta + "/" + llistaProjectes[punterFitxer])
    # punterFitxer = (punterFitxer + 1) % len(llistaProjectes)
    # stack.addWidget(widgetP1)
    # stack.addWidget(widgetP2)
    # print("gol")
    global punterFitxer 
    widgetAux = Projecta(pathCarpeta + "/" + llistaProjectes[punterFitxer])
    punterFitxer = (punterFitxer + 1) % len(llistaProjectes)

with qgisapp() as app:

    finestraPrincipal = QMainWindow()
    
    window = QWidget()


    pathCarpeta = "N:/9SITEB/Publicacions/qVista/CATALEG/Mapes/Urbanisme"
    llistaProjectesGen = os.walk(pathCarpeta)
    llistaProjectes = []
    for root, dirs, files in llistaProjectesGen:
        for name in files:
            if name[-4:] == ".qgs":
                llistaProjectes.append(name)

    punterFitxer = 0


    stack = StackedWidget()
    widgetP1 = Projecta("D:/qVista_tests/Dades/Projectes/prova2.qgs")
    widgetP2 = Projecta("D:/qVista_tests/Dades/Projectes/prova2.qgs")
    stack.addWidget(widgetP1)
    stack.addWidget(widgetP2)

    page = QvPushButton("Canvi Pàgina")
    page.clicked.connect(stack.canviPagina)

    page1Button = QvPushButton("Page 1")
    page2Button = QvPushButton("Page 2")
    page3Button = QvPushButton("Seguent Projecte")
    page1Button.clicked.connect(stack.setPage1)
    page2Button.clicked.connect(stack.setPage2)
    page3Button.clicked.connect(seguentProjecte)
    
    layout = QGridLayout(window)
    layout.addWidget(stack, 0, 0, 1, 2)
    layout.addWidget(page)

    layout.addWidget(page1Button)
    layout.addWidget(page2Button)
    layout.addWidget(page3Button)

    finestraPrincipal.setCentralWidget(window)
    finestraPrincipal.showMaximized()

    # lastChange = time.time() 
    # i = 0
    # while i < 5:
    #     if time.time() > lastChange + 2:
    #         print(time.time())
    #         print(lastChange + 2)
    #         stack.canviPagina()
    #         lastChange = time.time()
    #         i = i + 1
    # #widgetP.canvas.zoomScale(500)
    #widgetP.actualitzaVista()