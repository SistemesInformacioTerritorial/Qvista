from moduls.QvImports import *
from moduls.QvCanvas import QvCanvas

class DobleCanvas(QDockWidget):
    esEina = True
    titol = 'Segon canvas'
    def __init__(self,parent=None):
        super().__init__('Segona vista del projecte',parent)
        canvas = QvCanvasAuxiliar(parent.canvas,botoneraHoritzontal=True,posicioBotonera='SO')
        root = QgsProject.instance().layerTreeRoot()

        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        self.setWidget(canvas)

        if 'DobleCanvasTema' in QgsProject.instance().mapThemeCollection().mapThemes():
            canvas.setTheme('DobleCanvasTema')