from qgis.core.contextmanagers import qgisapp
from qgis.PyQt.QtWidgets import QStatusBar, QLineEdit, QMainWindow, QLabel, QProgressBar, QMessageBox, QMenu, QAction, QCompleter
from qgis.core import QgsProject, QgsPointXY
from qgis.gui import QgsLayerTreeMapCanvasBridge
from qgis.PyQt.QtCore import pyqtSignal, QPoint, Qt, QStringListModel
from qgis.PyQt.QtGui import QFontMetrics, QIntValidator
from pathlib import Path
from moduls.QvCanvas import QvCanvas
from moduls.QvAtributs import QvAtributs
from moduls.QvLlegenda import QvLlegenda
from moduls.QvApp import QvApp
from moduls.QvConstants import QvConstants
import configuracioQvista

# Stylesheet dels widgets de la statusbar
# Donat que és un f-string, quan vulguem posar un '{' o '}' haurem de posar-lo duplicat
STYLESHEET = f'''
    QWidget {{
        font-size: 15px;
        border: 1px solid {QvConstants.COLORGRISHTML};
        margin: 0px;
        padding: 2px;
    }}
    QLabel {{
        background-color: {QvConstants.COLORBLANCHTML};
        color: {QvConstants.COLORFOSCHTML};
    }}
    QLineEdit[text=""] {{
        color: {QvConstants.COLORTEXTHINTHTML};
    }}
    QProgressBar{{
        background: transparent;
    }}
'''
class QvLineEditPS(QLineEdit):
    def __init__(self, *args, prefix='', sufix='', **kwargs):
        super().__init__(*args, **kwargs)
        self.text_ = self.text
        self.text = self.textNet
        self.prefix = prefix
        self.sufix = sufix
        self.setText(self.textComplet())
        self.textEdited.connect(self.on_text_changed)
    def focusInEvent(self,e):
        self.setText(self.text())
        super().focusInEvent(e)

        # quan entrem a començar a editar, el completer mostrarà totes les possibilitats
        self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        # self.completer().complete()
    def focusOutEvent(self,e):
        self.setText(self.textComplet())
        super().focusOutEvent(e)
        self.parentWidget().setFocus()
    def on_text_changed(self,text):
        # a la que haguem modificat el text, el completer només mostrarà els textos que encaixin amb allò
        # si resulta que està buit, forcem que es mostrin tots. Si no, comportament normal
        self.setText(self.text())
        self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion if text=='' else QCompleter.PopupCompletion)
        if text=='':
            self.completer().complete()
    def textNet(self):
        try:
            return self.text_().removeprefix(self.prefix).removesuffix(self.sufix)
        except:
            # encara no tenim Python 3.9
            text = self.text_()
            if text.startswith(self.prefix) and self.prefix!='':
                text = text[len(self.prefix):]
            if text.endswith(self.sufix) and self.sufix!='':
                text = text[:-len(self.sufix)]
            return text
    def textComplet(self):
        return self.prefix+self.text()+self.sufix
    def setContingut(self, cont):
        self.setText(cont)
        self.setText(self.textComplet())
    def setPrefix(self, prefix):
        self.prefix = str(prefix)
        self.updateGeometry()
    def setSufix(self,sufix):
        self.sufix = str(sufix)
        self.updateGeometry()

