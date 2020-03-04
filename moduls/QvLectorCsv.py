#!/usr/bin/python3
# -*- coding:utf-8 -*-
import csv
import codecs #???
import os

from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtGui import QImage, QPainter #QImage (???)
from moduls.QvPushButton import QvPushButton
import io


class QvLectorCsv(QtWidgets.QWidget):

    def __init__(self, csvName, csv=None, separador=None, completa=False, guardar=False, parent=None):
        QtWidgets.QWidget.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.fileName = csvName
        self.model = QtGui.QStandardItemModel(self)
        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 50, 780, 645)
        self.model.dataChanged.connect(self.finishedEdit)

        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        grid.addWidget(self.tableView, 0, 0, 1, 9)
        # if guardar:  # aixo no s'arriba a executar mai
        #     bGuardar = QvPushButton()
        #     bGuardar.setText("Guardar CSV")
        #     bGuardar.clicked.connect(self.writeCsv)
        #     grid.addWidget(bGuardar, 0, 0, 2, 9)
        if guardar:
            bGuardar=QvPushButton(text='Desar CSV',parent=self)
            bGuardar.clicked.connect(lambda: self.writeCsv(self.fileName))
            grid.addWidget(bGuardar,0,0,2,9)

        self.setLayout(grid)

        item = QtGui.QStandardItem()
        self.model.appendRow(item)
        self.model.setData(self.model.index(0, 0), "", 0)
        self.tableView.resizeColumnsToContents()


        self.separador = separador
        self.fname=os.path.splitext(str(csvName))[0].split("/")[-1]
        self.setWindowTitle(self.fname)
        if self.separador is not None:
            self.carregaCsv(csvName,csv,separador,completa)

    # def carregaCsv(self, fileName):
    #     if fileName:
    #         print(fileName)
    #         ff = open(fileName, 'r')
    #         mytext = ff.read()
    #         ff.close()
    #         f = open(fileName, 'r')
    #         with f:
    #             self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
    #             self.setWindowTitle(self.fname)
    #             if mytext.count(';') <= mytext.count('\t'):
    #                 reader = csv.reader(f, delimiter='\t')
    #                 self.model.clear()
    #                 for row in reader:
    #                     items = [QtGui.QStandardItem(field) for field in row]
    #                     self.model.appendRow(items)
    #                 self.tableView.resizeColumnsToContents()
    #             else:
    #                 reader = csv.reader(f, delimiter=';')
    #                 self.model.clear()
    #                 for row in reader:
    #                     items = [QtGui.QStandardItem(field) for field in row]
    #                     self.model.appendRow(items)
    #                 self.tableView.resizeColumnsToContents()
    def carregaCsv(self, filename, file=None, separador=None, completa=False):
        if file is None:
            self.carregaCsvNom(filename, self.separador, completa)
        elif isinstance(file,io.TextIOBase): #És l'arxiu
            self.carregaCsvFile(file, filename, self.separador,completa)
    def carregaCsvNom(self, fileName, separador=None, completa=False):
        if separador is None:
            super().carregaCsv(fileName)
            return
        if fileName:
            f = open(fileName, 'r',errors='ignore')
            with f:
                self.carregaCsvFile(f,fileName,separador,completa)
    def carregaCsvFile(self,f, fname, separador,completa=False):
        from PyQt5 import QtGui
        self.setWindowTitle(self.fname)
        if not isinstance(separador, str):
            separador = ';'
        reader = csv.reader(f, delimiter=separador)
        self.model.clear()
        i = 0
        for row in reader:
            if not completa and i > 9:
                break  # Per agilitzar la càrrega, només ens cal una preview petita
            items = [QtGui.QStandardItem(field) for field in row]
            
            if (i==0): 
                self.model.setHorizontalHeaderLabels([x.text() for x in items])
            else:
                self.model.appendRow(items)
            i += 1
        self.tableView.resizeColumnsToContents()
        self.file=f

    def writeCsv(self, file):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File",
                        (QtCore.QDir.homePath() + "/" + self.fname + '_qVista' + ".csv"), "CSV Files (*.csv)")
        if fileName:
            with open(fileName,'w', newline='') as sortida:
                reader=csv.reader(file,delimiter=self.separador)
                writer=csv.writer(sortida,delimiter=';')
                for x in reader:
                    writer.writerow(x)
    def getFile(self):
        self.file.seek(0)
        return self.file
    def recarrega(self, separador, completa=False):
        self.separador = separador
        self.carregaCsv(self.fileName,self.getFile(), separador=self.separador, completa=completa)

    def verticalScrollBar(self):
        return self.tableView.verticalScrollBar()

    def horizontalScrollBar(self):
        return self.tableView.horizontalScrollBar()
    def handlePrint(self): 
        dialog = QtPrintSupport.QPrintDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.handlePaintRequest(dialog.printer())

    def handlePreview(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.setFixedSize(1000, 700)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    def handlePaintRequest(self, printer):
        # find empty cells
        for row in range(self.model.rowCount()):
            for column in range(self.model.columnCount()):
                myitem = self.model.item(row, column)
                if myitem is None:
                    item = QtGui.QStandardItem("")
                    self.model.setItem(row, column, item)
        printer.setDocName(self.fname)
        document = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(document)
        model = self.tableView.model()
        table = cursor.insertTable(model.rowCount(), model.columnCount())
        for row in range(table.rows()):
            for column in range(table.columns()):
                cursor.insertText(model.item(row, column).text())
                cursor.movePosition(QtGui.QTextCursor.NextCell)
        document.print_(printer)

    def removeRow(self):
        model = self.model
        indices = self.tableView.selectionModel().selectedRows()
        for index in sorted(indices):
            model.removeRow(index.row())

    def addRow(self):
        item = QtGui.QStandardItem("")
        self.model.appendRow(item)

    def clearList(self):
        self.model.clear()

    def removeColumn(self):
        model = self.model
        indices = self.tableView.selectionModel().selectedColumns()
        for index in sorted(indices):
            model.removeColumn(index.column())

    def addColumn(self):
        count = self.model.columnCount()
        # print(count)
        self.model.setColumnCount(count + 1)
        self.model.setData(self.model.index(0, count), "", 0)
        self.tableView.resizeColumnsToContents()

    def finishedEdit(self):
        self.tableView.resizeColumnsToContents()

    def contextMenuEvent(self, event):
        return None  # Forzamos salida, no interesa gestionar este evento (deberiamos eliminar este trozo de codigo pero mola coma ejemplo)
        
        self.menu = QtWidgets.QMenu(self)
        # copy
        copyAction = QtWidgets.QAction('Copy', self)
        copyAction.triggered.connect(lambda: self.copyByContext(event))
        # paste
        pasteAction = QtWidgets.QAction('Paste', self)
        pasteAction.triggered.connect(lambda: self.pasteByContext(event))
        # cut
        cutAction = QtWidgets.QAction('Cut', self)
        cutAction.triggered.connect(lambda: self.cutByContext(event))
        # delete selected Row
        removeAction = QtWidgets.QAction('delete Row', self)
        removeAction.triggered.connect(lambda: self.deleteRowByContext(event))
        # add Row after
        addAction = QtWidgets.QAction('insert new Row after', self)
        addAction.triggered.connect(lambda: self.addRowByContext(event))
        # add Row before
        addAction2 = QtWidgets.QAction('insert new Row before', self)
        addAction2.triggered.connect(lambda: self.addRowByContext2(event))
        # add Column before
        addColumnBeforeAction = QtWidgets.QAction(
            'insert new Column before', self)
        addColumnBeforeAction.triggered.connect(
            lambda: self.addColumnBeforeByContext(event))
        # add Column after
        addColumnAfterAction = QtWidgets.QAction(
            'insert new Column after', self)
        addColumnAfterAction.triggered.connect(
            lambda: self.addColumnAfterByContext(event))
        # delete Column
        deleteColumnAction = QtWidgets.QAction('delete Column', self)
        deleteColumnAction.triggered.connect(
            lambda: self.deleteColumnByContext(event))
        # add other required actions
        self.menu.addAction(deleteColumnAction)
        self.menu.popup(QtGui.QCursor.pos())
        
    def deleteRowByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            row = i.row()
            self.model.removeRow(row)
            # print("Row " + str(row) + " deleted")
            self.tableView.selectRow(row)

    def addRowByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            row = i.row() + 1
            self.model.insertRow(row)
            # print("Row at " + str(row) + " inserted")
            self.tableView.selectRow(row)

    def addRowByContext2(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            row = i.row()
            self.model.insertRow(row)
            # print("Row at " + str(row) + " inserted")
            self.tableView.selectRow(row)

    def addColumnBeforeByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            col = i.column()
            self.model.insertColumn(col)
            # print("Column at " + str(col) + " inserted")

    def addColumnAfterByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            col = i.column() + 1
            self.model.insertColumn(col)
            # print("Column at " + str(col) + " inserted")

    def deleteColumnByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            col = i.column()
            self.model.removeColumn(col)
            # print("Column at " + str(col) + " removed")

    def copyByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            row = i.row()
            col = i.column()
            myitem = self.model.item(row, col)
            if myitem is not None:
                clip = QtWidgets.QApplication.clipboard()
                clip.setText(myitem.text())

    def pasteByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            row = i.row()
            col = i.column()
            myitem = self.model.item(row, col)
            clip = QtWidgets.QApplication.clipboard()
            myitem.setText(clip.text())

    def cutByContext(self, event):
        for i in self.tableView.selectionModel().selection().indexes():
            row = i.row()
            col = i.column()
            myitem = self.model.item(row, col)
            if myitem is not None:
                clip = QtWidgets.QApplication.clipboard()
                clip.setText(myitem.text())
                myitem.setText("")


def stylesheet(self):
    return """
        QTableView{
            border: 1px solid grey;
            border-radius: 0px;
            font-size: 12px;
                    background-color: #f8f8f8;
            selection-color: white;
            selection-background-color: #111111;
        }

        QTableView QTableCornerButton::section {
            background: #D6D1D1;
            border: 1px outset black;
        }

        QPushButton{
            font-size: 11px;
            border: 1px inset grey;
            height: 24px;
            width: 80px;
            color: black;
            background-color: #e8e8e8;
            background-position: bottom-left;
        } 

        QPushButton::hover{
            border: 2px inset goldenrod;
            font-weight: bold;
            color: #e8e8e8;
            background-color: green;
        } 
"""

# from qgis.core.contextmanagers import qgisapp
# with qgisapp() as app:
#     app.setApplicationName('MyWindow')
#     main = MyWindow('')
#     main.setMinimumSize(820, 300)
#     main.setGeometry(0,0,820,700)
#     main.setWindowTitle("CSV Viewer")
#     main.show()
