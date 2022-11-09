from qgis.core import QgsProject
from qgis.gui import QgsLayerTreeMapCanvasBridge
from qgis.PyQt.QtWidgets import QDockWidget

from moduls.QvCanvas import QvCanvas
from moduls.QvCanvasAuxiliar import QvCanvasAuxiliar


# Classe no utilitzada. Es conserva com a exemple de com fer una eina sense utilitzar el creador
class DobleCanvas(QDockWidget):
    esEinaGlobal = False
    titol = 'Segon canvas'
    def __init__(self,parent=None):
        super().__init__('Segona vista del projecte',parent)
        canvas = QvCanvasAuxiliar(parent.canvas,botoneraHoritzontal=True,posicioBotonera='SO')
        root = QgsProject.instance().layerTreeRoot()

        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        self.setWidget(canvas)

        if 'DobleCanvasTema' in QgsProject.instance().mapThemeCollection().mapThemes():
            canvas.setTheme('DobleCanvasTema')