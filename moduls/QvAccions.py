# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QMenu, QAction
from qgis.PyQt.QtWidgets import QMessageBox, QWhatsThis


class QvAccions:

    def __init__(self):
        super().__init__()

        # Conjunto de acciones predefinidas
        self.accions = {}
        self.iniAccions()

    def accio(self, nom):
        if nom in self.accions:
            return self.accions[nom]
        else:
            return None

    def afegirAccio(self, nom, act):
        self.accions[nom] = act

    def _about(self):
        QMessageBox().information(None, 'Quant a', 'qVista - Versió 0.1')

    def iniAccions(self):
        act = QAction()
        act.setText('Quant a')
        act.triggered.connect(self._about)
        self.afegirAccio('about', act)

    def menuAccions(self, llistaAccions, accions=None, menuExtra=None):
        if QWhatsThis.inWhatsThisMode():
            return None
        if accions is None:
            accions = self.accions
        else:
            accions.update(self.accions)
        menu = QMenu()
        for nom in llistaAccions:
            if nom == 'separator':
                menu.addSeparator()
            elif nom in accions:
                item = accions[nom]
                if isinstance(item, QAction):
                    menu.addAction(item)
                elif isinstance(item, QMenu):
                    menu.addMenu(item)
        if menuExtra is not None:
            menu.addSeparator()
            menu.addMenu(menuExtra)
        return menu
