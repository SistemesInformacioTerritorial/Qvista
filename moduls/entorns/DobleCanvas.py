from moduls.QvImports import *
from moduls.QvCanvas import QvCanvas

class DobleCanvas(QDockWidget):
    def __init__(self,parent=None):
        super().__init__('Segona vista del projecte',parent)
        canvas = QvCanvas(botoneraHoritzontal=True,posicioBotonera='SO')
        root = QgsProject.instance().layerTreeRoot()

        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        
        self.setWidget(canvas)