class QvStatusBar(QStatusBar):
    coordsCanviades = pyqtSignal(float, float)
    expressioInferior = pyqtSignal(str)
    def __init__(self, parent, llistaWidgets=[], canvas=None, llegenda=None):
        super().__init__(parent)
        parent.setStatusBar(self)
        self.setSizeGripEnabled(True)

        self.canvas = canvas
        self.llegenda = llegenda

        self.escalaQgis = False

        self.setStyleSheet(STYLESHEET)
        self.setFont(QvConstants.FONTTEXT)

        for x in llistaWidgets:
            if not isinstance(x, str):
                try:
                    x, stretch = x
                except ValueError as e:
                    raise ValueError('La llista de Widgets pot rebre 1 o 2 valors, però no més')
            else:
                stretch = 0
            if x == 'nomProjecte':
                wid = QLabel(f'QGS: {Path(QgsProject.instance().fileName()).stem}', self)
                wid.setToolTip(f'{Path(QgsProject.instance().fileName())}')
                QgsProject.instance().readProject.connect(self.canviPathProjecte)
                nomWid = 'lblProjecte'
            elif x == 'connexio':
                wid = QLabel(configuracioQvista.estatConnexio, self)
                nomWid = 'lblConnexio'
            elif x == 'capaSeleccionada':
                wid = QLabel('No hi ha capa activa', self)
                self.llegenda.currentLayerChanged.connect(self.canviLayer)
                nomWid = 'lblCapaSeleccionada'
            elif x == 'seleccioExpressio':
                wid = QLineEdit(self)
                wid.returnPressed.connect(self.seleccioExpressio)
                wid.setPlaceholderText('Introduïu un text per filtrar elements a la capa seleccionada')
                nomWid = 'leSeleccioExpressio'
            elif x == 'progressBar':
                wid = QProgressBar(self)
                self.canvas.renderStarting.connect(self.showPB)
                self.canvas.renderComplete.connect(self.hidePB)
                wid.setRange(0,0)
                nomWid = 'sbCarregantCanvas'
            elif x == 'coordenades':
                wid = QLineEdit(self.getXY(self.canvas.center()),self)
                self.fixaMidaNecessariaLE(wid)
                self.canvas.xyCoordinates.connect(self.showXY)
                wid.returnPressed.connect(self.returnEditarXY)
                nomWid = 'leXY'
            elif x == 'projeccio':
                wid = QLabel(QgsProject.instance().crs().description(),self)
                QgsProject.instance().readProject.connect(lambda: self.lblProjeccio.setText(QgsProject.instance().crs().description()))
                nomWid = 'lblProjeccio'
            elif x == 'escala':
                wid = QvLineEditPS(prefix='Escala 1:', parent=self)
                wid.setValidator(QIntValidator(wid))
                self.canvas.scaleChanged.connect(self.setEscala)
                wid.returnPressed.connect(self.escalaEditada)
                QgsProject.instance().readProject.connect(self.actualitzaEscales)
                try:
                    self.escalesPossibles = list(map(str,self.llegenda.escales.llistaCb))
                except:
                    self.escalesPossibles = []
                self.completerEscales = QCompleter(self.escalesPossibles, wid)
                wid.setCompleter(self.completerEscales)
                # self.completerEscales.highlighted.connect(self.completerEscales.widget().clearFocus)

                self.menuEscala = QMenu()
                accioEscalaNormal = QAction('Escala',self)
                accioEscalaNormal.triggered.connect(self.setEscalaNormal)
                accioEscalaQGIS = QAction('Escala QGIS',self)
                accioEscalaQGIS.triggered.connect(self.setEscalaQGIS)
                self.menuEscala.addAction(accioEscalaNormal)
                self.menuEscala.addAction(accioEscalaQGIS)
                wid.setContextMenuPolicy(Qt.CustomContextMenu)
                wid.customContextMenuRequested.connect(self.on_context_menu_escala)
                nomWid = 'leEscala'
            else:
                # llençar excepció
                continue
            wid.setFont(QvConstants.FONTTEXT)
            self.afegirWidget(nomWid, wid, stretch)
    def actualitzaEscales(self):
        try:
            self.escalesPossibles = list(map(str,self.llegenda.escales.llistaCb))
            self.showXY(self.canvas.center())
        except:
            self.escalesPossibles = []
        # self.completerEscales = QCompleter(self.escalesPossibles, self.leEscala)
        self.completerEscales.setModel(QStringListModel(self.escalesPossibles,self.completerEscales))
        self.leEscala.setCompleter(self.completerEscales)
        pass
    def afegirWidget(self, nom, wid, stretch=0, posicio=None):
        # insertar a la posició -1 faria que s'insertés al final, però surt un warning per la terminal
        # Per tant, fem un cas especial
        if posicio==None:
            self.addPermanentWidget(wid, stretch)
        else:
            self.insertPermanentWidget(posicio, wid, stretch)
        setattr(self,nom, wid)
        wid.setStyleSheet(STYLESHEET)
        # wid.setStyleSheet(f'QLabel, QLineEdit{{border: 4px solid {QvConstants.COLORGRISHTML}}}')
    def canviPathProjecte(self):
        self.lblProjecte.setText(f'QGS: {Path(QgsProject.instance().fileName()).stem}')
        self.lblProjecte.setToolTip(f'{Path(QgsProject.instance().fileName())}')
    def canviLayer(self):
        layer = self.llegenda.currentLayer()
        if layer is not None:
            self.lblCapaSeleccionada.setText(f'Capa activa: {layer.name()}')
        else:
            self.lblCapaSeleccionada.setText('No hi ha capa activa')
    
    def setEscalaNormal(self):
        self.leEscala.setPrefix('Escala 1: ')
        self.escalaQgis = False
        self.fixaMidaNecessariaLE(self.leEscala)
        self.corrijoScale()
    def setEscalaQGIS(self):
        self.leEscala.setPrefix('Escala QGIS 1: ')
        self.escalaQgis = True
        self.fixaMidaNecessariaLE(self.leEscala)
        self.canvas.setMagnificationFactor(1)
    def on_context_menu_escala(self, point):
        self.menuEscala.exec_(self.leEscala.mapToGlobal(point))
    # Funció de JNB, originalment a qVista.py, migrada aquí
    def corrijoScale(self):
        import math

        def distancia(p1,p2):
            return ((p2.x-p1.x)**2+(p2.y-p1.y)**2)**0.5
    
        def DetectoCuadrante():
            """
            Retorno el cuadrante en que está el angulo de rotacion
            4  |  1
            3  |  2
            """
            Cuadrante=0
            if 0 <= self.canvas.rotation() <=90:             Cuadrante=1
            elif 90 < self.canvas.rotation() <= 180:         Cuadrante=2
            elif 180 < self.canvas.rotation() <= 270:        Cuadrante=3
            elif 270 < self.canvas.rotation() <= 360:        Cuadrante=4
            else:                                            Cuadrante= -1
            return Cuadrante    

        self.Cuadrante = DetectoCuadrante()

        PPa1=QPoint(); PPa2=QPoint(); PPa3=QPoint();  PPa4=QPoint()  # mundo 
        Pa1=QPoint();  Pa2=QPoint();  Pa3=QPoint();  Pa4=QPoint()   # mundo
        rect = self.canvas.extent()
        PPa1.x= rect.xMinimum();    PPa1.y= rect.yMinimum()   # abajo izquierda
        PPa3.x= rect.xMaximum();    PPa3.y= rect.yMaximum()   # arriba derecha
        PPa2.x=  PPa3.x;            PPa2.y=  PPa1.y           # abajo derecha
        PPa4.x=  PPa1.x;            PPa4.y=  PPa3.y           # arriba izquierda
        anchoMundoAzul= (PPa3.x - PPa1.x);    altoMundoAzul=  (PPa3.y - PPa1.y)
        w= self.canvas.widthMM();              h= self.canvas.heightMM()
        angulo= self.canvas.rotation()
        self.seno_giro= math.sin(math.radians(angulo))
        self.coseno_giro= math.cos(math.radians(angulo))
        self.seno_antigiro= math.sin(math.radians(360 - angulo))
        self.coseno_antigiro= math.cos(math.radians(360 - angulo))   

        if (self.Cuadrante == 1) or (self.Cuadrante == 3): 
            if self.Cuadrante == 1:  
                self.seno_giro_c= math.sin(math.radians(angulo))
                self.coseno_giro_c= math.cos(math.radians(angulo))
            elif (self.Cuadrante == 3): 
                self.seno_giro_c= math.sin(math.radians(angulo-180) )
                self.coseno_giro_c= math.cos(math.radians(angulo-180))          
            h1= (w*self.seno_giro_c)
            h2= (h*self.coseno_giro_c)
            w1= (w*self.coseno_giro_c)
            w2= (h*self.seno_giro_c) 
        elif (self.Cuadrante == 2) or (self.Cuadrante == 4):  
            if self.Cuadrante == 2:  
                self.seno_giro_c= math.sin(math.radians(angulo-90))
                self.coseno_giro_c= math.cos(math.radians(angulo-90))
            elif (self.Cuadrante == 4): 
                self.seno_giro_c= math.sin(math.radians(angulo-270) )
                self.coseno_giro_c= math.cos(math.radians(angulo-270))
            h1= (w*self.coseno_giro_c)
            h2= (h*self.seno_giro_c)
            w1= (h*self.coseno_giro_c)
            w2= (w*self.seno_giro_c)
        
        W = w1 + w2 ;                  H = h1 + h2   
        Escalax= anchoMundoAzul / W;   Escalay= altoMundoAzul /  H 

        if (self.Cuadrante ==1) or (self.Cuadrante ==3):
            Pa1.x = PPa1.x;                    Pa1.y = PPa1.y + Escalay * h2  
            Pa2.x = PPa4.x + Escalax * w1;     Pa2.y = PPa4.y                  
            Pa3.x = PPa2.x;                    Pa3.y = PPa2.y + Escalay * h1  
            # Pa4.x = PPa1.x + Escalax * w2;     Pa4.y = PPa1.y 
        elif (self.Cuadrante ==2)  or (self.Cuadrante ==4):
            Pa1.x = PPa2.x;                    Pa1.y = PPa2.y + Escalay * h1
            Pa2.x = PPa1.x + Escalax * w1;     Pa2.y = PPa1.y             
            Pa3.x = PPa1.x;                    Pa3.y = PPa1.y + Escalay * h2   
            # Pa4.x = PPa4.x + Escalax * w2;     Pa4.y = PPa4.y    

  
        incMy= distancia(Pa2,Pa3)
        incPy= self.canvas.heightMM()
        EsY=  incMy  / incPy*   1000

        incMx= distancia(Pa1,Pa2)
        incPx=  self.canvas.widthMM()
        EsX=  incMx / incPx * 1000  # esta es la buena

        factorX= EsX /self.canvas.scale()
        factorY= EsY /self.canvas.scale()
        # print(factorX,factorY)  
        factor=  (factorY + factorX)/2    
        self.canvas.setMagnificationFactor(factor * self.canvas.magnificationFactor())
    def setEscala(self, escala):
        self.leEscala.setContingut(f'{round(escala)}')
        if not self.escalaQgis:
            self.corrijoScale()
        self.fixaMidaNecessariaLE(self.leEscala)
    
    def escalaEditada(self):
        escala = self.leEscala.text()
        self.canvas.zoomScale(int(escala))
    def seleccioExpressio(self):
        command=self.leSeleccioExpressio.text().lower()
        if command == 'help':
            self.infoQVista()
        elif command == 'mapificacio':
            from moduls.QvMapForms import QvFormNovaMapificacio
            QvFormNovaMapificacio.executa(self.llegenda)
        elif command == 'carrilsbici':
            from moduls.QvVistacad import QvVistacad
            QvVistacad.carregaProjecte('341')
        elif command == 'vistacad':
            from moduls.QvVistacad import QvVistacad
            QvVistacad.formulariProjectes()
        elif command == 'masklabels':
            self.llegenda.setMask(self.llegenda.capaPerNom("MaskLabels"), 1)
        elif command == 'qvtemps':
            QMessageBox.information(self,'Temps per arrancar:', str('%.1f'%self.tempsTotal))
        # elif command=='mascara':
        #     self.emmascaraDivisions=True
        # elif command=='filtramascara':
        #     filtraMascara(self)
        elif command in ('versio', 'versió'):
            QMessageBox.information(self,'Versió de QGIS',f'La versió de QGIS actual és la {QvApp().versioQgis()}')
        elif command == 'afegircatalegcapes':
            self.afegirCataleg()
        else:
            layer=self.llegenda.currentLayer()
            if layer is not None:
                textCercat=""
                layer=self.llegenda.currentLayer()
                if layer is not None:
                    if self.leSeleccioExpressio.text()!='':
                        for field in layer.fields():
                            if field.typeName()=='String' or field.typeName()=='text'  or field.typeName()[0:4]=='VARC':
                                textCercat = textCercat + field.name()+" LIKE '%" + self.leSeleccioExpressio.text()+ "%'"
                                textCercat = textCercat + ' OR '
                        textCercat=textCercat[:-4]
                    # layer.setSubsetString(textCercat)
                    layer.selectByExpression(textCercat)
                    self.llegenda.actIconaFiltre(layer)
                    # ids = [feature.id() for feature in layer.getFeatures()]
                    # self.canvas.zoomToFeatureIds(layer, ids)
                    if layer.selectedFeatureCount() != 0:
                        self.canvas.setExtent(layer.boundingBoxOfSelected())
            else:
                QMessageBox.warning(self,'Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
        self.expressioInferior.emit(command)
    @staticmethod
    def fixaMidaNecessariaLE(le):
        if isinstance(le, QvLineEditPS):
            text = le.textComplet()
        else:
            text = le.text()
        font = le.font()
        fm = QFontMetrics(font)
        le.setFixedWidth(fm.width(text)*QvApp().zoomFactor())
    def showPB(self):
        self.sbCarregantCanvas.show()
    def hidePB(self):
        self.sbCarregantCanvas.hide()
    def getXY(self, p, numDec=3):
        text = QvApp().locale.toString(p.x(), 'f', numDec) + ';' + \
                QvApp().locale.toString(p.y(), 'f', numDec)
        return text
    def showXY(self, p, numDec=3):
        try:
            text = self.getXY(p,numDec)
            self.leXY.setText(text)
            self.fixaMidaNecessariaLE(self.leXY)
            # font=QvConstants.FONTTEXT
            # fm=QFontMetrics(font)
            # self.leXY.setFixedWidth(fm.width(text)*QvApp().zoomFactor())
        except Exception as e:
            pass
    def returnEditarXY(self):
        coords = self.leXY.text().split(';')
        if len(coords) == 2:
            x, xOk = QvApp().locale.toFloat(coords[0])
            y, yOk = QvApp().locale.toFloat(coords[1])
            if xOk and yOk:
                self.canvas.setCenter(QgsPointXY(x, y))
                self.canvas.refresh()
                self.coordsCanviades.emit(x, y)
                return
        print('ERROR >> Coordenades mal escrites')

if __name__=='__main__':
    with qgisapp() as app:
        canvas = QvCanvas(['centrar','zoomIn','zoomOut','panning'], posicioBotonera='SE', botoneraHoritzontal=True)
        atributs = QvAtributs(canvas)
        llegenda = QvLlegenda(canvas, atributs)
        root = QgsProject.instance().layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        QgsProject.instance().read('MapesOffline/qVista default map.qgs')

        win = QMainWindow()
        win.setCentralWidget(canvas)
        win.setStatusBar(QvStatusBar(win,['nomProjecte', 'connexio','capaSeleccionada',('seleccioExpressio',1), 'progressBar',('coordenades',1),'projeccio', 'escala'],canvas,llegenda))
        win.show()
        llegenda.show()