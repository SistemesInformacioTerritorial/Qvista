# coding:utf-8


from moduls.QvEinesGrafiques import QvSeleccioElement
from qgis.PyQt.QtCore import Qt, QSize
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolPan
from qgis.PyQt.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from qgis.PyQt.QtGui import QIcon, QPainter
from moduls.QvImports  import *
from qgis.core.contextmanagers import qgisapp
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvConstants import QvConstants
from moduls.QvStreetView import *
from moduls.QvEinesGrafiques import QvMesuraMultiLinia, QvMascaraEinaPlantilla
from moduls.QvApp import QvApp
import functools
#from qVista import QVista




class QvCanvas(QgsMapCanvas):
    canviMaximitza = pyqtSignal()
    desMaximitza = pyqtSignal()
    mostraStreetView = pyqtSignal()

    Sig_QuienMeClica = pyqtSignal('QString')    #JNB
    
    def __init__(self, pare = None, llistaBotons=['zoomIn', 'zoomOut', 'panning', 'centrar'], botoneraHoritzontal = True, posicioBotonera = 'NO', mapesBase = False, llegenda = None): #mapesBase (???)
        QgsMapCanvas.__init__(self)
        self.botoneraHoritzontal = botoneraHoritzontal
        self.llistaBotons = llistaBotons
        self.posicioBotonera = posicioBotonera
        self.llegenda = llegenda
        self.pare = pare
        # self.setSelectionColor(QvConstants.COLORDESTACAT)
        self.setSelectionColor(QColor('yellow'))
        self.setAcceptDrops(True)
        
        # self.setWhatsThis(QvApp().carregaAjuda(self))

        self._preparacioBotonsCanvas()
        self.eines=[]
        self.einesBotons={}
        if self.llistaBotons is not None:
            self.panCanvas()
            self.panCanvas()
        self.preparacioStreetView()

    def focusInEvent(self,event):  # JNB prueba detectar que canvas tiene foco
        # print("QvCanvas >> focusInEvent "+ str(id(self)))
        self.Sig_QuienMeClica.emit(str(id(self)))

    def keyPressEvent(self, event):
        """ Defineix les actuacions del QvMapeta en funció de la tecla apretada.
        """
        super().keyPressEvent(event)  # Para que los mapTools puedan procesar sus teclas
        if event.key() == Qt.Key_Escape:
            self.desMaximitza.emit()
            if self.pare is not None:
                try:
                    self.pare.esborrarSeleccio(tambePanCanvas = False)
                    self.pare.esborrarMesures(tambePanCanvas = False)
                    self.tool.fitxaAtributs.close()
                except:
                    pass
        if event.key()==Qt.Key_F11:
            self.canviMaximitza.emit()

        if event.key() == Qt.Key_F2:
            self.paradebug()  #JNB pruebas     




    def paradebug(self):
        print(self.magnificationFactor())

    def uncheckBotons(self,aExcepcio):
        for x in self._botons:
            if x is not aExcepcio: 
                x.setChecked(False)
    def panCanvas(self):        # MANO
        # bucle para quitar todos los cursores guardados. quiero que use el que ofrece MapTool
        # while self.pare.app.overrideCursor() != None:
        #     self.pare.app.restoreOverrideCursor()


        if self.bPanning.isChecked():
            self.uncheckBotons(self.bPanning)
           
            self.tool_pan = QgsMapToolPan(self)
            self.einesBotons[self.tool_pan]=self.bPanning
            self.setMapTool(self.tool_pan)


        else: 
            self.bPanning.setChecked(True)

    def amagaStreetView(self):
        self.bstreetview.setChecked(False)

    def centrarMapa(self):
        if self.bCentrar.isChecked():
            self.zoomToFullExtent()
            self.refresh()
        self.bCentrar.setChecked(False)
        # self.bCentrar.setChecked(True)

    def zoomIn(self):
        if self.bZoomIn.isChecked():
            self.uncheckBotons(self.bZoomIn)
           
            self.tool_zoomin = QgsMapToolZoom(self, False)
            self.tool_zoomin.setCursor(QvConstants.cursorZoomIn())
            self.einesBotons[self.tool_zoomin]=self.bZoomIn
            self.setMapTool(self.tool_zoomin)
        else: 
            self.bZoomIn.setChecked(True)
        self.setCursor(QvConstants.cursorZoomIn())

    def zoomOut(self):
        if self.bZoomOut.isChecked():
            self.uncheckBotons(self.bZoomOut)
           
            self.tool_zoomout = QgsMapToolZoom(self, True)
            self.tool_zoomout.setCursor(QvConstants.cursorZoomOut())
            self.einesBotons[self.tool_zoomout]=self.bZoomOut
            self.setMapTool(self.tool_zoomout)
        else: 
            self.bZoomOut.setChecked(True)

        self.setCursor(QvConstants.cursorZoomOut())

    def seleccioClick(self):
        if  self.bApuntar.isChecked():
            self.uncheckBotons(self.bApuntar)

            try:
                self.pare.esborrarSeleccio(tambePanCanvas = False)
                self.pare.esborrarMesures(tambePanCanvas = False)
                self.tool.fitxaAtributs.close()
            except:
                pass

            try:
                self.tool = QvSeleccioElement(self, llegenda = self.llegenda)
                self.tool.setCursor(QvConstants.cursorDit())
                self.einesBotons[self.tool]=self.bApuntar
                self.setMapTool(self.tool)
            except:
                pass
        else:
            self.bApuntar.setChecked(True)
        
        self.setCursor(QvConstants.cursorDit())

    def anotacions(self):
        if self.llegenda.anotacions:
            if  self.bAnotacions.isChecked():
                self.uncheckBotons(self.bAnotacions)
                self.einesBotons[self.llegenda.anotacions]=self.bAnotacions
                # Si estábamos digitalizando, acabar comando
                eina = self.mapTool()
                if self.testDigitizeTool(eina): eina.unset()
                self.setMapTool(self.llegenda.anotacions)
            else: 
                self.bAnotacions.setChecked(True)
        else:
            self.bAnotacions.setChecked(False)
            QMessageBox.information(self,'Atenció',"La gestió d'anotacions només funciona amb versions de QGIS superiors a la 3.10")

    def copyToClipboard(self):
        '''Potser no és la millor manera, però el que fa és desar la imatge temporalment i copiar-la d'allà'''
        nom=os.path.join(tempdir,str(time.time())+'.png')
        self.saveAsImage(nom)
        qApp.clipboard().setImage(QImage(nom))

    def setLlegenda(self, llegenda):
        self.llegenda = llegenda
    def preparacioStreetView(self):
        self.qvSv = QvStreetView(self, self)
        # self.setMapTool(self.qvSv.rp)
        self.qvSv.hide()
    def getStreetView(self):
        return self.qvSv
    def _botoMapa(self,imatge = None):
        boto = QvPushButton(flat=True)
        boto.setStyleSheet('background: rgba(255,255,255,168); padding: 1px;')
        boto.setCheckable(True)
        if imatge is not None:
            icon=QIcon(imatge)
            boto.setIcon(icon)
        boto.setWindowOpacity(0.5)
        boto.setIconSize(QSize(24,24))
        boto.setGeometry(0,0,24,24)
        self._botons.append(boto)
        return boto
    
    def afegirBotoCustom(self, nomBoto, imatge=None, toolTip = None, posicio=-1):
        """Afegeix un botó no estàndard al canvas.

        Si el paràmetre nomBoto té com a valor "botoReset", 
         un cop executada la funció el botó creat estarà a self.botoReset.
         El botó també serà retornat, per poder treballar amb ell

         En cas d'existir ja un atribut amb el nom donat, es provarà d'afegir-lo amb una _ al final
          (en l'exemple, si self.botoReset ja existís es tornaria a provar amb self.botoReset_)

        Args:
            nomBoto (str): Nom de la variable que contindrà el botó
            imatge (str, optional): Ruta de la imatge de la icona. Defaults to None.
            toolTip (str, optional): Tooltip del botó. Defaults to None.
            posicio (int, optional): Posició de la botonera on volem posar-lo. Si no s'especifica, serà al final. Defaults to -1.

        Returns:
            QvPushButton: Botó que s'ha creat
        """
        if hasattr(self,nomBoto):
            return self.afegirBotoCustom(self, nomBoto+'_', imatge, toolTip)
        boto = self._botoMapa(imatge)
        boto.setToolTip(toolTip)
        setattr(self, nomBoto, boto)
        self.layoutBotoneraMapa.insertWidget(posicio, boto)
        return boto

    def _preparacioBotonsCanvas(self):
        self.botoneraMapa = QFrame()

        #self.botoneraMapa.move(90,20)#nofares

        #self.botoneraMapa.setFrameShape(QFrame.StyledPanel)
        #self.botoneraMapa.setFrameShadow(QFrame.Raised)

        if self.botoneraHoritzontal:
            self.layoutCanvas = QVBoxLayout(self)
            self.layoutBotoneraMapa = QHBoxLayout(self.botoneraMapa)
        else:
            self.layoutCanvas = QHBoxLayout(self)
            self.layoutBotoneraMapa = QVBoxLayout(self.botoneraMapa)

        self.layoutCanvas.setContentsMargins(15,15,15,15)
        self.layoutBotoneraMapa.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layoutCanvas) 

        spacer = QSpacerItem(9999, 9999, QSizePolicy.Expanding,QSizePolicy.Maximum)
                    
        self.botoneraMapa.setLayout(self.layoutBotoneraMapa)

        if self.posicioBotonera == 'NE':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignRight) 
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignTop) 
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)  



        if self.posicioBotonera == 'NO':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignLeft)
                self.offsetEsq = QLabel()
                self.offsetEsq.setFixedWidth(200)
                self.offsetUp = QLabel()
                self.offsetUp.setFixedHeight(0)
                self.layoutBotoneraMapa.addWidget(self.offsetEsq)
                # self.layoutCanvas.addWidget(self.offsetUp)
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   
                #self.layoutBotoneraMapa.setAlignment(Qt.AlignLeft)
                #self.layoutCanvas.addWidget(self.botoneraMapa)  
                #self.layoutCanvas.addSpacerItem(spacer)   
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignTop)
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   
                


        if self.posicioBotonera == 'SE':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignRight)
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)  
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignBottom)
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)                


        if self.posicioBotonera == 'SO':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignLeft)
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)  
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignBottom)
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   

            # self.botoneraMapa.setMaximumHeight(25)
            # self.botoneraMapa.setMinimumHeight(25)
            # self.botoneraMapa.setMaximumWidth(9999)
            # self.botoneraMapa.setMinimumWidth(100)

        # configuració dels possibles botons del canvas
        # és un diccionari on les claus són strings identificant el botó, i el valor un diccionari amb la configuració d'aquest botó
        # EXEMPLE:
        # SETUP_BOTONS = {
        #     'apuntar':{
        #         # Si nom_var és 'bApuntar', podrem accedir al botó utilitzant self.bApuntar
        #         # IMPORTANT: si la variable ja existia, se sobreescriurà
        #         'nom_var':'bApuntar', 

        #         # La icona del botó serà {imatgesdir}/apuntar.png
        #         'icona':'apuntar.png', 

        #         # El toolTip del botó
        #         'toolTip':"Veure informació d'un objecte", 

        #         # La funció que es cridarà quan es faci click al botó
        #         # NOTA: la funció s'ha de posar sense els parèntesis
        #         'clicked':self.seleccioClick, 

        #         # [OPCIONAL] indica si el botó es queda marcat quan el prems
        #         # En cas de no posar-ho, per defecte és True
        #         'checkable':True, 

        #         # [OPCIONAL] Una funció que s'executarà després d'haver instanciat el botó. 
        #         # Ens permet configurar coses més concretes
        #         # Per exemple, en el cas del botó de StreetView podem fer que sigui arrossegable fent
        #         #  self.bstreetview.setDragable(True)
        #         'altres': lambda: self.bApuntar.setStyleSheet('background: purple') 
        #     }
        # }
        SETUP_BOTONS = {
            'apuntar':{
                'nom_var':'bApuntar',
                'icona':'apuntar.png', 
                'toolTip':"Veure informació d'un objecte",
                'clicked':self.seleccioClick
            },
            'panning':{
                'nom_var':'bPanning',
                'icona':'pan_tool_black_24x24.png', 
                'toolTip':"Desplaçar el mapa", 
                'clicked':self.panCanvas
            },
            'centrar':{
                'nom_var':'bCentrar',
                'icona':'fit.png', 
                'toolTip':"Enquadrar el mapa complet a la pantalla", 
                'clicked':self.centrarMapa,
                'checkable':False
            },
            'zoomIn':{
                'nom_var':'bZoomIn',
                'icona':'zoom_in.png', 
                'toolTip':'Zoom per apropar-se', 
                'clicked':self.zoomIn
            },
            'zoomOut':{
                'nom_var':'bZoomOut',
                'icona':'zoom_out.png', 
                'toolTip':'Zoom per allunyar-se', 
                'clicked':self.zoomOut
            },
            'enrere':{
                'nom_var':'bEnrere',
                'icona':'qv_vista_anterior.png', 
                'toolTip':'Retrocedir al zoom anterior', 
                'clicked':self.zoomToPreviousExtent,
                'checkable':False
            },
            'endavant':{
                'nom_var':'bEndavant',
                'icona':'qv_vista_seguent.png', 
                'toolTip':'Avançar al zoom següent', 
                'clicked':self.zoomToNextExtent,
                'checkable':False
            },
            'anotacions':{
                'nom_var':'bAnotacions',
                'icona':'anotacions.png', 
                'toolTip':"Gestió d'anotacions", 
                'clicked':self.anotacions
            },
            'streetview':{
                'nom_var':'bstreetview',
                'icona':'littleMan.png', 
                'toolTip':"Google Street view", 
                'clicked':self.anotacions,
                'altres': lambda: self.bstreetview.setDragable(True)
            },
            'maximitza':{
                'nom_var':'bMaximitza',
                'icona':'fullscreen.png', 
                'toolTip':"Pantalla completa (F11)", 
                'clicked':self.canviMaximitza.emit,
                'checkable':False
            },
        }

        if self.llistaBotons is not None:
            self._botons = []
            for x in self.llistaBotons:
                info = SETUP_BOTONS[x]
                boto = self._botoMapa(os.path.join(imatgesDir,info['icona']))
                setattr(self, info['nom_var'], boto)
                boto.setToolTip(info['toolTip'])
                boto.setCursor(QvConstants.cursorFletxa())
                boto.clicked.connect(info['clicked'])
                if 'checkable' in info: boto.setCheckable(info['checkable'])
                if 'altres' in info: info['altres']()
                self.layoutBotoneraMapa.addWidget(boto)
                self._botons.append(boto)
        # spacer = QSpacerItem(0, 50, QSizePolicy.Expanding, QSizePolicy.Maximum)
        # self.layoutBotoneraMapa.addSpacerItem(spacer)

        self.butoMostra = QvPushButton(flat=True)
        self.butoMostra.setMaximumHeight(80)
        self.butoMostra.setMinimumHeight(80)
        self.butoMostra.setMaximumWidth(80)
        self.butoMostra.setMinimumWidth(80)

        icon=QIcon(os.path.join(imatgesDir,'mapeta1.png'))
        self.butoMostra.setIconSize(QSize(80,80))
        self.butoMostra.setIcon(icon)

        self.butoMostra2 = QvPushButton(flat=True)
        self.butoMostra2.setMaximumHeight(80)
        self.butoMostra2.setMinimumHeight(80)
        self.butoMostra2.setMaximumWidth(80)
        self.butoMostra2.setMinimumWidth(80)
        icon=QIcon(os.path.join(imatgesDir,'mapeta2.png'))
        self.butoMostra2.setIconSize(QSize(80,80))
        self.butoMostra2.setIcon(icon)
        self.botoneraMostres = QFrame()

        
        # self.layoutCanvas = QVBoxLayout(self)
        # self.layoutCanvas.setContentsMargins(0,0,0,0)
        # self.setLayout(self.layoutCanvas)

        self.layoutBotoneraMostres = QHBoxLayout(self.botoneraMostres)
        self.botoneraMostres.setLayout(self.layoutBotoneraMostres)
        # self.layoutCanvas.setAlignment(Qt.AlignVCenter)
        self.layoutBotoneraMostres.addWidget(self.butoMostra)
        self.layoutBotoneraMostres.addWidget(self.butoMostra2)
        self.layoutBotoneraMostres.setAlignment(Qt.AlignRight)
        # self.layoutCanvas.addWidget(self.botoneraMapa)
        # self.layoutCanvas.addWidget(self.botoneraMostres)    
    
    def actualitzaBotoMaximitza(self, maximitzat):
        if maximitzat:
            self.bMaximitza.setIcon(QIcon(os.path.join(imatgesDir,'fullscreen-exit.png')))
        else:
            self.bMaximitza.setIcon(QIcon(os.path.join(imatgesDir,'fullscreen.png')))

    def mostraBotoTemes(self):
        try:
            self.temes=QgsProject.instance().mapThemeCollection().mapThemes()
            if len(self.temes)>0:
                self.bTemes.show()
            else:
                self.bTemes.hide()
        except:
            self.bTemes.hide()
    def dragEnterEvent(self, e):
      
        e.accept()
        

    def dropEvent(self, e):
        position = e.pos()
        self.qvSv.rp.llevameP(position)
        self.mostraStreetView.emit()
        # self.button.move(position)

        e.setDropAction(Qt.MoveAction)
        e.accept()

    def setMapTool(self,tool):
        if isinstance(tool,QvMascaraEinaPlantilla):
            while tool in self.eines: 
                self.unsetLastMapTool()
        super().setMapTool(tool)
        if len(self.eines)>0 and self.eines[-1]==tool: return
        self.eines.append(tool)
        if tool in self.einesBotons:
            self.einesBotons[tool].setChecked(True)
            self.uncheckBotons(self.einesBotons[tool])
        else:
            self.uncheckBotons(None)

    def unsetMapTool(self,eina, ultima=False):
        super().unsetMapTool(eina)
        if isinstance(eina,QvMascaraEinaPlantilla):
            eina.eliminaRubberbands()
        if not ultima:
            #Eliminar l'aparició de més al final d'aquesta eina
            indexes = [i for i,x in enumerate(self.eines) if x == eina]
            if len(indexes)!=0: del(self.eines[indexes[-1]])

        if len(self.eines)>0:
            if self.eines[-1] is None or self.eines[-1]==eina:
                self.unsetLastMapTool()
                return
            # self.uncheckBotons(None)
            if self.eines[-1] in self.einesBotons:
                self.uncheckBotons(self.einesBotons[self.eines[-1]])
                self.einesBotons[self.eines[-1]].setChecked(True)
            super().setMapTool(self.eines[-1])

    def unsetLastMapTool(self):
        if len(self.eines)>1:
            eina=self.eines.pop()
            self.unsetMapTool(eina,True)

    def testDigitizeTool(self, eina):
        if eina is not None and QvApp().testVersioQgis(3, 10):
            from qgis.gui import QgsMapToolDigitizeFeature
            return isinstance(eina, QgsMapToolDigitizeFeature)
        return False

    def mousePressEvent(self,event):
        super().mousePressEvent(event)
        if event.button()==Qt.RightButton:
            eina = self.eines[-1]
            if not isinstance(eina, QvMesuraMultiLinia) and not self.testDigitizeTool(eina):
                self.unsetLastMapTool()
                # Si volvemos a digitalización, ignorar RightButton
                eina = self.mapTool()
                if self.testDigitizeTool(eina): eina.ignoreRightButton = True

