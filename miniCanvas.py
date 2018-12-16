from moduls.QvImports import *
from qgis.core.contextmanagers import qgisapp

def main(argv):
    with qgisapp() as app: 
        print (argv)
        canvas = QgsMapCanvas()
                # Instancia del projecte i associació canvas-projecte
        project = QgsProject.instance()
        root = QgsProject.instance().layerTreeRoot()

        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        project.read(argv[1])
        canvas.show()

if __name__ == "__main__":
    main(sys.argv)