# -*- coding: utf-8 -*-

from typing import List
import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

from pathlib import Path, PureWindowsPath
from typing import Tuple
import json

class QvAnnotation:
    """Métodos estáticos relacionados con anotaciones
    """
    @staticmethod 
    def toolTipText(item: qgGui.QgsMapCanvasAnnotationItem) -> str:
        try:
            layer = item.annotation().mapLayer()
            if layer is None:
                return "Anotació general del mapa"
            else:
                return f"Anotació de la capa '{layer.name()}'"
        except:
            return ''

    @staticmethod 
    def updateMargins(item: qgGui.QgsMapCanvasAnnotationItem, margin: float) -> None:
        margen = qgCor.QgsMargins()
        margen.setTop(margin)
        item.setContentsMargin(margen)

class QvAnnotationHtml:
    def __init__(self, font: str = 'Arial', size: str = 'normal') -> None:
        """Generación de html para definir el texto enriquecido de una anotación

        Args:
            font (str, optional): Fuente del texto. Defaults to 'Arial'.
            size (str, optional): Tamaño del texto ('small', 'normal' o 'large'). Defaults to 'normal'.
        """
        self.htmlIni = '<body style="background-color:transparent;font-family:{font}">'
        self.htmlTit = '<p align="center" style="margin:12px;font-size:{size};font-weight:bold">{text}</p>'
        self.htmlTxt = '<p align="left" style="margin:8px;font-size:{size};text-indent:8px">{text}</p>'
        self.htmlFin = '</body>'
        self.setFont(font)
        self.setSize(size)

    def setFont(self, font: str = '') -> None:
        if font is None or font.strip() == '':
            font = 'Arial'
        self.font = font.strip()

    def setSize(self, size: str = '') -> None:
        if size is None or size.strip() == '':
            size = 'normal'
        size = size.lower().strip()
        if size == 'small':
            val = ('small', 'normal')
        elif size == 'large':
            val = ('large', 'x-large')
        else:
            val = ('normal', 'large')
        self.sizeTxt, self.sizeTit = val

    def calc(self, titulo: str, texto: str) -> str:
        html = self.htmlIni.format(font=self.font)
        if titulo != '':
            html += self.htmlTit.format(size=self.sizeTit, text=titulo)
        for linea in texto.splitlines():
            html += self.htmlTxt.format(size=self.sizeTxt, text=linea.strip())
        html += self.htmlFin
        return html

class QvAnnotationParams:
    def __init__(self, file: str = '') -> None:
        """Gestión de los estilos de una anotación. Cada estilo incluye parámetros de texto y 
           de los símbolos de marca y relleno

        Args:
            file (str, optional): Fichero json que contiene la lista de estilos. Default to: se
                                  usa el mismo nombre que el fichero acutal con extensión 'json'.
        """
        if file == '':
            self.file = PureWindowsPath(__file__).with_suffix('.json')
        else:
            self.file = file
        self.list = None
        self.item = None

    def read(self) -> bool:
        try:
            self.list = json.loads(Path(self.file).read_text(encoding="utf-8"))
            return True
        except Exception as e:
            print(str(e))
            self.list = None
            return True

    def names(self) -> Tuple[str, dict]:
        for item in self.list:
            if 'name' in item:
                yield item['name'], item

    def byName(self, name: str) -> None:
        for n, item in self.names():
            if name == n:
                self.item = item
                return True
        self.item = None
        return False

    def setColorTransparency(self, params: dict) -> None:
        try:
            alpha = params.get('alpha')
            color = params.get('color')
            if alpha is None or color is None:
                return
            del params['alpha']
            qColor = qgCor.QgsSymbolLayerUtils.decodeColor(color)
            qColor.setAlpha(256 * float(alpha))
            params['color'] = qgCor.QgsSymbolLayerUtils.encodeColor(qColor)
        except Exception as e:
            print(str(e))

    def paramsSymbol(self, id: str) -> dict:
        if id in self.item:
            params = self.item[id]
            self.setColorTransparency(params)
            return params
        else:
            return None

