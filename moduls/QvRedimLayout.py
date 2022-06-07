#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

#Codi copiat de https://github.com/baoboa/pyqt5/blob/master/examples/layouts/flowlayout.py

from qgis.PyQt.QtCore import QPoint, QRect, QSize, Qt
from qgis.PyQt.QtWidgets import (QApplication, QLayout, QPushButton, QSizePolicy,
        QWidget)


class QvRedimLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(QvRedimLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(QvRedimLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        self.posicions={} #Desarem les posicions dels elements del layout en un diccionari, on la clau serà el widget i el valor serà una tupla amb les posicions
        self.elements=[[]]
        i, j = 0, 0
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
                #Passem a la línia següent
                i+=1
                j=0
                self.elements.append([])

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            self.posicions[wid]=(i,j)
            self.elements[i].append(wid)

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
            j+=1 #Següent posició

        return y + lineHeight - rect.y()
    
    def indexsOf(self,widget):
        if widget in self.posicions:
            return self.posicions[widget]
        return None
    def widgetAt(self,i,j):
        if i<0:
            return self.elements[0][0]
        if i<len(self.elements):
            if j<0:
                #Si la j és més petita que 0, i la i és major que 1, tornem l'últim element de la fila anterior
                if i>0:
                    return self.elements[i-1][-1]
                return self.elements[i][0]
            if j<len(self.elements[i]):
                return self.elements[i][j]
            # return self.elements[i][-1]
            #Això de sota no es farà
            if i+1<len(self.elements):
                return self.elements[i+1][0]
        else:
            return self.elements[-1][-1]
    def y(self):
        '''Retorna la quantitat de files que té el layout'''
        return len(self.elements)
    def x(self,i):
        '''Retorna la quantitat de columnes que té la fila i (ja que cada fila pot tenir nombre diferent de columnes)'''
        return len(self.elements[i])
    def keyPressEvent(self,event):
        if event.key()==Qt.Key_Left:
            return
        super().keyPressEvent(event)

