# -*- coding: utf-8 -*-

import qgis.PyQt.QtCore as qtCor
import qgis.PyQt.QtGui as qtGui
import qgis.core as qgCor
import qgis.gui as qgGui


class QvItemLlegenda:

    def __init__(self, item, nivell):
        self.item = item
        self.nivell = nivell
        self.tipus = self.calcTipus()

    def calcTipus(self):
        clase = type(self.item).__name__
        if clase == 'QgsLayerTreeLayer':
            return 'layer'
        elif clase == 'QgsLayerTreeGroup':
            return 'group'
        elif clase in ('QgsSymbolLegendNode', 'QgsLayerTreeModelLegendNode'):
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
            return self.item.data(qtCor.Qt.DisplayRole)
        else:
            return None

    def esMarcat(self):
        if self.tipus in ('layer', 'group'):
            return self.item.itemVisibilityChecked()
        elif self.tipus == 'symb':
            return self.item.data(qtCor.Qt.CheckStateRole) != 0
        else:
            return None

    def marcar(self, switch=True):
        if self.tipus in ('layer', 'group'):
            self.item.setItemVisibilityChecked(switch)
        elif self.tipus == 'symb':
            if switch:
                self.item.setData(qtCor.Qt.Checked, qtCor.Qt.CheckStateRole)
            else:
                self.item.setData(qtCor.Qt.Unchecked, qtCor.Qt.CheckStateRole)

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


class QvModelLlegenda(qgCor.QgsLegendModel):
    def __init__(self, root):
        super().__init__(root)
        self.setScale(1.0)

    def setScale(self, scale):
        self.scale = scale

    def data(self, index, role):
        if index.isValid() and role == qtCor.Qt.ForegroundRole:
            node = self.index2node(index)
            if node is not None and node.nodeType() == qgCor.QgsLayerTreeNode.NodeLayer:
                layer = node.layer()
                if layer is not None and layer.hasScaleBasedVisibility():
                    if layer.isInScaleRange(self.scale):
                        color = qtGui.QColor('#000000')
                    else:
                        color = qtGui.QColor('#c0c0c0')
                    return color
        return super().data(index, role)


class QvMenuLlegenda(qgGui.QgsLayerTreeViewMenuProvider):

    def __init__(self, llegenda):
        qgGui.QgsLayerTreeViewMenuProvider.__init__(self)
        self.llegenda = llegenda

    def createContextMenu(self):
        tipo = self.llegenda.setMenuAccions()
        self.llegenda.clicatMenuContexte.emit(tipo)
        return self.llegenda.accions.menuAccions(self.llegenda.menuAccions,
                                                 menuExtra=self.llegenda.menuExtra)
