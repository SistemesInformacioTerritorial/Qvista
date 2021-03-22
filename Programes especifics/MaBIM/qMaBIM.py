#from MaBIM-ui import Ui_MainWindow
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from qgis.core.contextmanagers import qgisapp
from moduls.QvCanvas import QvCanvas
from moduls.QvCanvasAuxiliar import QvCanvasAuxiliar
from moduls.QvMapetaBrujulado import QvMapetaBrujulado
from moduls.QvSingleton import Singleton
from moduls.QvAtributs import QvAtributs
from moduls.QvLlegenda import QvLlegenda
from moduls.QVCercadorAdreca import QCercadorAdreca
from moduls.QvAtributsForms import QvFitxesAtributs
from moduls.QvConstants import QvConstants
from moduls import QvFuncions
import functools
import sys
import os
from typing import Sequence
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRectangle, QgsFeatureRequest
from qgis.gui import  QgsLayerTreeMapCanvasBridge, QgsVertexMarker, QgsMapTool, QgsGui

# Consulta a partir del text escrit al camp de cerca. 
# Obté el codi BIM, la descripció i la denominació.
CONSULTA_CERCADOR = '''SELECT BIM, DESCRIPCIO_BIM, DENOMINACIO_BIM
FROM 
ZAFT_0002
WHERE
((BIM LIKE '%'||:pText||'%')
    OR (UPPER(DESCRIPCIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(DENOMINACIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(REF_CADASTRE_BIM) LIKE '%'||:pText||'%'))
AND (ROWNUM < 100)''' #aquesta consulta haurà d'estar en un arxiu, però ja es farà


CONSULTA_INFO_BIM_Z2 = '''SELECT BIM, ESTAT, ADSCRIT, 
DESCRIPCIO_BIM, DENOMINACIO_BIM, 
TIPOLOGIA_BIM, SUBTIPOLOGIA_BIM, TIPUS_IMMOBLE, QUALIFICACIO_JURIDICA
FROM 
ZAFT_0002 
WHERE 
((BIM LIKE :pText||'%')
    OR (UPPER(DESCRIPCIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(DENOMINACIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(REF_CADASTRE_BIM) LIKE '%'||:pText||'%'))
AND (ROWNUM < 100)'''

