from moduls.QvImports import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileSystemModel, QTreeView, QWidget
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from pathlib import Path
import shutil

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

        
        self.qModel=QFileSystemModel(self)
        rootPath=self.qModel.setRootPath(carpetaDocuments)
        self.treeView=QTreeView(self)
        self.treeView.setModel(self.qModel)
        self.treeView.setRootIndex(rootPath)
        self.treeView.clicked.connect(self.clicat)
        self.treeView.doubleClicked.connect(self.obrir)
        # self.treeView.introPressed.connect(self.obrir)


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
        self.layout.addWidget(self.treeView)
        self.layout.addLayout(self.layoutBotonera)
        self.formata()
    def formata(self):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.lblTitol.setStyleSheet('background-color: %s; color: %s; border: 0px' % (
            QvConstants.COLORFOSCHTML, QvConstants.COLORBLANCHTML))
        self.lblTitol.setFont(QvConstants.FONTCAPCALERES)
        self.lblTitol.setFixedHeight(40)

        for i in range(1,4):
            self.treeView.header().hideSection(i)
        self.treeView.setHeaderHidden(True)
        self.treeView.adjustSize()
        self.treeView.setAnimated(True)
        # self.treeView.setStyleSheet('QTreeView{background: transparent; border: 1px solid #38474F;}')
        self.treeView.setStyleSheet('QTreeView{margin: 20px 2px 0px 20px; border: none;}')

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layoutBotonera.setContentsMargins(10,10,10,10)
        # self.treeView.setStyleSheet('padding: 5px; background: white')
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
            os.startfile(path)
            time.sleep(1)
            self.acabaCarrega.emit()
        else:
            pass
        #Ara la fem
    def desar(self):
        path=self.qModel.fileInfo(self.index).absoluteFilePath()
        if os.path.isfile(path):
            # nouPath=str(Path.home())+'/'+Path(path).name
            # print(nouPath)
            # nfile, _=QFileDialog.getSaveFileName(None,"Desar arxiu", nouPath)
            nfile,_=QFileDialog.getSaveFileName(None,'Desar arxiu',Path(path).name)
            if nfile!='': shutil.copy(path,nfile)
        else:
            nomCarpeta=Path(path).name
            nfile = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            if nfile!='': shutil.copytree(path,nfile+'/'+nomCarpeta)

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