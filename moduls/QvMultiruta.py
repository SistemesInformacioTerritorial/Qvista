"""
Mòdul multiruta basat en Project-OSRM, el motor de rutes que fa servir l'OpenStreetMap.
Aquest mòdul permet calcular la ruta més curta a partir d'un seguit de punts, establint
un punt d'inici, un punt final i n punts intemitjos (si 0<=n<=10 es fa servir l'algorisme
"farthest-insertion", si n>10 es fa servir força bruta i el resultat podria no ser òptim).
Evidentment els punts intermitjos no han d'estar ordenats, és el propi WebService qui els
endreça de manera òptima.

Opcions de ruta:
- roundtrip: true indica si és una ruta circular
- source: true indica si el primer element del llistat de punts és el punt d'inici
- destination: true indica si l'últim element del llistat de punts és el punt de finalització

Exemple de codi:
TODO: escriure exemple

punts = [QgsPointXY(_,_),QgsPointXY(_,_),QgsPointXY(_,_)...]
multiruta = QvMultiruta(punts)
multiruta.setRouteOptions(True,True,True)
multiruta.getRoute()

URL d'exemple WebService:
http://router.project-osrm.org/trip/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219?geometries=geojson
- Format JSON
- El paràmetre geometires=json ens retorna una polilínia com un conjunt de punts

Documentació: http://project-osrm.org/
"""
from qgis.core import QgsPoint, QgsPointXY, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject, QgsGeometry
from qgis.gui import QgsMapCanvas, QgsRubberBand
from qgis.PyQt.QtGui import QColor
import requests, json

