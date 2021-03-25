#imports
import xml.etree.ElementTree as ET
import requests
from moduls.QvImports import *
from qgis.core import QgsPointXY
from qgis.gui import QgsMapCanvas, QgsRubberBand

class Gir():
    coord = QgsPointXY() #Coordenada()

    def __init__(self,inp_coord):
        """
        Pre: inp_coord és una coordenada inicialitzada
        Post: s'inicialitza la variable coord
        """
        self.coord = inp_coord

class Tram():
    circulable = False #boolean
    coords = []

    def __init__(self,circulable,coords):
        """
        Pre: coords és una array de coordenades
        Post: s'inicialitza la variable coord
        """
        self.circulable = circulable
        self.coords = coords

    def getCoords(self):
        return self.coords

    def getCirculable(self):
        return self.circulable

class Ruta():
    ruta_calculada = False

    coordInici = QgsPointXY()
    coordInici_descripcio = ""
    coordFinal = QgsPointXY()
    coordFinal_descripcio = ""

    descripcioRuta = [] #array d'Strings
    girsRuta = [] #array de Gir
    tramsRuta = [] #array de Tram
    distanciaRuta = 0
    duradaRuta = 0

    coord_Final_descripcio = ""

    def __init__(self, coordA, coordB):
        """ 
        Pre: coordA i coordB són instàncies de la classe QgsPointXY
        Post: s'inicialitzen les variables coordInici i coordFinal
        """
        #comprovacions coordenades?

        self.coordInici = coordA
        self.coordFinal = coordB

    def calculaRuta(self):
        """ 
        Pre: coordInici i coordFi han estat establerts i són a Barcelona.
        Post: es defineixen la resta d'atributs de la classe
        comprovar que missatgeResultat sigui OK
        """
        def readLocalXML(filename):
            with open(filename, 'r') as file:
                data = file.read().replace('\n', '')
            return data

        def readRemoteXML(URL):
            """
                Cal especificar que s'accepta només xml com a resposta. Per defecte torna JSON.
            """
            headers = {
                "Accept": "application/xml",
            }
            var = requests.get(URL,headers=headers).text
            return var 

        def parseXML(content):
            root = ET.fromstring(content)

            ns = {'nsruta': 'http://schemas.datacontract.org/2004/07/RutesSrv.Controllers', 'd2p1': 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'}

            if (int(root.find("nsruta:codiResultat",ns).text) != 0):
                print("XML parse error")

            self.coordInici_descripcio = root.find("nsruta:sortida",ns).find("nsruta:descripcio",ns).text
            self.coordFinal_descripcio = root.find("nsruta:arribada",ns).find("nsruta:descripcio",ns).text

            self.distanciaRuta = int(root.find("nsruta:distancia",ns).text)
            self.duradaRuta = int(root.find("nsruta:durada",ns).text)

            for descripcio in root.find("nsruta:descripcio",ns).findall("d2p1:string",ns):
                self.descripcioRuta.append(descripcio.text)

            for gir in root.find("nsruta:girs",ns).findall("nsruta:Gir",ns):
                temp_coord = QgsPointXY(float(gir.find("nsruta:coord",ns).find("nsruta:x",ns).text), float(gir.find("nsruta:coord",ns).find("nsruta:y",ns).text))
                self.girsRuta.append(temp_coord)

            for tram in root.find("nsruta:trams",ns).findall("nsruta:Tram",ns):
                coords = []
                circulable = False

                str_circulable = tram.find("nsruta:circulable",ns).text

                if (str_circulable == "true"):
                    circulable = True
                
                for tramcoord in tram.find("nsruta:coords",ns).findall("nsruta:Coord",ns):
                    temp_coord = QgsPointXY(float(tramcoord.find("nsruta:x",ns).text), float(tramcoord.find("nsruta:y",ns).text))
                    coords.append(temp_coord)

                self.tramsRuta.append(Tram(circulable,coords))

        URL = "http://netiproa.corppro.imi.bcn:81/karta/api/Ruta/Utm/" + str(self.coordInici.x()) + "/" + str(self.coordInici.y()) + "/" + str(self.coordFinal.x()) + "/" + str(self.coordFinal.y()) + "/EPSG:25831"

        filecontent = readRemoteXML(URL)
        #filecontent = readLocalXML(r"C:/QVista/ruta1.xml")

        parseXML(filecontent)


    def pintarRuta(self,canvas):
        """ Pre: la ruta ja ha estat calculada. project és un QgsMapCanvas
        """

        polylines = []

        for tram in self.tramsRuta:
            points = []
            polyline = QgsRubberBand(canvas, False)
            polylines.append(polyline)
            for point in tram.getCoords():
                points.append(QgsPoint(point))

            polyline.setToGeometry(QgsGeometry.fromPolyline(points), None)
            if (tram.getCirculable() == False):
                polyline.setColor(QColor(255, 0, 0))
            else:
                polyline.setColor(QColor(0, 0, 255))

            polyline.setWidth(3)
            polyline.show()



    #def mostrarLlegenda(window? qwidget?):
        """ Pre: la ruta ha estat calculada
        """


if __name__ == "__main__":
    projecteInicial='mapesOffline/qVista default map.qgs'
    with qgisapp():
        canvas=QgsMapCanvas()
        canvas.setContentsMargins(0,0,0,0)
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)
        bridge.setCanvasLayers()

        # llegim un projecte de demo

        project.read(projecteInicial)
        
        ruta = Ruta(QgsPointXY(434799.933, 4584672.930),QgsPointXY(433463.058, 4583356.121))
        ruta.calculaRuta()
        ruta.pintarRuta(canvas)

        canvas.show()