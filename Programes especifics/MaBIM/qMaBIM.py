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
from moduls.QvApp import QvApp
from moduls import QvFuncions
from moduls.QvStatusBar import QvStatusBar
import functools
import sys
import os
import math
from typing import Sequence
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRectangle, QgsPointXY, QgsFeatureRequest, QgsMapLayer, QgsVectorLayer, QgsGeometry
from qgis.gui import  QgsLayerTreeMapCanvasBridge, QgsVertexMarker, QgsMapTool, QgsGui, QgsRubberBand

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
((BIM LIKE '%'||:pText||'%')
    OR (UPPER(DESCRIPCIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(DENOMINACIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(REF_CADASTRE_BIM) LIKE '%'||:pText||'%'))
AND (ROWNUM < 100)'''

# Consulta que obté informació de ZAFT_0003 a partir del codi BIM
CONSULTA_INFO_BIM_Z3 = '''SELECT TIPUS_VIA, NOM_VIA, NUM_INI, 
LLETRA_INI, NUM_FI, LLETRA_FI, DISTRICTE, BARRI, MUNICIPI, CP,
PROVINCIA, TIPUS
FROM ZAFT_0003
WHERE
((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''

CONSULTA_INFO_BIM_Z13 = '''SELECT PROPIETARI_SOL, PROPIETARI_CONS, SUP_REGISTRAL_SOL, SUP_REGISTRAL_CONS
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
# és un decorador que garanteix que la Base de Dades estigui oberta
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
    """Completador pel cercador. Gestiona les suggerències quan cerques alguna cosa
       - Filtra en funció de si el contingut conté el string cercat
       - Primer mostra les que contenen algun substring que comenci per la cerca, i després les que contenen la cerca
    """
    def __init__(self):
        super().__init__()
        self.setModel(QtCore.QStringListModel())
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
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
        # actualitza el contingut del completer en funció del text cercat
        # fa la consulta a la base de dades, i ordena el resultat
        self.llista=Consulta().consulta(CONSULTA_CERCADOR,{':pText':text.upper()},(0,1,2))
        self.m_word = text
        # converteix el resultat de la consulta 
        #  (llista de llistes, amb els camps de la base de dades)
        #  en una llista de strings, que conté els camps no nuls separats per espais
        res = [' '.join([str(y) for y in x if str(y).upper()!='NULL']) for x in self.llista]
        comencen, contenen = self.separa(res, text)
        self.model().setStringList(comencen+contenen)
        self.complete()
    def splitPath(self,path):
        # funció que en els QCompleter rep el que vols cercar
        #  i retorna una llista de strings per fer el match
        #  en aquest cas aprofitem per actualitzar el model que conté els resultats,
        #  ja que la nostra cerca es basa en una base de dades
        self.update(path)
        return [path]

class QvSeleccioBIM(QgsMapTool):
    """Aquesta clase és un QgsMapTool que selecciona l'element clickat. 

       Si la llegenda no té un layer actiu, és treballa amb el primer visible al canvas.
    """

    elementsSeleccionats = QtCore.pyqtSignal('PyQt_PyObject') # layer, features

    def __init__(self, canvas, llegenda, radi=10):
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
        # Llegim posició del mouse
        # Donat que el cursor no selecciona exactament al centre, desplacem un petit offset
        x = event.pos().x()-1
        y = event.pos().y()-8
        try:
            # Per fer la selecció triarem dues cantonades (esquerra-dalt i dreta-baix) d'un rectangle
            #  si tenim una rotació aplicada, caldrà rotar també els punts
            if self.canvas.rotation() == 0:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x - self.radi, y-self.radi)
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x + self.radi, y+self.radi)
            else:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x-self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x+self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
            rect = QgsRectangle(esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())

            features = []
            for layer in self.llegenda.capes():
                if layer.type()==QgsMapLayer.VectorLayer and 'BIM' in layer.fields().names():
                    # la funció getFeatures retorna un iterable. Volem una llista
                    featsAct = [(feat, layer) for feat in layer.getFeatures(QgsFeatureRequest().setFilterRect(rect).setFlags(QgsFeatureRequest.ExactIntersect))]
                    features.extend(featsAct)

            if len(features) > 0:
                    self.elementsSeleccionats.emit(features)
        except Exception as e:
            print(str(e))

class FormulariAtributs(QvFitxesAtributs):
    """Formulari d'atributs del qVista, ampliat per tenir un botó extra de seleccionar
        Per fer-ho, bàsicament a la funció __init__ afegim el botó
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui.buttonBox.removeButton(self.ui.buttonBox.buttons()[0])
        self.ui.bSeleccionar = self.ui.buttonBox.addButton('Seleccionar', QtWidgets.QDialogButtonBox.ActionRole)
        self.ui.bSeleccionar.clicked.connect(self.selecciona)
        # self.ui.stackedWidget.setStyleSheet('background: transparent; color: black; font-size: 14px')
        self.ui.buttonBox.setFixedWidth(300)
        # self.ui.buttonBox.hide()
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
    

class Cercador:
    MIDALBLCARRER = 400, 40
    MIDALBLNUMERO = 80, 40
    MIDALBLICONA = 20, 20
    def __init__(self, canvas, leCarrer, leNumero, lblIcona):
        super().__init__()
        self.canvas = canvas
        self.marcaLloc = None
        self.leCarrer = leCarrer
        self.leCarrer.setPlaceholderText('Carrer')
        self.leNumero = leNumero
        self.leNumero.setPlaceholderText('Número')
        self.lblIcona = lblIcona
        pix = QtGui.QPixmap('imatges/MaBIM/cercador-icona.png')
        self.lblIcona.setPixmap(pix.scaledToHeight(self.MIDALBLICONA[0]))
        self.cercador = QCercadorAdreca(self.leCarrer, self.leNumero, 'SQLITE')
        self.marcaLlocPosada = False
        # self.setStyleSheet('font-size: 14px;')

        self.cercador.sHanTrobatCoordenades.connect(self.resultatCercador)
    
    def resultatCercador(self, codi, info):
        if codi == 0:
            self.canvas.setCenter(self.cercador.coordAdreca)
            self.canvas.zoomScale(1000)
            self.canvas.scene().removeItem(self.marcaLloc)

            self.marcaLloc = QgsVertexMarker(self.canvas)
            self.marcaLloc.setCenter( self.cercador.coordAdreca )
            self.marcaLloc.setColor(QtGui.QColor(255, 0, 0))
            self.marcaLloc.setIconSize(15)
            self.marcaLloc.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
            self.marcaLloc.setPenWidth(3)
            self.marcaLloc.show()
            self.marcaLlocPosada = True
            self.leCarrer.clear()
            self.leNumero.clear()
    def eliminaMarcaLloc(self):
        if self.marcaLlocPosada:
            self.canvas.scene().removeItem(self.marcaLloc)
            self.marcaLlocPosada = False
    
    # def resizeEvent(self, event):
    #     self.leCarrer.setFixedSize(*self.MIDALBLCARRER)
    #     self.leNumero.setFixedSize(*self.MIDALBLNUMERO)
    #     self.lblIcona.setFixedSize(*self.MIDALBLICONA)
    #     self.setFixedSize(self.MIDALBLCARRER[0]+self.MIDALBLNUMERO[0]+self.MIDALBLICONA[0], 50)
    #     self.move(self.parentWidget().width()-self.width()-2, 2)
    #     super().resizeEvent(event)
    
    # def cerca(self):
    #     txt = self.leCercador.text()
    #     print(txt)
    #     self.leCercador.clear()

class QMaBIM(QtWidgets.QMainWindow):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('Programes especifics/MaBIM/MaBIM.ui',self)
        
        self.llistaBotons = (self.bFavorits, self.bBIMs, self.bPIP, self.bProjectes, self.bConsultes)

        self.connectBotons()
        self.connectaCercador()
        self.configuraPlanols()
        self.inicialitzaProjecte()
        self.connectaDB()
        self.setIcones()

        self.einaSeleccio = QvSeleccioBIM(self.canvasA, self.llegenda)
        self.einaSeleccio.elementsSeleccionats.connect(self.seleccioGrafica)

        self.setStatusBar(QvStatusBar(self,['progressBar',('coordenades',1),'projeccio', 'escala'],self.canvasA,self.llegenda))
        self.statusBar().afegirWidget('lblSIT',QtWidgets.QLabel("SIT - Sistemes d'Informació Territorial"),0,0)
        self.statusBar().afegirWidget('lblSIT',QtWidgets.QLabel("Direcció de Patrimoni"),0,1)
        self.statusBar().afegirWidget('spacer',QtWidgets.QWidget(),1,2)

        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()

    def showEvent(self, e):
        super().showEvent(e)
        self.tabCentral.setCurrentIndex(2)
    
    def seleccioGrafica(self, feats):
        form = FormulariAtributs(self.getCapaBIMs(), feats, self)
        # form.setStyleSheet('QWidget{font-size: 12pt}')
        form.moveWid(self.width()-form.width(),(self.height()-form.height())//2)
        form.exec()
        self.canvasA.bPanning.click()
    
    def setIcones(self):
        self.setIconesBotons()
        # Qt com a tal no permet fer  una label amb imatge i text. HTML sí que ho permet
        # Ja que les labels permeten tenir com a contingut un HTML,
        # doncs posem un mini HTML amb la imatge i el text
        self.lblLogoMaBIM.setFixedSize(275,60)
        self.lblLogoMaBIM.setText(f"""<html><img src=imatges/MaBIM/MaBIM-text.png height={self.lblLogoMaBIM.height()}><span style="font-size:18pt; color:#ffffff;"></span></html>""")
        self.lblLogoAjuntament.setFixedSize(275//2,45)
        self.lblLogoAjuntament.setPixmap(QtGui.QPixmap('imatges/logo-ajuntament-de-barcelona-png-3.png').scaledToHeight(45))
        # self.lblLogoMaBIM.setFixedWidth(275)
    
    def setIconesBotons(self):
        # afegir les icones des del designer donava problemes
        # per tant, les afegim aquí i té un comportament més consistent
        parelles = (
            (self.bFavorits, 'botonera-fav.png'),
            (self.bBIMs, 'botonera-BIM.png'),
            (self.bPIP, 'botonera-PIP.png'),
            (self.bProjectes, 'botonera-projectes'),
            (self.bConsultes, 'botonera-consultes')
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
        # funció que fa les consultes a la Base de Dades, per omplir els diferents camps i taules

        # Donat que el primer camp del Line Edit és el BIM, l'utiltizarem per fer la consulta definitiva
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
        # un cop hem obtingut la nova informació, recarreguem la informació de les labels i taules

        # Eliminem la marca del cercador
        self.cerca1.eliminaMarcaLloc()
        self.dadesLabelsDades[0] = self.dadesLabelsDades[0].replace('0000', ' ').lstrip()
        # self.lCapcaleraBIM.setText(f'BIM {self.dadesLabelsDades[0]}  {self.dadesLabelsDades[3]}')

        # Labels pestanya "Dades Identificatives"
        labels = (self.lNumBIM, self.lEstatBIM, self.lBIMAdscrit, 
                  self.lDescripcioBIM, self.lDenominacioBIM, 
                  self.lTipologiaReal, self.lSubtipologiaReal, self.lTipusBeReal, self.lQualificacioJuridica)
        # totes les labels tindran la mateixa font. Per tant, agafem la d'una qualsevol
        font = self.lNumBIM.font()
        # font.setBold(True)
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
                    elem = str(elem)
                    if elem=='NULL': elem=''
                self.twDadesBIM.setItem(i,j,QtWidgets.QTableWidgetItem(elem))
        self.twDadesBIM.resizeColumnsToContents()

        # Labels pestanya "Titularitat i Registral"
        labels = (self.lPropietariSol, self.lPropietariCons, self.lSupSolReg, self.lSupConsReg)
        for (lbl,txt) in zip(labels, self.dadesTitularitat):
            if str(txt).upper()!='NULL':
                lbl.setText(str(txt))

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

        cerca = f"BIM LIKE '0000{self.dadesLabelsDades[0]}'"
        
        layers = self.getCapesBIMs()
        for layer in layers:
            layer.setSubsetString(cerca)
        # Si no hi ha cap feature després d'aplicar el filtre, eliminem el filtre i mostrem tota l'extensió
        if sum(layer.featureCount() for layer in layers)==0:
            self.netejaFiltre()
            QtWidgets.QMessageBox.warning(self,"Atenció!", "No s'ha pogut localitzar el BIM en el mapa.")
        self.canvasA.setExtent(layer.extent())

        # Si intentes eliminar el contingut d'un QLineEdit que té un QCompleter associat,
        #  el propi QCompleter torna a completar el QLineEdit, provocant que no es pugui netejar
        # Fent servir un QTimer es pot saltar això
        # https://stackoverflow.com/a/49032473
        QtCore.QTimer.singleShot(0, self.leCercador.clear)

    def netejaFiltre(self):
        layers = self.getCapesBIMs()
        for layer in layers:
            layer.setSubsetString('')

    @QvFuncions.cronometraDebug
    def configuraPlanols(self):
        # QgsProject.instance().read('mapesOffline/accelerator.qgs')
        # QgsProject.instance().read('mapesOffline/qVista default map.qgs')
        root = QgsProject.instance().layerTreeRoot()
        planolA = self.tabCentral.widget(2)
        
        mapetaPng = "mapesOffline/default.png"
        botons = ['panning', 'streetview', 'zoomIn', 'zoomOut', 'centrar']

        # instanciem el canvas que representarà el Plànol de l'Ajuntament
        self.canvasA = QvCanvas(planolA, posicioBotonera='SE', llistaBotons=botons)
        QgsLayerTreeMapCanvasBridge(root, self.canvasA)
        planolA.layout().addWidget(self.canvasA)
        self.canvasA.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:25831'))
        self.canvasA.mostraStreetView.connect(lambda: self.canvasA.getStreetView().show())

        self.canvasA.bCentrar.disconnect()
        self.canvasA.bCentrar.clicked.connect(self.centrarMapa)

        # instanciem el mapeta
        self.mapetaA = QvMapetaBrujulado(mapetaPng, self.canvasA, pare=self.canvasA)
        
        self.cerca1 = Cercador(self.canvasA, self.leCarrer, self.leNumero, self.lblIcona)
        self.cerca1.cercador.sHanTrobatCoordenades.connect(lambda: self.tabCentral.setCurrentIndex(2))

        botoSelecciona = self.canvasA.afegirBotoCustom('botoSelecciona', 'imatges/apuntar.png', 'Selecciona BIM gràficament', 1)
        def setEinaSeleccionar():
            self.canvasA.setMapTool(self.einaSeleccio)
            botoSelecciona.setChecked(True)
        botoSelecciona.clicked.connect(setEinaSeleccionar)
        botoSelecciona.setCheckable(True)
        botoNeteja = self.canvasA.afegirBotoCustom('botoNeteja', 'imatges/MaBIM/canvas_neteja_filtre.png', 'Mostra tots els BIMs', 2)
        botoNeteja.clicked.connect(self.netejaFiltre)
        botoNeteja.setCheckable(False)
        botoLlegenda = self.canvasA.afegirBotoCustom('botoLlegenda', 'imatges/map-legend.png', 'Mostrar/ocultar llegenda', 3)
        botoLlegenda.clicked.connect(lambda: self.llegenda.setVisible(not self.llegenda.isVisible()))
        botoLlegenda.setCheckable(False)
        botoMapeta = self.canvasA.afegirBotoCustom('botoMapeta', 'imatges/mapeta.png', 'Mostrar/ocultar mapa de situació',4)
        botoMapeta.clicked.connect(lambda: self.mapetaA.setVisible(not self.mapetaA.isVisible()))
        botoMapeta.setCheckable(False)
        botoCaptura = self.canvasA.afegirBotoCustom('botoCaptura','imatges/content-copy.png','Copiar una captura del mapa al portarretalls')
        botoCaptura.clicked.connect(self.canvasA.copyToClipboard)
        botoCaptura.setCheckable(False)

        # Donem estil als canvas
        estilCanvas = '''
            QvPushButton {
                background-color: #F9F9F9 transparent;
                color: #38474F;
                margin: 0px;
                border: 0px;
            }

            QvPushButton:checked{
                background-color: #DDDDDD;
                color: #38474F;
                border: 2px solid #FF6215;
                padding: 2px 2px;
            }'''
        self.canvasA.setStyleSheet(estilCanvas)

        

        taulesAtributs = QvAtributs(self.canvasA)
        taulesAtributs.setWindowTitle("Taules d'atributs")
        self.llegenda = QvLlegenda(self.canvasA, taulesAtributs)
        self.canvasA.setLlegenda(self.llegenda)
        self.llegenda.resize(500, 600)

        self.tabCentral.currentChanged.connect(self.canviaTab)

    def centrarMapa(self):
        self.canvasA.setExtent(QgsRectangle(QgsPointXY(405960, 4572210), QgsPointXY(452330 , 4595090)))
        self.canvasA.refresh()
        self.canvasA.bCentrar.setChecked(False)
    
    @QvFuncions.cronometraDebug
    def inicialitzaProjecte(self):
        # QgsProject.instance().read('L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Patrimoni/PPM_CatRegles_geopackage.qgs')
        self.llegenda.readProject('L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Patrimoni/PPM_CatRegles_geopackage.qgs')
        self.centrarMapa()

        # cal comprovar si les capes ... i ... són visibles
        model = self.llegenda.model
        capa1 = self.llegenda.capaPerNom('Entitats en PH')
        nodeCapa1 = QgsProject.instance().layerTreeRoot().findLayer(capa1.id())
        nodeBaixa1 = [node for node in model.layerLegendNodes(nodeCapa1) if 'PH: Baixa' in node.data(QtCore.Qt.DisplayRole)]
        capa2 = self.llegenda.capaPerNom('Entitats en PV')
        nodeCapa2 = QgsProject.instance().layerTreeRoot().findLayer(capa2.id())
        nodeBaixa2 = [node for node in model.layerLegendNodes(nodeCapa2) if 'Baixes' in node.data(QtCore.Qt.DisplayRole)]

        self.nodesBaixes = *nodeBaixa1, *nodeBaixa2

        self.cbBaixesVisibles.stateChanged.connect(self.swapVisibilitatBaixes)
    
    def swapVisibilitatBaixes(self,check):
        if check:
            for x in self.nodesBaixes:
                x.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        else:
            for x in self.nodesBaixes:
                x.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
    
    def getCapaBIMs(self):
        # Retorna una capa amb camp de BIMs
        #  nota: millor evitar-la, això només per quan ens veiem forçats a passar una única capa
        # return self.llegenda.capaPerNom('Entitats en PV')
        return self.getCapesBIMs()[0]
    def getCapesBIMs(self):
        return [capa for capa in self.llegenda.capes() if 'BIM' in capa.fields().names()]
    
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
    splash_pix = QtGui.QPixmap('imatges/MABIM/MABIMSplash.png')
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splash.setEnabled(True)
    splash.showMessage("""Institut Municipal d'Informàtica (IMI) MaBIM""",QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom, QvConstants.COLORFOSC)
    splash.setFont(QtGui.QFont(QvConstants.NOMFONT,8))
    splash.show()
    return splash
def main():
    with qgisapp(sysexit=False) as app:
        app.setWindowIcon(QtGui.QIcon('imatges/MaBIM/MaBIM.png'))
        splash = splashScreen()
        app.processEvents()
        main = QMaBIM()
        splash.finish(main)
        main.showMaximized()
        # main.inicialitzaProjecte()

if __name__ == '__main__':
    main()