class QvMultiruta():
    points = [] #QgsPointXY array

    #configuracio sistema coordenades
    coordSystem = "EPSG:25831" #ETRS89. TODO: agafar de variable global de qVista

    #configuracio ruta
    routeType = True #True si tipus trip, False si tipus Route
    transportationMode = "vehicle"
    roundtrip = True
    source = False
    destination = False

    #elements de la resposta de l'API
    routeOK = False
    polylines = []
    routePoints = [] #cada element de l'array és un array de punts

    #distance i duration són arrays donat que hi pot haver una ruta partida en dos
    trips_distance = []
    trips_duration = []

    #inicialitzadora: startPoint i endPoint son QgsPointXY, wayPoints un arrray que pot ser nul
    def __init__(self, Points):
        #transformacio de punts a LatLon (EPGS4326)
        self.points = self._transformArrayLatLon(Points)

    def setRouteOptions(self,roundtrip,source,destination):
        """
        Els tres arguments són booleans:
        - roundtrip: indica si és una ruta circular
        - source: indica si el primer element del llistat de punts és el punt d'inici
        - destination: indica si l'últim element del llistat de punts és el punt de finalització

        Incompatibilitats:
        roundtrip   source  destination
        false       true    false
        false       false   true
        false       true    true
        """
        self.roundtrip = roundtrip
        self.source = source
        self.destination = destination

        #TODO: comprovacio incompatibilitats

    def setRouteType(self,routeType):
        """
        Si bool és TRUE, el tipus de ruta és Trip.
        Si bool és FALSE, el tipus de ruta és Route.
        """
        self.routeType = routeType

    def setTransportationMode(self, mode):
        """
        mode pot ser:
        - walk
        - bike
        - vehicle
        """
        self.transportationMode = mode

    def getRoute(self):
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

        url = "https://routing.openstreetmap.de/routed-"

        #mode de transport. pot ser a peu (walk), en bicicleta (bike) o en automòbil (vehicle)
        if (self.transportationMode == "walk"):
            url += "foot/"
        elif (self.transportationMode == "bike"):
            url += "bike/"
        else:
            url += "car/"

        #tipus de ruta. si routeType = True, és tipus trip. sinó és Route
        if (self.routeType):
            url += "trip/v1/driving/"
        else:
            url += "route/v1/driving/"

        

        for index, p in enumerate(self.points):
            url += str(p.x()) + ',' + str(p.y())
            if index < len(self.points)-1:
                url += ';'

        url += "?geometries=geojson&overview=full" #necessari per obtenir ruta detallada i en format geoJSON
        if (self.routeType):
            if (self.roundtrip):
                url += "&roundtrip=true" 
            else:
                url += "&roundtrip=false" 

            if (self.source):
                url += "&source=first" 
            else:
                url += "&source=any" 

            if (self.destination):
                url += "&destination=last" 
            else:
                url += "&destination=any" 

        print(url)

        response = _makeRequest(url)
        if (response == "-1"):
            #TODO: error handling
            return

        #decodificar response (JSON)
        response = json.loads(response)

        self.routePoints = [] #reset de l'array

        #afegir punts ruta a routePoints
        keyname = "trips"
        if not self.routeType:
            keyname = "routes"

        if keyname in response:
            for trip in response[keyname]:
                tripPoints = []
                #obtenir coordenades de la ruta per cada trip. format geojson.
                if "geometry" in trip:
                    if "coordinates" in trip["geometry"]:
                        for c in trip["geometry"]["coordinates"]:
                            p = QgsPointXY(c[0],c[1])
                            tripPoints.append(p)
                    self.routePoints.append(tripPoints)

                #informació de la ruta
                if "distance" in trip:
                    self.trips_distance.append(trip["distance"])
                if "duration" in trip:
                    self.trips_duration.append(trip["duration"])

        #convertir routePoints a ETRS89
        aux_routePoints = []
        for trip in self.routePoints:
            aux_routePoints.append(self._transformArrayfromLatLon(trip))
        self.routePoints = aux_routePoints

        self.routeOK = True

    #creació de polilínies. cal enviar-li el canvas
    def printRoute(self,canvas):
        self.hideRoute() #neteja prèvia
        self.polylines = [] #reset de l'array
        #creació polilínies a partir de routePoints. cada trip és una polilínia
        for trip in self.routePoints:
            QgsPoint_trip = self._convertPointList(trip)
            polyline = QgsRubberBand(canvas, False)
            polyline.setToGeometry(QgsGeometry.fromPolyline(QgsPoint_trip), None)
            polyline.setColor(QColor(0, 0, 255))
            polyline.setWidth(3)
            self.polylines.append(polyline)

    #neteja del canvas
    def hideRoute(self):
        for line in self.polylines:
            line.hide()
            line.reset(True)
        self.polylines.clear()

    #converteix array de QgsPointXY a QgsPoint
    def _convertPointList(self,pointlist):
        retQgsPoint = []
        for point in pointlist:
            retQgsPoint.append(QgsPoint(point))
        return retQgsPoint

    #convertir punts en sistema de coordenades actual a EPSG4326
    def _transformArrayLatLon(self,array):
        transformedArray = []
        for point in array:
            if (point == None):
                return
            pointTransformation = QgsCoordinateTransform(
                    QgsCoordinateReferenceSystem(self.coordSystem), 
                    QgsCoordinateReferenceSystem("EPSG:4326"), 
                    QgsProject.instance())
            transformedArray.append(pointTransformation.transform(point))
        return transformedArray

    #convertir punts en sistema EPSG4326 al sistema del projecte
    def _transformArrayfromLatLon(self,array):
        transformedArray = []
        for point in array:
            pointTransformation = QgsCoordinateTransform(
                    QgsCoordinateReferenceSystem("EPSG:4326"), 
                    QgsCoordinateReferenceSystem(self.coordSystem), 
                    QgsProject.instance())
            transformedArray.append(pointTransformation.transform(point))
        return transformedArray

if __name__ == "__main__":
    punts = [QgsPointXY(432655.37,4584569.85), QgsPointXY(432652.37,4584564.85), QgsPointXY(432651.37,4584560.85), QgsPointXY(432659.37,4584567.85)]
    multiruta = QvMultiruta(punts)
    multiruta.setRouteOptions(True,True,True)
    multiruta.getRoute()
    multiruta.printRoute(QgsMapCanvas())