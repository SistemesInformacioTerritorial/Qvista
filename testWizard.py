#!/usr/bin/env python
 
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty
from PyQt5 import QtCore, QtWidgets
 
 
class QvNews(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(QvNews, self).__init__(parent)
        for i in range(0,5):
            page = QtWidgets.QWizardPage()
            layout = QtWidgets.QVBoxLayout(page)
            page.setLayout(layout)
            caixaText = QtWidgets.QTextEdit()
            doc = QtGui.QTextDocument()
            doc.setHtml('d:/qvista/codi/qVistaweb2.html')
            
            text=open('d:/qvista/codi/Noticies_0.htm').read()
            caixaText.setHtml(text)
            layout.addWidget(caixaText)
            self.addPage(page)
        # self.addPage(Page1(self))
        # self.addPage(Page2(self))
        # self.addPage(Page1(self))
        self.setWindowTitle("qVista - Noticies")
        self.resize(640,480)
        # self.button(MagicWizard.BackButton).show()
 
class Page1(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(Page1, self).__init__(parent)
        # self.comboBox = QIComboBox(self)
        # self.comboBox.addItem("Python","/path/to/filename1")
        # self.comboBox.addItem("PyQt5","/path/to/filename2")
        layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(self.comboBox)
        self.setLayout(layout)
 
 
class Page2(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.label1 = QtWidgets.QLabel()
        self.label2 = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)
 
    def initializePage(self):
        self.label1.setText("Example text")
        self.label2.setText("Example text")
 
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    wizard = QvNews()
    wizard.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
    # wizard.button(MagicWizard.BackButton).show()
    buto = QtWidgets.QPushButton('hola')
    wizard.setSideWidget(buto)
    wizard.show()
    sys.exit(app.exec_())