import os
import shutil
import sys
import time
from pathlib import Path

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QPoint, Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (QDialog, QFileDialog, QFileSystemModel,
                                 QHBoxLayout, QLabel, QTreeView, QVBoxLayout,
                                 QWidget)

import configuracioQvista
from moduls.QvConstants import QvConstants
from moduls.QvMemoria import QvMemoria
from moduls.QvPushButton import QvPushButton
from moduls.QvVisorHTML import QvVisorHTML


class ElMeuModel(QFileSystemModel):
    def data(self,index,role):
        """Funció sobrecarregada per poder tunejar algun aspecte del tree view

        Arguments:
            index {QModelIndex} -- Índex que apunta a l'element del qual volem obtenir la informació
            role {int} -- Rol que fem servir (Qt.DecorationRole, Qt.DisplayRole...)

        Returns:
            QVariant -- Informació associada a l'índex utilitzant el rol indicat
        """

        # Si el rol és de decoració, podem tunejar algunes icones
        if role==Qt.DecorationRole:
            nom=index.data()
            if Path(nom).suffix == '.url':
                return QIcon(os.path.join(configuracioQvista.imatgesDir,'doc-web.png'))
        # Si el rol és de mostrar, podem tunejar el nom
        # Problema: si eliminem l'extensió, com distingim el tipus de l'arxiu???
        # elif role==Qt.DisplayRole:
        #     res=super().data(index,role)
        #     return Path(res).stem
        return super().data(index,role)

class QvDocumentacio(QDialog):
    comencaCarrega = pyqtSignal()
    acabaCarrega = pyqtSignal()
    '''Diàleg que mostra la documentació de la carpeta de documentació definida a configuracioQvista
    Mostra una TreeView amb els documents, i delega en el sistema la tasca d'obrir-los'''
    def __init__(self,parent: QWidget=None):
        super().__init__(parent)
        self.setMinimumSize(750,500)
        #Layout principal. Tot aquí
        self.layout=QVBoxLayout(self)
        #Layout de la capçalera
        self.layoutCapcalera=QHBoxLayout()
        self.lblTitol=QLabel('  Documentació')
        self.layoutCapcalera.addWidget(self.lblTitol)

        self.qModel=ElMeuModel(self)
        self.lblExplicacio=QLabel()
        if os.path.isdir(configuracioQvista.carpetaDocuments):
            self.lblExplicacio.setText('Esteu visualitzant la documentació corporativa completa')
            rootPath=self.qModel.setRootPath(configuracioQvista.carpetaDocuments)
        else:
            self.lblExplicacio.setText('No teniu accés a la documentació corporativa. Esteu visualitzant una còpia local que pot no estar actualitzada.')
            rootPath=self.qModel.setRootPath(configuracioQvista.carpetaDocumentsLocal)
        self.treeView=QTreeView(self)
        self.treeView.setModel(self.qModel)
        self.treeView.setRootIndex(rootPath)
        self.treeView.clicked.connect(self.clicat)
        self.treeView.doubleClicked.connect(self.obrir)

        self.layoutBotonera=QHBoxLayout()
        self.layoutBotonera.addStretch()
        self.botoObrir=QvPushButton('Obrir',destacat=True)
        self.botoObrir.setEnabled(False)
        self.botoObrir.clicked.connect(self.obrir)
        self.layoutBotonera.addWidget(self.botoObrir)
        self.botoDescarregar=QvPushButton('Descarregar')
        self.botoDescarregar.setEnabled(False)
        self.botoDescarregar.clicked.connect(self.desar)
        self.layoutBotonera.addWidget(self.botoDescarregar)
        self.botoSortir=QvPushButton('Sortir')
        self.botoSortir.clicked.connect(self.close)
        self.layoutBotonera.addWidget(self.botoSortir)

        self.layout.addLayout(self.layoutCapcalera)
        self.layout.addWidget(self.lblExplicacio)
        self.layout.addWidget(self.treeView)
        self.layout.addLayout(self.layoutBotonera)
        self.formata()

    def formata(self):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.layout.setAlignment(Qt.AlignCenter)

        self.lblTitol.setStyleSheet('background-color: %s; color: %s; border: 0px' % (
            QvConstants.COLORFOSCHTML, QvConstants.COLORBLANCHTML))
        self.lblTitol.setFont(QvConstants.FONTCAPCALERES)
        self.lblTitol.setFixedHeight(40)

        self.lblExplicacio.setWordWrap(True)
        self.lblExplicacio.setStyleSheet(f'color: {QvConstants.COLORFOSCHTML}; margin: 20px 20px 0px 20px')

        for i in range(1,4):
            self.treeView.header().hideSection(i)
        self.treeView.setHeaderHidden(True)
        self.treeView.adjustSize()
        self.treeView.setAnimated(True)
        self.treeView.setStyleSheet('QTreeView{margin: 20px 2px 0px 20px; border: none;}')

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layoutBotonera.setContentsMargins(10,10,10,10)

    def clicat(self,index: int):
        path=self.qModel.fileInfo(index).absoluteFilePath()
        self.index=index
        if os.path.isfile(path):
            self.botoObrir.setEnabled(True)
            self.botoDescarregar.setEnabled(True)
        else:
            self.botoObrir.setEnabled(False)
            self.botoDescarregar.setEnabled(True)

    def obrir(self):
        path=self.qModel.fileInfo(self.index).absoluteFilePath()
        if os.path.isfile(path):
            self.comencaCarrega.emit()
            if '.html' in path:
                self.visor = QvVisorHTML(path,'Vídeo de documentació')
                self.visor.setZoomFactor(1)
                self.visor.show()
            else:
                os.startfile(path)
            time.sleep(1)
            self.acabaCarrega.emit()

    def desar(self):
        path=self.qModel.fileInfo(self.index).absoluteFilePath()
        if os.path.isfile(path):
            nfile,_=QFileDialog.getSaveFileName(None,'Desar arxiu',os.path.join(QvMemoria().getDirectoriDesar(),Path(path).name))
            if nfile!='': shutil.copy(path,nfile)
        else:
            nomCarpeta=Path(path).name
            nfile = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            if nfile!='': shutil.copytree(path,os.path.join(nfile,nomCarpeta))

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key()==Qt.Key_Return:
            self.obrir()

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    doc=QvDocumentacio()
    doc.show()
    sys.exit(app.exec_())