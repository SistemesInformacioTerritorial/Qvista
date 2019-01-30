# -*- coding: utf-8 -*-

from qgis.PyQt import QtCore
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.PyQt.QtWebKit import QWebSettings

from moduls.QvApp import QvApp

class QvPDF(QWebView):
    def __init__(self, pdf, page=1, zoom='auto', toolbar=True):
        super(QvPDF, self).__init__()
        self.pdf = pdf
        self.page = page
        self.zoom = zoom
        self.toolbar = toolbar
        self.carrega()

    def carrega(self):
        if self.toolbar:
            sufijo = ''
        else:
            sufijo = '_no_toolbar'
        viewer = 'file:///' + QvApp().ruta + 'pdfjs/web/viewer' + sufijo + '.html'
        self.load(QtCore.QUrl.fromUserInput('%s?file=%s#page=%d&zoom=%s' % (viewer, self.pdf, self.page, self.zoom)))

# https://github.com/mozilla/pdf.js/wiki/Viewer-options

if __name__ == '__main__':

    from qgis.core.contextmanagers import qgisapp

    with qgisapp(sysexit=False) as app:

        pdf = 'file:///' + QvApp().ruta + 'pdfjs/web/compressed.tracemonkey-pldi-09.pdf'

        w = QvPDF(pdf)
        # w = QvPDF(pdf, 5, 'page-width', False)

        w.setGeometry(50, 50, 1200, 800)
        w.setWindowTitle('PDF widget')
        w.show()
