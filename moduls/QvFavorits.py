from moduls.QvSingleton import Singleton
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
from qgis.PyQt.QtCore import Qt
import getpass
from moduls.QvApp import _DB_QVISTA, QvApp
from qgis.PyQt.QtWidgets import QMessageBox



class QvFavorits(Singleton):
    dadesDB = _DB_QVISTA[QvApp().calcEntorn()]

    dadesTaula = {'nomCampInfo':'nom_mapa',
                  'nomTaula':'QV_MAPES_FAVORITS',
                  'nomCampId':'iduser'}
    consultaGet = "select {nomCampInfo} from {nomTaula} where {nomCampId}=:IDUSER"
    consultaAfegeix = "insert into {nomTaula} ({nomCampId}, {nomCampInfo}) values (:IDUSER,:NOM_FAVORIT)"
    consultaElimina = "delete from {nomTaula} where {nomCampId}=:IDUSER and {nomCampInfo}=:NOM_FAVORIT"
    def __init__(self):
        if hasattr(self,'db'):
            return
        self.configuraBD()
    def configuraBD(self):
        self.db = QSqlDatabase.addDatabase(self.dadesDB['Database'], 'FAV')
        if self.db.isValid():
            self.db.setHostName(self.dadesDB['HostName'])
            self.db.setPort(self.dadesDB['Port'])
            self.db.setDatabaseName(self.dadesDB['DatabaseName'])
            self.db.setUserName(self.dadesDB['UserName'])
            self.db.setPassword(self.dadesDB['Password'])
    def __CONNECTA_BASE_DADES__(self,usuari):
        if not self.db.isOpen() and not self.db.open():
            #No ens hem pogut connectar
            return False
        return True
            
        
    def __DESCONNECTA_BASE_DADES__(self,usuari,commit=True):
        if commit:
            self.db.commit()
        self.db.close()
        
    def getFavorits(self,usuari=getpass.getuser().upper()):
        '''Comentari explicant'''
        if not self.__CONNECTA_BASE_DADES__(usuari):
            return []
        query=QSqlQuery(self.db)
        consulta = self.consultaGet.format(**self.dadesTaula)
        query.prepare(consulta)
        query.bindValue(':IDUSER',usuari)
        query.exec()
        res=[]
        while query.next():
            res.append(query.value(0))
        #Consulta
        self.__DESCONNECTA_BASE_DADES__(usuari,False)
        return res
    
    def mostra_error(self, icona, titol, text, text_extra, text_detallat=None):
        msg = QMessageBox(icona, titol, text, QMessageBox.Ok)
        # msg.setIcon(icona)
        # msg.setText(text)
        if text_extra is not None: msg.setInformativeText(text_extra)
        if text_detallat is not None: msg.setDetailedText(text_detallat)
        # msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowFlag(Qt.WindowStaysOnTopHint)
        msg.exec_()
    
    def actualitzaFavorit(self, favorit, usuari, consulta):
        if not self.__CONNECTA_BASE_DADES__(usuari):
            return False, self.db.lastError().text()
        query=QSqlQuery(self.db)
        query.prepare(consulta.format(**self.dadesTaula))
        query.bindValue(':IDUSER',usuari)
        query.bindValue(':NOM_FAVORIT',favorit)
        executada = query.exec()
        self.__DESCONNECTA_BASE_DADES__(usuari)
        if not executada: 
            return executada, self.db.lastError.text()
        else:
            return executada, ''
        
    def afegeixFavorit(self,favorit,usuari=getpass.getuser().upper()):
        executada, error = self.actualitzaFavorit(favorit, usuari, self.consultaAfegeix)
        if not executada:
            self.mostra_error(QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, error)
            # QMessageBox.critical(None,"Atenció","No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau")
        return executada
        
    def eliminaFavorit(self,favorit,usuari=getpass.getuser().upper()):
        executada, error = self.actualitzaFavorit(favorit, usuari, self.consultaElimina)
        if not executada:
            QMessageBox.critical(None,"Atenció","No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau")
        return executada
        

if __name__=='__main__':
    from qgis.core.contextmanagers import qgisapp
    with qgisapp() as app:
        fav=QvFavorits()
        fav.afegeixFavorit('Hola :D','DE1719')
        print(fav.getFavorits('DE1719'))
        fav.eliminaFavorit('Hola :D','DE1719')