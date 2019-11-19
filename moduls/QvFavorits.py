from moduls.QvSingleton import Singleton
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery, QSql
import getpass
from moduls.QvApp import _DB_QVISTA, QvApp
from PyQt5.QtWidgets import QMessageBox



class QvFavorits(Singleton):
    def __init__(self):
        if hasattr(self,'db'):
            return
        self.dbQvista=_DB_QVISTA[QvApp().calcEntorn()]
        self.db = QSqlDatabase.addDatabase(self.dbQvista['Database'], 'FAV')
        if self.db.isValid():
            self.db.setHostName(self.dbQvista['HostName'])
            self.db.setPort(self.dbQvista['Port'])
            self.db.setDatabaseName(self.dbQvista['DatabaseName'])
            self.db.setUserName(self.dbQvista['UserName'])
            self.db.setPassword(self.dbQvista['Password'])
    def __CONNECTA_BASE_DADES__(self,usuari):
        if not self.db.open():
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
        query.prepare("select nom_mapa from QV_MAPES_FAVORITS where iduser=:IDUSER")
        query.bindValue(':IDUSER',usuari)
        query.exec()
        res=[]
        while query.next():
            res.append(query.value(0))
        #Consulta
        self.__DESCONNECTA_BASE_DADES__(usuari,False)
        return res
        
    def afegeixFavorit(self,mapa,usuari=getpass.getuser().upper()):
        if not self.__CONNECTA_BASE_DADES__(usuari):
            return False
        query=QSqlQuery(self.db)
        query.prepare("insert into QV_MAPES_FAVORITS (iduser, nom_mapa) values (:IDUSER,:NOM_MAPA)")
        query.bindValue(':IDUSER',usuari)
        query.bindValue(':NOM_MAPA',mapa)
        if not query.exec():
            QMessageBox.critical(None,"Atenció","No s'ha pogut afegir el mapa a favorits. Intenteu-ho més tard, si us plau")
        self.__DESCONNECTA_BASE_DADES__(usuari)
        return True
        
    def eliminaFavorit(self,mapa,usuari=getpass.getuser().upper()):
        if not self.__CONNECTA_BASE_DADES__(usuari):
            return False
        query=QSqlQuery(self.db)
        query.prepare("delete from QV_MAPES_FAVORITS where iduser=:IDUSER and nom_mapa=:NOM_MAPA")
        query.bindValue(':IDUSER',usuari)
        query.bindValue(':NOM_MAPA',mapa)
        if not query.exec():
            QMessageBox.critical("Atenció","No s'ha pogut eliminar el mapa de favorits. Intenteu-ho més tard, si us plau")
        self.__DESCONNECTA_BASE_DADES__(usuari)
        return True
        

if __name__=='__main__':
    from qgis.core.contextmanagers import qgisapp
    with qgisapp() as app:
        fav=QvFavorits()
        fav.afegeixFavorit('Hola :D','DE1719')
        print(fav.getFavorits('DE1719'))
        fav.eliminaFavorit('Hola :D','DE1719')