# Consulta que obté informació de ZAFT_0003 a partir del codi BIM
CONSULTA_INFO_BIM_Z3 = '''SELECT TIPUS_VIA, NOM_VIA, NUM_INI, 
LLETRA_INI, NUM_FI, LLETRA_FI, DISTRICTE, BARRI, MUNICIPI, CP,
PROVINCIA, CODI_CARRER, TIPUS, ESTAT, ID_PROV 
FROM ZAFT_0003
WHERE
((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''

CONSULTA_INFO_BIM_Z13 = '''SELECT PROPIETARI_SOL, PROPIETARI_CONS
FROM ZAFT_0013
WHERE
((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))
'''

CONSULTA_INFO_BIM_Z11 = '''SELECT FINCA, NUM_REGISTRE, MUNICIPI, SECCIO, TOM, LLIBRE, FOLI, INSCRIP, CRU, SUP_REGISTRAL_SOL, SUP_REGISTRAL_CONS
FROM ZAFT_0011
WHERE
((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))
'''

# això estaria millor dins de la classe Consulta, però no va
# No es pot utilitzar fora d'aquesta classe
def connexio(func):
    def _funcio(self,*args,**kwargs):
        if self.OBRE_DB():
            return func(self,*args,**kwargs)
        return []
    return _funcio

class Consulta(Singleton):
    _DB_MABIM_PRO = {
        'Database': 'QOCISPATIAL',
        'HostName': 'GEOPR1.imi.bcn',
        'Port': 1551,
        'DatabaseName': 'GEOPR1',
        # 'UserName': None,
        # 'Password': None
        'UserName': 'PATRIMONI_CONS',
        'Password': 'PATRIMONI_CONS'
    }

    def __init__(self):
        if hasattr(self,'db'):
            return
        self.dbMaBIM=self._DB_MABIM_PRO
        self.obte_camps_restants()
        self.db = QSqlDatabase.addDatabase(self.dbMaBIM['Database'], 'FAV')
        if self.db.isValid():
            self.db.setHostName(self.dbMaBIM['HostName'])
            self.db.setPort(self.dbMaBIM['Port'])
            self.db.setDatabaseName(self.dbMaBIM['DatabaseName'])
            self.db.setUserName(self.dbMaBIM['UserName'])
            self.db.setPassword(self.dbMaBIM['Password'])
        else:
            # missatge avisant de que no funciona, que tornin a intentar-ho
            pass
    def obte_camps_restants(self):
        while self.dbMaBIM['UserName'] in (None, ''):
            self.dbMaBIM['UserName'], _ = QtWidgets.QInputDialog.getText(None,'Usuari de la base de dades',f"Introduïu el nom d'usuari de la base de dades {self.dbMaBIM['DatabaseName']}")
        while self.dbMaBIM['Password'] in (None, ''):
            self.dbMaBIM['Password'], _ = QtWidgets.QInputDialog.getText(None,'Contrasenya de la base de dades',f"Introduïu la contrasenya de la base de dades {self.dbMaBIM['DatabaseName']}",QtWidgets.QLineEdit.Password)
    @connexio
    def consulta(self, consulta: str, binds: dict = {}, camps: Sequence[int]=None):
        """
        Realitza una consulta a la base de dades

        Arguments:
            consulta {str} -- Consulta que volem executar
        
        Keyword Arguments:
            binds {dict} -- Arguments que volem lligar a la consulta. Per exemple, 

        """
        res = []
        query=QSqlQuery(self.db)
        query.prepare(consulta)
        for (x,y) in binds.items():
            query.bindValue(x,y)
        query.exec()
        res = []
        while query.next():
            # vals = query.value(0), query.value(1), query.value(2)
            if camps is None:
                camps = range(query.record().count())
            vals = [query.value(i) for i in camps]
            res.append(vals)
        return res
    
    def OBRE_DB(self):
        if self.dbMaBIM is None:
            self.connectaDB()
        # Si ja està oberta, retornem True. Si no, intentem obrir-la, i retornem el que retorni
        # Lazy evaluation :D
        return self.db.isOpen() or self.db.open()
    def TANCA_DB(self):
        return self.db.close()
    def __del__(self):
        if not self.TANCA_DB() and self.db.isOpen():
            # No s'ha tancat la base de dades :'(
                pass

class Completador(QtWidgets.QCompleter):
    def __init__(self):
        super().__init__()
        self.setModel(QtCore.QStringListModel())
        self.setFilterMode(QtCore.Qt.MatchContains)
    @staticmethod
    def separa(llista, word):
        def comenca(x):
            # Volem comprovar si alguna de les subparaules de x comença per word
            # Una manera de mirar-ho és mirar si x comença per word o x conté ' 'word
            return x.startswith(word) or f' {word}' in x
        def no_comenca(x):
            return not comenca(x)
        return list(filter(comenca,llista)), list(filter(no_comenca,llista))
    def update(self, text):
        # self.model().setStringList(self.consulta(text))
        self.llista=Consulta().consulta(CONSULTA_CERCADOR,{':pText':text},(0,1,2))
        self.m_word = text
        res = [' '.join([str(y) for y in x if str(y).upper()!='NULL']) for x in self.llista]
        comencen, contenen = self.separa(res, text)
        self.model().setStringList(comencen+contenen)
        self.complete()
    def splitPath(self,path):
        self.update(path)
        return [path]
        # print(path)

class QvSeleccioBIM(QgsMapTool):
    """Aquesta clase és un QgsMapTool que selecciona l'element clickat. 

       Si la llegenda no té un layer actiu, és treballa amb el primer visible al canvas.
    """

    elementsSeleccionats = QtCore.pyqtSignal('PyQt_PyObject') # layer, features

    def __init__(self, canvas, llegenda, layer, radi=10):
        """[summary]

        Arguments:
            canvas {QgsMapCanvas} -- El canvas de la app
            llegenda {QvLlegenda} -- La llegenda de la app

        Keyword Arguments:
            radi {int} -- [El radi de tolerancia de la seleccio (default: 20)
            senyal {bool} -- False: mostra fitxa del(s) element(s) seleccionat(s)
                             True: llença un senyal (default: False)
        """

        super().__init__(canvas)
        self.canvas = canvas
        self.llegenda = llegenda
        self.radi = radi
        self.layer = layer
        self.setCursor(QvConstants.cursorDit())

    def keyPressEvent(self, event):
        """ Defineix les actuacions del QvMapeta en funció de la tecla apretada.
        """
        if event.key() == Qt.Key_Escape:
            pass

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def missatgeCaixa(self, textTitol, textInformacio):
        msgBox = QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        msgBox.exec()

    def canvasReleaseEvent(self, event):
        # Lllegim posició del mouse
        x = event.pos().x()-1
        y = event.pos().y()-8
        try:

            if self.canvas.rotation() == 0:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x - self.radi, y-self.radi)
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x + self.radi, y+self.radi)
            else:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x-self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x+self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
            rect = QgsRectangle(esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())
            it = self.layer.getFeatures(QgsFeatureRequest().setFilterRect(rect))
            features = [feature for feature in it]

            if len(features) > 0:
                    self.elementsSeleccionats.emit(features)
        except Exception as e:
            print(str(e))

class FormulariAtributs(QvFitxesAtributs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui.bSeleccionar = self.ui.buttonBox.addButton('Seleccionar', QtWidgets.QDialogButtonBox.ActionRole)
        self.ui.bSeleccionar.clicked.connect(self.selecciona)
        self.ui.stackedWidget.setStyleSheet('background: transparent; color: black; font-size: 14px')
        self.ui.buttonBox.setFixedWidth(300)
        for x in (self.ui.bNext, self.ui.bPrev, *self.ui.buttonBox.buttons()):
            x.setStyleSheet('QAbstractButton{font-size: 14px; padding: 2px}')
            x.setFixedSize(100,30)
    def selecciona(self):
        index = self.ui.stackedWidget.currentIndex()
        feature = self.features[index]
        codi = str(feature.attribute('BIM'))
        self.parentWidget().leCercador.setText(codi)
        self.parentWidget().consulta()
        self.close()
    

class WidgetCercador(QtWidgets.QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.marcaLloc = None
        lay = QtWidgets.QHBoxLayout()
        self.setLayout(lay)
        self.leCarrer = QtWidgets.QLineEdit()
        self.leCarrer.setPlaceholderText('Carrer')
        self.leNumero = QtWidgets.QLineEdit()
        self.leNumero.setPlaceholderText('Número')
        self.lblIcona = QtWidgets.QLabel()
        pix = QtGui.QPixmap('imatges/MaBIM/cercador-icona.png')
        self.lblIcona.setPixmap(pix.scaledToHeight(20))
        self.cercador = QCercadorAdreca(self.leCarrer, self.leNumero, 'SQLITE')
        lay.addWidget(self.leCarrer)
        lay.addStretch()
        lay.addWidget(self.leNumero)
        # lay.addWidget(self.lblIcona)

        self.cercador.sHanTrobatCoordenades.connect(self.resultatCercador)
    
    def resultatCercador(self, codi, info):
        if codi == 0:
            self.canvas.setCenter(self.cercador.coordAdreca)
            print(self.canvas.scale(), self.canvas.mapUnits())
            self.canvas.zoomScale(1000)
            print(self.canvas.scale())
            self.canvas.scene().removeItem(self.marcaLloc)

            self.marcaLloc = QgsVertexMarker(self.canvas)
            self.marcaLloc.setCenter( self.cercador.coordAdreca )
            self.marcaLloc.setColor(QtGui.QColor(255, 0, 0))
            self.marcaLloc.setIconSize(15)
            self.marcaLloc.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
            self.marcaLloc.setPenWidth(3)
            self.marcaLloc.show()
            self.marcaLlocPosada = True
    
    def resizeEvent(self, event):
        self.leCarrer.setFixedSize(400,20)
        self.leNumero.setFixedSize(80,20)
        print(self.leCarrer.width(), self.leNumero.width())
        self.setFixedSize(self.leCarrer.width()+self.leNumero.width()+20, 30)
        self.move(self.parentWidget().width()-self.width()-2, 2)
        super().resizeEvent(event)
    
    # def cerca(self):
    #     txt = self.leCercador.text()
    #     print(txt)
    #     self.leCercador.clear()

class QMaBIM(QtWidgets.QMainWindow):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('Programes especifics/MaBIM/MaBIM.ui',self)
        self.llistaBotons = (self.bFavorits, self.bBIMs, self.bPIP, self.bProjectes, self.bConsultes, self.bDocumentacio, self.bEines)

        self.connectBotons()
        self.connectaCercador()
        self.configuraPlanols()
        self.inicialitzaProjecte()
        self.connectaDB()
        self.setIcones()

        self.einaSeleccio = QvSeleccioBIM(self.canvasA, self.llegenda, self.getCapaBIMs())
        self.einaSeleccio.elementsSeleccionats.connect(self.seleccioGrafica)

        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
    
    def seleccioGrafica(self, feats):
        form = FormulariAtributs(self.getCapaBIMs(), feats, self)
        form.exec()
        self.canvasA.bPanning.click()
    
    def setIcones(self):
        self.setIconesBotons()
        # Qt com a tal no permet fer  una label amb imatge i text. HTML sí que ho permet
        # Ja que les labels permeten tenir com a contingut un HTML,
        # doncs posem un mini HTML amb la imatge i el text
        self.lblLogoMaBIM.setText(f"""<html><img src=imatges/MaBIM/MaBIM.png height={self.lblLogoMaBIM.height()}><span style="font-size:18pt; color:#ffffff; vertical-align: middle;"> MaBIM</span></html>""")
        self.lblLogoMaBIM.setFixedWidth(275)
        print(self.widget_3.width())
    
    def setIconesBotons(self):
        # afegir les icones des del designer donava problemes
        # per tant, les afegim aquí i té un comportament més consistent
        parelles = (
            (self.bFavorits, 'botonera-fav.png'),
            (self.bBIMs, 'botonera-BIM.png'),
            (self.bPIP, 'botonera-PIP.png'),
            (self.bProjectes, 'botonera-projectes'),
            (self.bConsultes, 'botonera-consultes'),
            (self.bDocumentacio, 'botonera-documentacio'),
            (self.bEines, 'botonera-eines')
        )
        for (boto, icona) in parelles:
            boto.setIcon(QtGui.QIcon(f'Imatges/MaBIM/{icona}'))

    def connectaDB(self):
        pass
    def connectaCercador(self):
        # self.leCercador.editingFinished.connect(self.consulta)
        completer = Completador()
        self.leCercador.setCompleter(completer)
        completer.activated.connect(self.consulta)
    def consulta(self):
        txt = self.leCercador.text().split(' ')[0]
        cons = Consulta()
        try:
            self.dadesLabelsDades = cons.consulta(CONSULTA_INFO_BIM_Z2,{':pText':txt})[0]
            self.dadesTaula = cons.consulta(CONSULTA_INFO_BIM_Z3,{':pText':txt})
            self.dadesTitularitat = cons.consulta(CONSULTA_INFO_BIM_Z13, {':pText':txt})[0]
            self.dadesFinquesRegistrals = cons.consulta(CONSULTA_INFO_BIM_Z11, {':pText':txt})
        except IndexError:
            # la consulta no funciona :(
            return
        self.recarregaLabelsDades()
        
    def recarregaLabelsDades(self):
        self.lCapcaleraBIM.setText(f'BIM {self.dadesLabelsDades[0]}  {self.dadesLabelsDades[3]}')

        # Labels pestanya "Dades Identificatives"
        labels = (self.lNumBIM, self.lEstatBIM, self.lBIMAdscrit, 
                  self.lDescripcioBIM, self.lDenominacioBIM, 
                  self.lTipologiaReal, self.lSubtipologiaReal, self.lTipusBeReal, self.lQualificacioJuridica)
        # totes les labels tindran la mateixa font. Per tant, agafem la d'una qualsevol
        font = self.lNumBIM.font()
        font.setBold(True)
        for (lbl,txt) in zip(labels, self.dadesLabelsDades):
            if str(txt).upper()!='NULL':
                lbl.setText(txt)

                lbl.setFont(font)
                lbl.setWordWrap(True)
            else:
                lbl.setText('')
        self.lTipologiaRegistral.setText(self.lTipologiaReal.text())
        self.lSubtipologiaRegistral.setText(self.lSubtipologiaReal.text())
        self.lTipusBeRegistral.setText(self.lTipusBeReal.text())
        self.lTipologiaRegistral.setFont(font)
        self.lSubtipologiaRegistral.setFont(font)
        self.lTipusBeRegistral.setFont(font)

        # Taula pestanya "Dades Identificatives"
        self.twDadesBIM.setRowCount(len(self.dadesTaula))
        for (i,x) in enumerate(self.dadesTaula):
            for (j,elem) in enumerate(x):
                if type(elem)!=str:
                    print(type(elem))
                    elem = str(elem)
                    if elem=='NULL': elem=''
                self.twDadesBIM.setItem(i,j,QtWidgets.QTableWidgetItem(elem))
        self.twDadesBIM.resizeColumnsToContents()

        # Labels pestanya "Titularitat i Registral"
        labels = (self.lPropietariSol, self.lPropietariCons, self.lSupSolReg, self.lSupConsReg)
        for (lbl,txt) in zip(labels, self.dadesTitularitat):
            if str(txt).upper()!='NULL':
                lbl.setText(txt)

                lbl.setFont(font)
                lbl.setWordWrap(True)
            else:
                lbl.setText('')

        self.twFinquesRegistrals.setRowCount(len(self.dadesFinquesRegistrals))
        for (i,x) in enumerate(self.dadesFinquesRegistrals):
            for (j, elem) in enumerate(x):
                if not isinstance(x, str):
                    elem = str(elem)
                    if elem=='NULL': elem=''
                self.twFinquesRegistrals.setItem(i,j,QtWidgets.QTableWidgetItem(elem))
        self.twFinquesRegistrals.resizeColumnsToContents()

        cerca = f"BIM LIKE '{self.dadesLabelsDades[0]}'"
        
        
        layer = self.getCapaBIMs()
        layer.subsetString()
        layer.setSubsetString(cerca)
        # Si no hi ha cap feature després d'aplicar el filtre, eliminem el filtre i mostrem tota l'extensió
        if layer.featureCount()==0:
            self.netejaFiltre()
            QtWidgets.QMessageBox.warning(self,"Atenció!", "No s'ha pogut localitzar el BIM en el mapa. Contacteu amb l'administrador")
        self.canvasA.setExtent(layer.extent())

        # Si intentes eliminar el contingut d'un QLineEdit que té un QCompleter associat,
        #  el propi QCompleter torna a completar el QLineEdit, provocant que no es pugui netejar
        # Fent servir un QTimer es pot saltar això
        # https://stackoverflow.com/a/49032473
        QtCore.QTimer.singleShot(0, self.leCercador.clear)
    def netejaFiltre(self):
        layer = self.getCapaBIMs()
        layer.setSubsetString('')

    def configuraPlanols(self):
        root = QgsProject.instance().layerTreeRoot()
        planolA = self.tabCentral.widget(2)
        planolC = self.tabCentral.widget(3)
        planolR = self.tabCentral.widget(4)

        
        mapetaPng = "mapesOffline/default.png"
        botons = ['zoomIn', 'zoomOut', 'panning', 'centrar', 'streetview']

        # instanciem el canvas que representarà el Plànol de l'Ajuntament
        self.canvasA = QvCanvas(planolA, posicioBotonera='SE', llistaBotons=botons)
        QgsLayerTreeMapCanvasBridge(root, self.canvasA)
        planolA.layout().addWidget(self.canvasA)
        self.canvasA.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:25831'))
        self.canvasA.mostraStreetView.connect(lambda: self.canvasA.getStreetView().show())
        
        canvasC = QvCanvasAuxiliar(self.canvasA, sincronitzaExtensio=True, posicioBotonera='SE')
        QgsLayerTreeMapCanvasBridge(root, canvasC)
        planolC.layout().addWidget(canvasC)

        # instanciem els mapetes
        QvMapetaBrujulado(mapetaPng, self.canvasA, pare=self.canvasA)
        QvMapetaBrujulado(mapetaPng, canvasC, pare=canvasC)
        
        self.cerca1 = WidgetCercador(self.canvasA, self.canvasA)
        self.cerca1.show()
        # self.cerca1.move(-200,0)

        botoNeteja = self.canvasA.afegirBotoCustom('botoNeteja', 'imatges/MaBIM/canvas_neteja_filtre.png', 'Mostra tots els BIMs')
        botoNeteja.clicked.connect(self.netejaFiltre)
        botoNeteja.setCheckable(False)
        botoSelecciona = self.canvasA.afegirBotoCustom('botoSelecciona', 'imatges/apuntar.png', 'Selecciona BIM gràficament', 0)
        botoSelecciona.clicked.connect(lambda: self.canvasA.setMapTool(self.einaSeleccio))
        botoSelecciona.setCheckable(True)
        botoLlegenda = self.canvasA.afegirBotoCustom('botoLlegenda', 'imatges/map-legend.png', 'Mostrar/ocultar llegenda')
        botoLlegenda.clicked.connect(lambda: self.llegenda.setVisible(not self.llegenda.isVisible()))
        botoLlegenda.setCheckable(False)

        # Donem estil als canvas
        with open('style.qss') as f:
            estilCanvas = f.read()
        self.canvasA.setStyleSheet(estilCanvas)
        canvasC.setStyleSheet(estilCanvas)

        

        taulesAtributs = QvAtributs(self.canvasA)
        taulesAtributs.setWindowTitle("Taules d'atributs")
        self.llegenda = QvLlegenda(self.canvasA, taulesAtributs)
        self.llegenda.resize(500, 600)

        self.tabCentral.currentChanged.connect(self.canviaTab)
    
    def inicialitzaProjecte(self):
        QgsProject.instance().read('L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Patrimoni/PPM_CatRegles_geopackage.qgs')
    
    def getCapaBIMs(self):
        return self.llegenda.capaPerNom('MABIM')
    
    def canviaTab(self):
        return
        i = self.tabCentral.currentIndex()
        if i==2:
            self.llegenda.show()
            self.cerca1.show()

    def connectBotons(self):
        for (i,x) in enumerate(self.llistaBotons):
            x.clicked.connect(functools.partial(self.desmarcaBotons,x))
            x.clicked.connect(functools.partial(self.switchPantallaP,i))
    def switchPantallaP(self,i):
        self.stackedWidget.setCurrentIndex(i)
    def desmarcaBotons(self,aExcepcio):
        for x in self.llistaBotons:
            if x is not aExcepcio:
                x.setChecked(False)
            else:
                x.setChecked(True)

def splashScreen():
    splash_pix = QtGui.QPixmap('imatges/SplashScreen_qVista.png')
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splash.setEnabled(True)
    splash.showMessage("""Institut Municipal d'Informàtica (IMI) MaBIM""",QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom, QvConstants.COLORFOSC)
    splash.setFont(QtGui.QFont(QvConstants.NOMFONT,8))
    splash.show()
    return splash
def main():
    with qgisapp(sysexit=False) as app:
        app.setWindowIcon(QtGui.QIcon('imatges/MaBIM/Logo48.png'))
        splash = splashScreen()
        app.processEvents()
        main = QMaBIM()
        splash.finish(main)
        main.showMaximized()
        # sys.exit(app.exec())

if __name__ == '__main__':
    main()