from qgis.core import QgsPointXY, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject
import json, requests
"""
Mòdul basat en Nominatim, un servei lliure que té una API que utilitza les dades d'OpenStreetMap per a cercar llocs al mapa. 
També permet fer una cerca inversa (a partir d'un punt obtenir l'adreça postal). 

Documentació: https://nominatim.org/
"""
class QvReverse():
    nomCarrer = ""
    numCarrer = ""
    mappoint = QgsPointXY(-1,-1)
    coordSystem = "EPSG:25831" #default coord system is ETRS89

    def __init__(self,qgspoint):
        self.nomCarrer = "Punt seleccionat al mapa"
        self.numCarrer = ""
        self.mappoint = qgspoint
        
        self._transformETRS89toLatLon()
        self._request()


    #petició web i obtenció del resultat
    def _request(self):
        #fer GET a la API. 
        def _makeRequest(url):
            try:
                var = requests.get(url).text
            except requests.exceptions.ConnectionError as err:
                var = "-1"
            return var

        url = "https://nominatim.openstreetmap.org/reverse?"
        url += "lat=" + str(self.mappoint.y())
        url += "&lon=" + str(self.mappoint.x())
        url += "&format=json"

        response = _makeRequest(url)
        if (response == "-1"):
            #TODO: mostrar missatge d'error
            return

        #decodificar response (és un JSON)
        response = json.loads(response)

        if "address" in response:
            if "road" in response["address"]:
                self.nomCarrer = response["address"]["road"]
            if "house_number" in response["address"]:
                self.numCarrer = response["address"]["house_number"]
                

    #conversió de sistema de coordenades EPSG:25831 a EPSG:4326
    def _transformETRS89toLatLon(self):
        #TODO: caldria adaptar el codi a altres sistemes de geoposició
        if self.coordSystem == "EPSG:25831":
            pointTransformation = QgsCoordinateTransform(
                    QgsCoordinateReferenceSystem(self.coordSystem), 
                    QgsCoordinateReferenceSystem("EPSG:4326"), 
                    QgsProject.instance())
            self.mappoint = pointTransformation.transform(self.mappoint)
            print(self.mappoint)

if __name__ == "__main__":
        project = QgsProject.instance()

        point = QgsPointXY(432655.37,4584569.85)
        test = QvReverse(point)