class Marc(QFrame):
    def __init__(self, master=None):
        QFrame.__init__(self, master)
    #ENTRA????
    def paintEvent(self, ev):
        painter = QPainter(self)
        # gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        # gradient.setColorAt(0.0, Qt.black)
        # gradient.setColorAt(0.4, Qt.gray)
        # gradient.setColorAt(0.7, Qt.black)
        painter.setBrush(Qt.QColor(100,100,100))
        painter.drawRoundedRect(self.rect(), 10.0, 10.0)
        # painter.end()

class BotoStreetView(QPushButton):
  
    def __init__(self, title, parent):
        super().__init__(title, parent)
        
        self.setAcceptDrops(True)
        

    def dragEnterEvent(self, e):
      
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore() 

    def dropEvent(self, e):
        
        self.setText(e.mimeData().text()) 



if __name__ == "__main__":
    from qgis.core import QgsProject
    from qgis.gui import  QgsLayerTreeMapCanvasBridge
    from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel
    from qgis.PyQt.QtGui import QColor
   

    
    projecteInicial=os.path.abspath('mapesOffline/qVista default map.qgs')

    with qgisapp() as app:
        # app.setStyle(QStyleFactory.create('fusion'))
        
        llistaBotons = ['centrar', 'zoomIn', 'zoomOut', 'panning']
        widget = QWidget()
        widget.show()
        canvas = QvCanvas(llistaBotons, posicioBotonera = 'NO', botoneraHoritzontal = True)
        canvas.setParent(widget)
        canvas.setGeometry(10,10,1000,1000)
        canvas.setCanvasColor(QColor(10,10,10))
        marc = Marc(canvas)
        marc.setGeometry(10,10,100,100)
        marc.show()
        label = QLabel(marc)
        label.setGeometry(10,10,10,10)
        label.setText('sdf')

        project= QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        # canvas.show()