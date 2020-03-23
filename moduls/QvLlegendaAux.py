# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsLegendModel, QgsLayerTreeNode
from qgis.gui import QgsLayerTreeViewMenuProvider

class QvItemLlegenda(object):

    def __init__(self, item, nivell):
        super().__init__()
        self.item = item
        self.nivell = nivell
        self.tipus = self.calcTipus()

    def calcTipus(self):
        clase = type(self.item).__name__
        if clase == 'QgsLayerTreeLayer':
            return 'layer'
        elif clase == 'QgsLayerTreeGroup':
            return 'group'
        elif clase == 'QgsLayerTreeModelLegendNode':
            return 'symb'
        else:
            return 'none'

    def capa(self):
        if self.tipus == 'layer':
            return self.item.layer()
        elif self.tipus == 'group':
            return None
        elif self.tipus == 'symb':
            return self.item.layerNode().layer()
        else:
            return None

    def nom(self):
        if self.tipus in ('layer', 'group'):
            return self.item.name()
        elif self.tipus == 'symb':
            return self.item.data(Qt.DisplayRole)
        else:
            return None

    def esMarcat(self):
        if self.tipus in ('layer', 'group'):
            return self.item.itemVisibilityChecked()
        elif self.tipus == 'symb':
            return self.item.data(Qt.CheckStateRole) != 0
        else:
            return None

    def marcar(self, switch=True):
        if self.tipus in ('layer', 'group'):
            self.item.setItemVisibilityChecked(switch)
        elif self.tipus == 'symb':
            if switch:
                self.item.setData(Qt.Checked, Qt.CheckStateRole)
            else:
                self.item.setData(Qt.Unchecked, Qt.CheckStateRole)

    def esVisible(self):
        if self.tipus in ('layer', 'group'):
            return self.item.isVisible()
        elif self.tipus == 'symb':
            return self.esMarcat() and self.item.layerNode().isVisible()
        else:
            return None

    def veure(self, switch=True, children=True):
        if self.tipus in ('layer', 'group'):
            if switch:
                self.item.setItemVisibilityCheckedParentRecursive(True)
                if children:
                    self.item.setItemVisibilityCheckedRecursive(True)
            else:
                self.marcar(False)
        elif self.tipus == 'symb':
            self.marcar(switch)
            if switch:
                self.item.layerNode().setItemVisibilityCheckedParentRecursive(True)
                if children:
                    self.item.layerNode().setItemVisibilityCheckedRecursive(True)

class QvModelLlegenda(QgsLegendModel):
    def __init__(self, root):
        super().__init__(root)
        self.setScale(1.0)

    def setScale(self, scale):
        self.scale = scale

    def data(self, index, role):
        if index.isValid() and role == Qt.ForegroundRole:
            node = self.index2node(index)
            if node is not None and node.nodeType() == QgsLayerTreeNode.NodeLayer:
                layer = node.layer()
                if layer is not None and layer.hasScaleBasedVisibility():
                    if layer.isInScaleRange(self.scale):
                        color = QColor('#000000')
                    else:
                        color = QColor('#c0c0c0')
                    return color
        return super().data(index, role)

class QvMenuLlegenda(QgsLayerTreeViewMenuProvider):

    def __init__(self, llegenda):
        QgsLayerTreeViewMenuProvider.__init__(self)
        self.llegenda = llegenda

    def createContextMenu(self):
        tipo = self.llegenda.setMenuAccions()
        self.llegenda.clicatMenuContexte.emit(tipo)
        return self.llegenda.accions.menuAccions(self.llegenda.menuAccions)