class QvAnnotationDoc:
    def __init__(self, doc: qtGui.QTextDocument) -> None:
        """Gestión del documento de una anotación, manejando su título y texto y
           la metainformación asociada

        Args:
            doc (qtGui.QTextDocument): Documento de la anotación
        """
        self.doc = doc
        self.setMetaInfo()
        self.setText()

    def setMetaInfo(self) -> None:
        meta = self.doc.metaInformation(qtGui.QTextDocument.DocumentTitle)
        try:
            self.titulo = meta.split("\n")[0]
        except:
            self.titulo = ''
        try:
            self.estilo = meta.split("\n")[1]
        except:
            self.estilo = ''

    def setText(self) -> None:
        self.texto = self.doc.toPlainText()

    def update(self, estilo: str, titulo: str, texto: str,  html: str) -> None:
        self.estilo = estilo
        self.titulo = titulo
        self.texto = texto
        self.doc.setHtml(html)
        meta = self.titulo + '\n' + self.estilo
        self.doc.setMetaInformation(qtGui.QTextDocument.DocumentTitle, meta)

class QvAnnotationDialog(qtWdg.QDialog):
    def __init__(self, llegenda, item: qgGui.QgsMapCanvasAnnotationItem, title: str = 'Anotació'):
        """Cuadro de diálogo de edición de las características de las anotaciones

        Args:
            llegenda (QvLlegenda).
            item (QgsMapCanvasAnnotationItem): item de la anotación a modificar.
            title (str, optional): título del formulario. Defaults to 'Anotació'.
        """
        self.llegenda = llegenda
        super().__init__(llegenda.canvas)
        self.setWindowTitle(title)
        self.item = item
        self.toolName = 'Anotacions'
        self.layout = qtWdg.QFormLayout()
        self.setLayout(self.layout)

        # Capas disponibles
        self.layers = qtWdg.QComboBox(self)
        self.layers.setEditable(False)
        self.layers.addItem('(Tot el mapa)', None)
        current = item.annotation().mapLayer() or self.llegenda.currentLayer()
        index = 0
        for i in llegenda.items():
            if i.tipus == 'layer' and i.esVisible():  # Solo visibles
                layer = i.capa()
                self.layers.addItem(layer.name(), layer.id())
                if current and current.id() == layer.id():
                    index = self.layers.count() - 1
        self.layers.setCurrentIndex(index)

        # Leer metadatos del documento
        self.doc = QvAnnotationDoc(self.item.annotation().document())

        # Estilos disponibles (json)
        self.params = QvAnnotationParams()
        if self.params.read():
            self.estil = qtWdg.QComboBox(self)
            self.estil.setEditable(False)
            self.estil.addItem('(Cap)')
            current = 0
            i = 1
            for estilo, _ in self.params.names():
                self.estil.addItem(estilo)
                if estilo == self.doc.estilo:
                    current = i
                i = i + 1
            self.estil.setCurrentIndex(current)
        else:
            self.estil = None

        # Posición fija
        self.position = qtWdg.QCheckBox(self)
        if item.annotation().hasFixedMapPosition():
            self.position.setCheckState(qtCor.Qt.Checked)
        else:
            self.position.setCheckState(qtCor.Qt.Unchecked)

        # Titulo de la nota
        self.title = qtWdg.QLineEdit(self.doc.titulo, self)

        # Texto de la nota
        self.text = qtWdg.QTextEdit(self)
        lineaTitulo = True and self.doc.titulo != ''
        for linea in self.doc.texto.split("\n"):
            if lineaTitulo:
                lineaTitulo = False
                continue
            self.text.append(linea)
        self.text.setAcceptRichText(False)

        # Botones
        self.bDelete = qtWdg.QPushButton('Esborra')
        self.bDelete.clicked.connect(self.delete)

        self.buttons = qtWdg.QDialogButtonBox(self)
        self.buttons.addButton(qtWdg.QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.buttons.addButton(qtWdg.QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)
        self.buttons.addButton(self.bDelete, qtWdg.QDialogButtonBox.ResetRole)
        [button.setMaximumWidth(90) for button in self.buttons.buttons()]

        # Formulario
        self.layout.addRow('Capa associada:', self.layers)
        self.layout.addRow('Posició fixa:', self.position)
        if self.estil:
            self.layout.addRow('Estil:', self.estil)
        self.layout.addRow('Títol:', self.title)
        self.layout.addRow('Nota:', self.text)
        self.layout.addRow(self.buttons)

    def accept(self):
        layerId = self.layers.currentData()
        if layerId:
            layer = self.llegenda.project.mapLayer(layerId)
        else:
            layer = None
        if self.item is None:
            self.hide()
            return
        self.item.annotation().setMapLayer(layer)
        self.item.setToolTip(QvAnnotation.toolTipText(self.item))
        self.item.annotation().setHasFixedMapPosition(self.position.isChecked())

        # Tratamiento del estilo (símbolos de marca y relleno)
        estilo = ''
        paramsText = None
        if self.estil and self.estil.currentIndex() >= 0:
            try:
                # - Marker: https://qgis.org/api/qgsmarkersymbollayer_8cpp_source.html#l00715
                # - Formas: https://qgis.org/api/qgsmarkersymbollayer_8cpp_source.html#l00292
                # - Fill: https://qgis.org/api/qgsfillsymbollayer_8cpp_source.html#l00150
                # - Colores: https://www.w3.org/TR/SVG11/types.html#ColorKeywords
                if self.estil.currentIndex() == 0:
                    estilo = self.doc.estilo # Aplicar estilo anterior
                else:
                    estilo = self.estil.currentText()
                if self.params.byName(estilo):
                    paramsMarker = self.params.paramsSymbol('marker')
                    if paramsMarker:
                        markerSymbol = qgCor.QgsMarkerSymbol.createSimple(paramsMarker)
                        self.item.annotation().setMarkerSymbol(markerSymbol)
                    paramsFill = self.params.paramsSymbol('fill')
                    if paramsFill:
                        fillSymbol = qgCor.QgsFillSymbol.createSimple(paramsFill)
                        self.item.annotation().setFillSymbol(fillSymbol)
                    paramsText = self.params.item.get('text')
            except Exception as e:
                print(str(e))

        # Generar html de la nota
        htmlDoc = QvAnnotationHtml()
        if paramsText:
            htmlDoc.setFont(paramsText.get('font'))
            htmlDoc.setSize(paramsText.get('size'))
        titulo = self.title.text().strip()
        texto = self.text.toPlainText().strip()
        html = htmlDoc.calc(titulo, texto)

        # Actualizar márgenes
        if paramsText:
            margin = float(paramsText.get('margin', 2.5))
        else:
            margin = 2.5
        QvAnnotation.updateMargins(self.item.annotation(), margin)
        
        # Actualizar documento de la nota
        self.doc.update(estilo, titulo, texto, html)

        self.llegenda.projecteModificat.emit('annotationsChanged')
        self.hide()

    def cancel(self):
        self.hide()

    def delete(self):
        self.llegenda.anotacions.deleteItem(self.item)
        self.hide()

class QvMapToolAnnotation(qgGui.QgsMapTool):
    def __init__(self, llegenda) -> None:
        """Map Tool de gestión de anotaciones (visualización, alta, baja, modificación)

        Args:
            llegenda (QvLlegenda).

        Raises:
            TypeError: Si no hay leyenda o no hay canvas.
        """
        if llegenda is None:
            raise TypeError('llegenda is None (QvMapToolAnnotation.__init__)')
        if llegenda.canvas is None:
            raise TypeError('canvas is None (QvMapToolAnnotation.__init__)')
        qgGui.QgsMapTool.__init__(self, llegenda.canvas)
        self.llegenda = llegenda
        self.llegenda.project.annotationManager().annotationAdded.connect(self.annotationCreated)
        self.currentMoveAction = None
        self.lastMousePosition = None
        self.editor = None
        self.lastItem = None
        self.activated.connect(self.activa)
        self.deactivated.connect(self.desactiva)
        self.canvas().scene().selectionChanged.connect(self.hideItemEditor)

    # Señales de activación

    def activa(self):
        self.noAction()
        self.toggleAnnotations(True)

    def desactiva(self):
        self.hideItemEditor()
        self.canvas().scene().clearSelection()

    # Manejo de anotaciones de proyecto y de canvas

    def annotationCreated(self, annotation: qgCor.QgsAnnotation) -> None:
        # Necesario para que las anotaciones del proyecto pasen al canvas y se visualicen
        self.lastItem = qgGui.QgsMapCanvasAnnotationItem(annotation, self.canvas())
        self.lastItem.setToolTip(QvAnnotation.toolTipText(self.lastItem))

    def removeAnnotations(self) -> None:
        # Borrado de anotaciones al cambiar de proyecto. Si no se hace así
        # justo antes del read() de proyecto, el programa aborta
        for item in self.canvas().annotationItems():
            item.annotation().setVisible(False)
        self.llegenda.project.annotationManager().clear()
        for item in self.canvas().annotationItems():
            self.canvas().scene().removeItem(item)

    # Acciones y cursores

    def noAction(self) -> None:
        self.currentMoveAction = qgGui.QgsMapCanvasAnnotationItem.NoAction
        self.canvas().setCursor(qtGui.QCursor(qtCor.Qt.ArrowCursor))

    def moveAction(self, item: qgGui.QgsMapCanvasAnnotationItem,
                   pos: qtCor.QPoint) -> qgGui.QgsMapCanvasAnnotationItem.MouseMoveAction:
        action = item.moveActionForPosition(pos)
        self.canvas().setCursor(qtGui.QCursor(item.cursorShapeForAction(action)))
        return action

    # Selección y visibilidad

    def menuVisible(self, act: qtWdg.QAction) -> bool:
        num = len(self.canvas().annotationItems())
        if num > 0:
            act.setText(f"Veure anotacions [{num}]")
            act.setChecked(self.canvas().annotationsVisible())
            act.setEnabled(not self.isActive())
            return True
        return False

    def toggleAnnotations(self, visible: bool = None) -> bool:
        toggle = self.canvas().annotationsVisible()
        if visible is not None and visible == toggle:
            return
        toggle = not toggle
        self.canvas().setAnnotationsVisible(toggle)
        for item in self.canvas().annotationItems():
            if not self.canvas().annotationsVisible():
                visible = False
            elif not item.annotation().mapLayer():
                visible = True
            else:
                visible = item.annotation().mapLayer() in self.canvas().mapSettings().layers()
            item.setVisible(visible)
        self.llegenda.projecteModificat.emit('annotationsChanged')
        return toggle

    def selectedItem(self) -> qgGui.QgsMapCanvasAnnotationItem:
        for item in self.canvas().annotationItems():
            if item.isSelected():
                return item
        return None

    def selectItemAtPos(self, pos: qtCor.QPoint) -> qgGui.QgsMapCanvasAnnotationItem:
        self.canvas().scene().clearSelection()
        for item in self.canvas().annotationItems():
            if item.isVisible() and item.sceneBoundingRect().contains(pos):
                item.setSelected(True)
                return item
        return None

    # Formulario de edición

    def showItemEditor(self, item: qgGui.QgsMapCanvasAnnotationItem) -> None:
        if item and item.isVisible() and item.annotation() and \
           isinstance(item.annotation(), qgCor.QgsTextAnnotation):
            self.editor = QvAnnotationDialog(self.llegenda, item)
            self.editor.show()
        else:
            self.hideItemEditor()

    def hideItemEditor(self) -> None:
        if self.editor:
            self.editor.hide()
            self.editor = None

    # Transformación coordenadas

    def transformCanvasToAnnotation(self, p: qgCor.QgsPointXY,
                                    annotation: qgCor.QgsAnnotation) -> qgCor.QgsPointXY:
        if annotation.mapPositionCrs() != self.canvas().mapSettings().destinationCrs():
            transform = qgCor.QgsCoordinateTransform(self.canvas().mapSettings().destinationCrs(),
                                                     annotation.mapPositionCrs(),
                                                     self.llegenda.project)
            try:
                p = transform.transform(p)
            except Exception as e:
                # ignore
                print(str(e))
        return p

    # Alta, modificación, borrado

    def createItem(self, pos: qtCor.QPoint,
                   size: qtCor.QSizeF = qtCor.QSizeF(50, 25),
                   textWidth: float = 100.0) -> qgGui.QgsMapCanvasAnnotationItem:
        annotation = qgCor.QgsTextAnnotation.create()
        if annotation:
            mapPos = self.transformCanvasToAnnotation(self.toMapCoordinates(pos), annotation)
            annotation.setMapPosition(mapPos)
            annotation.setHasFixedMapPosition(True)
            annotation.setMapPositionCrs(self.canvas().mapSettings().destinationCrs())
            annotation.setRelativePosition(qtCor.QPointF(pos.x() / self.canvas().width(),
                                                         pos.y() / self.canvas().height()))
            annotation.setFrameSizeMm(size)
            annotation.document().setTextWidth(textWidth)
            # Dar de alta en project (y en canvas por señal)
            self.lastItem = None
            self.llegenda.project.annotationManager().addAnnotation(annotation)
            item = self.lastItem
            if item is not None:
                self.canvas().scene().clearSelection()
                item.setSelected(True)
                self.llegenda.projecteModificat.emit('annotationsChanged')
            return item
        return None

    def deleteItem(self, item: qgGui.QgsMapCanvasAnnotationItem) -> None:
        if item is None:
            return
        self.llegenda.project.annotationManager().removeAnnotation(item.annotation())
        self.canvas().scene().removeItem(item)
        item.deleteLater()
        self.llegenda.projecteModificat.emit('annotationsChanged')
        self.noAction()

    def updateItem(self, item: qgGui.QgsMapCanvasAnnotationItem) -> None:
        if item is None:
            return
        item.update()
        self.llegenda.projecteModificat.emit('annotationsChanged')

    # Cambio posición o tamaño

    def moveMapPosition(self, item: qgGui.QgsMapCanvasAnnotationItem,
                        e: qgGui.QgsMapMouseEvent) -> None:
        annotation = item.annotation()
        mapPos = self.transformCanvasToAnnotation(e.snapPoint(), annotation)
        annotation.setMapPosition(mapPos)
        annotation.setRelativePosition(qtCor.QPointF(e.pos().x() / self.canvas().width(),
                                                     e.pos().y() / self.canvas().height()))

    def moveFramePosition(self, item: qgGui.QgsMapCanvasAnnotationItem,
                          e: qgGui.QgsMapMouseEvent) -> None:
        annotation = item.annotation()
        newCanvasPos = item.pos() + (e.pos() - self.lastMousePosition)
        if annotation.hasFixedMapPosition():
            pixelToMmScale = 25.4 / self.canvas().logicalDpiX()
            deltaX = pixelToMmScale * (e.pos().x() - self.lastMousePosition.x())
            deltaY = pixelToMmScale * (e.pos().y() - self.lastMousePosition.y())
            annotation.setFrameOffsetFromReferencePointMm(qtCor.QPointF(
                annotation.frameOffsetFromReferencePointMm().x() + deltaX,
                annotation.frameOffsetFromReferencePointMm().y() + deltaY))
            annotation.setRelativePosition(qtCor.QPointF(newCanvasPos.x() / self.canvas().width(),
                                                         newCanvasPos.y() / self.canvas().height()))
        else:
            mapPos = self.transformCanvasToAnnotation(
                self.toMapCoordinates(newCanvasPos.toPoint()),
                annotation)
            annotation.setMapPosition(mapPos)
            annotation.setRelativePosition(qtCor.QPointF(newCanvasPos.x() / self.canvas().width(),
                                                         newCanvasPos.y() / self.canvas().height()))

    def resizeFrame(self, item: qgGui.QgsMapCanvasAnnotationItem,
                    e: qgGui.QgsMapMouseEvent) -> None:
        annotation = item.annotation()
        pixelToMmScale = 25.4 / self.canvas().logicalDpiX()
        size = annotation.frameSizeMm()
        xmin = annotation.frameOffsetFromReferencePointMm().x()
        ymin = annotation.frameOffsetFromReferencePointMm().y()
        xmax = xmin + size.width()
        ymax = ymin + size.height()
        relPosX = annotation.relativePosition().x()
        relPosY = annotation.relativePosition().y()

        if self.currentMoveAction in (qgGui.QgsMapCanvasAnnotationItem.ResizeFrameRight,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameRightDown,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameRightUp):
            xmax = xmax + pixelToMmScale * (e.pos().x() - self.lastMousePosition.x())

        if self.currentMoveAction in (qgGui.QgsMapCanvasAnnotationItem.ResizeFrameLeft,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameLeftDown,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameLeftUp):
            xmin = xmin + pixelToMmScale * (e.pos().x() - self.lastMousePosition.x())
            relPosX = (relPosX * self.canvas().width() + e.pos().x() -
                       self.lastMousePosition.x()) / self.canvas().width()

        if self.currentMoveAction in (qgGui.QgsMapCanvasAnnotationItem.ResizeFrameUp,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameLeftUp,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameRightUp):
            ymin = ymin + pixelToMmScale * (e.pos().y() - self.lastMousePosition.y())
            relPosY = (relPosY * self.canvas().height() + e.pos().y() -
                       self.lastMousePosition.y()) / self.canvas().height()

        if self.currentMoveAction in (qgGui.QgsMapCanvasAnnotationItem.ResizeFrameDown,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameLeftDown,
                                      qgGui.QgsMapCanvasAnnotationItem.ResizeFrameRightDown):
            ymax = ymax + pixelToMmScale * (e.pos().y() - self.lastMousePosition.y())

        # switch min / max if necessary
        if xmax < xmin:
            xmin, xmax = xmax, xmin
        if ymax < ymin:
            ymin, ymax = ymax, ymin

        annotation.setFrameOffsetFromReferencePointMm(qtCor.QPointF(xmin, ymin))
        annotation.setFrameSizeMm(qtCor.QSizeF(xmax - xmin, ymax - ymin))
        annotation.setRelativePosition(qtCor.QPointF(relPosX, relPosY))

    # ******************** E V E N T O S ********************

    def canvasReleaseEvent(self, e: qgGui.QgsMapMouseEvent) -> None:
        self.noAction()

    def canvasPressEvent(self, e: qgGui.QgsMapMouseEvent) -> None:
        if e.button() != qtCor.Qt.LeftButton:
            return
        self.lastMousePosition = e.pos()
        item = self.selectedItem()
        if item:
            self.currentMoveAction = self.moveAction(item, e.pos())
            if self.currentMoveAction != qgGui.QgsMapCanvasAnnotationItem.NoAction:
                return
        if not self.selectItemAtPos(e.pos()):
            item = self.createItem(e.pos())
            self.showItemEditor(item)

    def canvasDoubleClickEvent(self, e: qgGui.QgsMapMouseEvent) -> None:
        item = self.selectedItem()
        if item:
            self.showItemEditor(item)

    def keyPressEvent(self, e: qtGui.QKeyEvent) -> None:
        item = self.selectedItem()
        if not item:
            return
        # Borrar elemento
        if e.key() in (qtCor.Qt.Key_Backspace, qtCor.Qt.Key_Delete):
            self.deleteItem(item)
        # Limpiar selección
        elif e.key() == qtCor.Qt.Key_Escape:
            item.setSelected(False)
        # Editar
        elif e.key() in (qtCor.Qt.Key_Return, qtCor.Qt.Key_Enter):
            self.showItemEditor(item)

    def canvasMoveEvent(self, e: qgGui.QgsMapMouseEvent) -> None:
        item = self.selectedItem()
        if not item or not item.annotation():
            return
        self.moveAction(item, e.pos())
        if self.currentMoveAction != qgGui.QgsMapCanvasAnnotationItem.NoAction:
            if self.currentMoveAction == qgGui.QgsMapCanvasAnnotationItem.MoveMapPosition:
                self.moveMapPosition(item, e)
            elif self.currentMoveAction == qgGui.QgsMapCanvasAnnotationItem.MoveFramePosition:
                self.moveFramePosition(item, e)
            else:
                self.resizeFrame(item, e)
            self.updateItem(item)
        self.lastMousePosition = e.pos()


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    # from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda
    import configuracioQvista as cfg

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = qgGui.QgsMapCanvas()
        # canvas = QvCanvas()

        inicial = cfg.projecteInicial
        # inicial = 'd:/temp/test.qgs'

        leyenda = QvLlegenda(canvas)
        leyenda.readProject(inicial)

        canvas.setWindowTitle('Canvas - ' + inicial)
        canvas.show()

        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

        # Acciones de usuario para el menú

        def setAnnotations():
            if leyenda.anotacions.isActive():
                canvas.unsetMapTool(leyenda.anotacions)
                leyenda.accions.accio('setAnnotations').setChecked(False)
            else:
                canvas.setMapTool(leyenda.anotacions)
                leyenda.accions.accio('setAnnotations').setChecked(True)

        def writeProject():
            print('write file')
            leyenda.project.write()

        def openProject():
            dialegObertura = qtWdg.QFileDialog()
            dialegObertura.setDirectoryUrl(qtCor.QUrl('D:/Temp/'))
            mapes = "Tots els mapes acceptats (*.qgs *.qgz);; " \
                    "Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz)"
            nfile, _ = dialegObertura.getOpenFileName(None, "Obrir mapa Qgis",
                                                      "D:/Temp/", mapes)
            if nfile != '':

                print('read file ' + nfile)
                ok = leyenda.readProject(nfile)
                if ok:
                    canvas.setWindowTitle('Canvas - ' + nfile)
                else:
                    print(leyenda.project.error().summary())

        act = qtWdg.QAction()
        act.setCheckable(True)
        act.setChecked(False)
        act.setText("Dibuixa anotacions")
        act.triggered.connect(setAnnotations)
        leyenda.accions.afegirAccio('setAnnotations', act)

        act = qtWdg.QAction()
        act.setText("Desa projecte")
        act.triggered.connect(writeProject)
        leyenda.accions.afegirAccio('writeProject', act)

        act = qtWdg.QAction()
        act.setText("Obre projecte")
        act.triggered.connect(openProject)
        leyenda.accions.afegirAccio('openProject', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'none':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('setAnnotations')
                leyenda.menuAccions.append('writeProject')
                leyenda.menuAccions.append('openProject')

        # Conexión de la señal con la función menuContexte para personalizar el menú
        leyenda.clicatMenuContexte.connect(menuContexte)
