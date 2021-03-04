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
import functools
import sys
from typing import Sequence
from qgis.core import QgsProject, QgsCoordinateReferenceSystem
from qgis.gui import  QgsLayerTreeMapCanvasBridge, QgsVertexMarker

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
((BIM LIKE :pText||'%') AND (ROWNUM<100))'''

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
        self.llistaBotons = (self.bFavorits, self.bBIMs, self.bPublicar, self.bPIP, self.bProjectes, self.bConsultes, self.bDocumentacio, self.bEines)

        self.connectBotons()
        self.connectaCercador()
        self.configuraPlanols()
        self.connectaDB()
        self.setIcones()
    
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
            (self.bPublicar, 'botonera-publicar.png'),
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
        except IndexError:
            # la consulta no funciona :(
            return
        self.recarregaLabelsDades()
        
    def recarregaLabelsDades(self):
        # self.lNumBIM.setText(self.dadesLabelsDades[0])
        # self.lEstatBIM.setText(self.dadesLabelsDades[1])
        # self.lBIAdscrit.setText(self.dadesLabelsDades[2])
        self.lCapcaleraBIM.setText(f'BIM {self.dadesLabelsDades[0]}  {self.dadesLabelsDades[3]}')
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
        self.twDadesBIM.setRowCount(len(self.dadesTaula))
        for (i,x) in enumerate(self.dadesTaula):
            for (j,elem) in enumerate(x):
                if type(elem)!=str:
                    print(type(elem))
                    elem = str(elem)
                    if elem=='NULL': elem=''
                self.twDadesBIM.setItem(i,j,QtWidgets.QTableWidgetItem(elem))
        self.twDadesBIM.resizeColumnsToContents()
        self.lTipologiaRegistral.setText(self.lTipologiaReal.text())
        self.lSubtipologiaRegistral.setText(self.lSubtipologiaReal.text())
        self.lTipusBeRegistral.setText(self.lTipusBeReal.text())
        self.lTipologiaRegistral.setFont(font)
        self.lSubtipologiaRegistral.setFont(font)
        self.lTipusBeRegistral.setFont(font)

        cerca = f"BIM LIKE '{self.dadesLabelsDades[0]}'"
        
        layer = self.llegenda.capaPerNom('MABIM')
        # for field in layer.fields():
        #     print(field.name(), field.typeName())
        # layer.selectByExpression(cerca)
        # capes = [x for x in self.llegenda.capes() if 'BIM' in [camp.name() for camp in x.fields()]]
        # for x in capes:
        #     x.setSubsetString('')
        #     x.setSubsetString(cerca)
        #     x.selectAll()
        layer.setSubsetString(cerca)
        layer.selectAll()
        self.canvasA.zoomToSelected(layer)
        layer.removeSelection()
        # for x in capes:
        #     x.removeSelection()
        QtCore.QTimer.singleShot(0, self.leCercador.clear)

    def configuraPlanols(self):
        # QgsProject.instance().read('D:/MABIM-DADES/mabimAUX.qgs')
        QgsProject.instance().read('U:/QUOTA/Comu_imi/patrimoni/Oriol/PPM_CatRegles_geopackage.qgs')
        root = QgsProject.instance().layerTreeRoot()
        planolA = self.tabCentral.widget(2)
        planolC = self.tabCentral.widget(3)
        planolR = self.tabCentral.widget(4)

        mapetaPng = "mapesOffline/default.png"
        self.canvasA = QvCanvas(planolA, posicioBotonera='SE')
        self.canvasA.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:25831'))
        mapeta = QvMapetaBrujulado(mapetaPng, self.canvasA,  pare=self.canvasA)
        QgsLayerTreeMapCanvasBridge(root, self.canvasA)
        planolA.layout().addWidget(self.canvasA)
        self.cerca1 = WidgetCercador(self.canvasA, self.canvasA)
        self.cerca1.show()


        # canvasC = QvCanvas(planolC, posicioBotonera='SE')
        canvasC = QvCanvasAuxiliar(self.canvasA, sincronitzaExtensio=True, posicioBotonera='SE')
        mapeta = QvMapetaBrujulado(mapetaPng, canvasC,  pare=canvasC)
        QgsLayerTreeMapCanvasBridge(root, canvasC)
        planolC.layout().addWidget(canvasC)

        taulesAtributs = QvAtributs(self.canvasA)
        # self.llegendes = [QvLlegenda(x, taulesAtributs, editable=False) for x in (canvasA, canvasC, canvasR)]
        self.llegenda = QvLlegenda(self.canvasA, taulesAtributs)

        self.tabCentral.currentChanged.connect(self.canviaTab)
    
    def canviaTab(self):
        return
        i = self.tabCentral.currentIndex()
        # if i in range(2,4):
        #     self.llegendes[i-2].show()
        # else:
        #     for x in self.llegendes:
        #         x.hide()
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


def main():
    with qgisapp() as app:
        main = QMaBIM()
        main.showMaximized()
        sys.exit(app.exec())

if __name__ == '__main__':
    main()