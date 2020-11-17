#from MaBIM-ui import Ui_MainWindow
from PyQt5 import QtWidgets, uic
from PyQt5.QtSql import QSqlDatabase
from qgis.core.contextmanagers import qgisapp
from moduls.QvCanvas import QvCanvas
from moduls.QvMapetaBrujulado import QvMapetaBrujulado
import functools
import sys
from qgis.core import QgsProject
from qgis.gui import  QgsLayerTreeMapCanvasBridge

_DB_MABIM_PRO = {
    'Database': 'QOCISPATIAL',
    'HostName': 'GEOPR1.imi.bcn',
    'Port': 1551,
    'DatabaseName': 'GEOPR1',
    'UserName': None,
    'Password': None
}

CONSULTA = '''SELECT
  BIM, DESCRIPCIO_BIM, DENOMINACIO_BIM
FROM 
  ZAFT_0002
WHERE
  ((BIM LIKE :pText||'%')
    OR (UPPER(DESCRIPCIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(DENOMINACIO_BIM) LIKE '%'||:pText||'%')
    OR (UPPER(REF_CADASTRE_BIM) LIKE '%'||:pText||'%'))
  AND (ROWNUM < 100)''' #aquesta consulta haurà d'estar en un arxiu, però ja es farà


class QMaBIM(QtWidgets.QMainWindow):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('Programes especifics/MaBIM/MaBIM.ui',self)
        self.llistaBotons = (self.bFavorits, self.bBIMs, self.bPublicar, self.bPIP, self.bProjectes, self.bConsultes, self.bDocumentacio, self.bEines)

        self.connectBotons()
        self.connectaCercador()
        self.configuraPlanols()
        self.connectaDB()

    def connectaDB(self):
        self.dbMaBIM=_DB_MABIM_PRO
        while self.dbMaBIM['UserName'] in (None, ''):
            self.dbMaBIM['UserName'], _ = QtWidgets.QInputDialog.getText(self,'Usuari de la base de dades',f"Introduïu el nom d'usuari de la base de dades {self.dbMaBIM['DatabaseName']}")
        while self.dbMaBIM['Password'] in (None, ''):
            self.dbMaBIM['Password'], _ = QtWidgets.QInputDialog.getText(self,'Contrasenya de la base de dades',f"Introduïu la contrasenya de la base de dades {self.dbMaBIM['DatabaseName']}",QtWidgets.QLineEdit.Password)
        
        self.db = QSqlDatabase.addDatabase(self.dbMaBIM['Database'], 'FAV')
        if self.db.isValid():
            self.db.setHostName(self.dbMaBIM['HostName'])
            self.db.setPort(self.dbMaBIM['Port'])
            self.db.setDatabaseName(self.dbMaBIM['DatabaseName'])
            self.db.setUserName(self.dbMaBIM['UserName'])
            self.db.setPassword(self.dbMaBIM['Password'])
    def connectaCercador(self):
        self.leCercador.returnPressed.connect(self.consulta)
    def consulta(self):
        text = self.leCercador.text()
        res = []
        if text!='':
            if self.OBRE_DB():
                query=QSqlQuery(self.db)
                query.prepare(CONSULTA)
                query.bindValue(':pText',text)
                query.exec()
                res = []
                while query.next():
                    res.append(query.value(0))
                print(res)
                self.TANCA_DB()
            else:
                QtWidgets.QMessageBox.critical(self,'Error de base de dades',"No s'ha pogut establir la connexió a la base de dades. Reviseu que teniu accés a la xarxa corporativa i que l'usuari i la contrasenya són correctes")
                self.leCercador.clear()
        return res
    def OBRE_DB(self):
        return self.db.open()
    def TANCA_DB(self):
        return self.db.close()
    # def cerca(self):
    #     txt = self.leCercador.text()
    #     print(txt)
    #     self.leCercador.clear()

    def configuraPlanols(self):
        QgsProject.instance().read('mapesOffline/qVista default map.qgs')
        root = QgsProject.instance().layerTreeRoot()
        planolA = self.tabCentral.widget(2)
        planolC = self.tabCentral.widget(3)
        planolR = self.tabCentral.widget(4)

        mapetaPng = "mapesOffline/default.png"
        canvasA = QvCanvas(planolA, posicioBotonera='SE')
        mapeta = QvMapetaBrujulado(mapetaPng, canvasA,  pare=canvasA)
        QgsLayerTreeMapCanvasBridge(root, canvasA)
        planolA.layout().addWidget(canvasA)

        canvasC = QvCanvas(planolC, posicioBotonera='SE')
        mapeta = QvMapetaBrujulado(mapetaPng, canvasC,  pare=canvasC)
        QgsLayerTreeMapCanvasBridge(root, canvasC)
        planolC.layout().addWidget(canvasC)

        canvasR = QvCanvas(planolR, posicioBotonera='SE')
        mapeta = QvMapetaBrujulado(mapetaPng, canvasR,  pare=canvasR)
        QgsLayerTreeMapCanvasBridge(root, canvasR)
        planolR.layout().addWidget(canvasR)

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