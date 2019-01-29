# -*- coding: utf-8 -*-

import sys
from qgis.PyQt import QtCore, QtWidgets, QtWebKitWidgets
from moduls.QvApp import QvApp

class QvPDF(QtWebKitWidgets.QWebView):
    def __init__(self, pdf, page=1, zoom='auto'):
        super(QvPDF, self).__init__()
        self.pdf = pdf
        self.page = page
        self.zoom = zoom
        self.viewer = 'file:///' + QvApp().ruta + 'pdfjs/web/viewer.html'
        self.load(QtCore.QUrl.fromUserInput('%s?file=%s#page=%d&zoom=%s' % (self.viewer, self.pdf, self.page, self.zoom)))

# https://github.com/mozilla/pdf.js/wiki/Viewer-options

if __name__ == '__main__':

    from qgis.core.contextmanagers import qgisapp

    with qgisapp(sysexit=False) as app:

        PDF = 'file:///' + QvApp().ruta + 'pdfjs/web/compressed.tracemonkey-pldi-09.pdf'

        w = QvPDF(PDF)
        w.setGeometry(50, 50, 1200, 800)
        w.setWindowTitle('PDF widget')
        w.show()
