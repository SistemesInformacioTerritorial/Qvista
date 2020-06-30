# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui

import os

from configuracioQvista import imatgesDir

TEMA_INICIAL = '(Inicial)'


class QvTema:

    def __init__(self, llegenda):
        self.llegenda = llegenda
        self.menu = qtWdg.QMenu('Temes')
        self.llegenda.root.visibilityChanged.connect(self.aplicaTitolTema)

    def temaInicial(self, crea=False):
        rec = qgCor.QgsMapThemeCollection.createThemeFromCurrentState(self.llegenda.root,
                                                                      self.llegenda.model)
        temaIni = self.buscaTema(rec)
        if temaIni is None and crea:
            self.creaTema(TEMA_INICIAL, rec)
        self.titolTema(temaIni)

    def temes(self):
        return self.llegenda.project.mapThemeCollection().mapThemes()

    def numTemes(self):
        return len(self.llegenda.project.mapThemeCollection().mapThemes())

    def buscaTema(self, rec=None):
        if rec is None:
            rec = qgCor.QgsMapThemeCollection.createThemeFromCurrentState(self.llegenda.root,
                                                                          self.llegenda.model)
        for tema in self.temes():
            if rec == self.llegenda.project.mapThemeCollection().mapThemeState(tema):
                return tema
        return None

    def existeTema(self, tema):
        # Busca temas de forma case-insensitive
        for item in self.temes():
            if item.upper() == tema.upper():
                return item
        return ''

    def creaTema(self, tema, rec=None):
        # Crea o actualiza tema
        if rec is None:
            rec = qgCor.QgsMapThemeCollection.createThemeFromCurrentState(self.llegenda.root,
                                                                          self.llegenda.model)
        temes = self.llegenda.project.mapThemeCollection()
        item = self.existeTema(tema)
        if item == '':
            temes.insert(tema, rec)
            return True, tema
        else:
            temes.update(item, rec)
            return False, item

    def esborraTema(self, tema):
        self.llegenda.project.mapThemeCollection().removeMapTheme(tema)

    def canviaNomTema(self, tema, nouTema):
        # A partir de la 3.14:
        # return self.llegenda.project.mapThemeCollection().renameMapTheme(tema, nouTema)
        try:
            temes = self.llegenda.project.mapThemeCollection()
            if temes.hasMapTheme(nouTema):  # case-sensitive
                return False
            rec = temes.mapThemeState(tema)
            temes.insert(nouTema, rec)
            temes.removeMapTheme(tema)
            return True
        except Exception as e:
            print(str(e))
            return False

    def aplicaTitolTema(self):
        if self.numTemes() == 0:
            return
        self.titolTema()

    def titolTema(self, tema=None):
        if tema is None:
            tema = self.buscaTema()
        if tema is not None and tema != TEMA_INICIAL:
            self.llegenda.setTitol('Tema ' + tema)
        else:
            self.llegenda.setTitol()

    def aplicaTema(self, tema):
        self.llegenda.project.mapThemeCollection().applyTheme(tema, self.llegenda.root,
                                                              self.llegenda.model)
        self.titolTema(tema)

    def menuAplicaTema(self):
        try:
            tema = self.llegenda.sender().text()
            self.aplicaTema(tema)
        except Exception as e:
            print(str(e))

    def menuNouTema(self):
        nom, ok = qtWdg.QInputDialog.getText(self.llegenda, self.llegenda.sender().text(),
                                             'Nom del tema: ', qtWdg.QLineEdit.Normal, '')
        nom = nom.strip()
        if not ok or nom == '':
            return
        nou, tema = self.creaTema(nom)
        self.titolTema()
        msg = f"Creat nou tema '{tema}'" if nou else f"Tema '{tema}' modificat"
        qtWdg.QMessageBox.information(self.llegenda, 'Informació', msg)

    def menuEsborraTema(self):
        actiu = self.buscaTema()
        txt = f"Estem a punt d'eliminar el tema '{actiu}'"
        res = qtWdg.QMessageBox.question(self.llegenda, 'Confirmació',
                                         txt + "\n\nVol continuar?")
        if res == qtWdg.QMessageBox.Yes:
            self.esborraTema(actiu)
            self.titolTema()
            # msg = f"Esborrat tema '{actiu}'"
            # qtWdg.QMessageBox.information(self.llegenda, 'Informació', msg)

    def menuCanviaNomTema(self):
        actiu = self.buscaTema()
        nom, ok = qtWdg.QInputDialog.getText(self.llegenda, self.llegenda.sender().text(),
                                             'Nou nom del tema: ', qtWdg.QLineEdit.Normal, actiu)
        nom = nom.strip()
        if not ok or nom == '' or nom == actiu:
            return
        ok = self.canviaNomTema(actiu, nom)
        if ok:
            self.titolTema()
        else:
            msg = f"No s'ha pogut canvia el nom del tema '{actiu}'"
            qtWdg.QMessageBox.critical(self.llegenda, 'Error', msg)

    def setMenuTemes(self):
        self.menu.clear()
        actiu = self.buscaTema()
        for tema in self.temes():
            if actiu is not None and actiu == tema:
                icon = qtGui.QIcon(os.path.join(imatgesDir, 'check-box.png'))
                self.menu.addAction(icon, tema, self.menuAplicaTema)
            else:
                self.menu.addAction(tema, self.menuAplicaTema)
        if self.llegenda.editable:
            self.menu.addSeparator()
            if actiu is None:  # or actiu == TEMA_INICIAL:
                if self.numTemes() > 0:
                    self.menu.addAction('Afegeix o modifica tema', self.menuNouTema)
                else:
                    self.menu.addAction('Afegeix tema', self.menuNouTema)
            else:
                self.menu.addAction(f"Canvia nom '{actiu}'", self.menuCanviaNomTema)
                self.menu.addAction(f"Esborra '{actiu}'", self.menuEsborraTema)
