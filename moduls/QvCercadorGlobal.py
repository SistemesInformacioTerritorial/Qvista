from qgis.PyQt.QtCore import QObject
from qgis.core import QgsPointXY
from moduls.QvImports import *
from urllib.request import urlopen
from abc import abstractmethod, ABCMeta, ABC
from enum import Enum
import json
import sys


class QCercadorGlobal(ABC):
    '''
Classe base per tots els cercadors.
Rep tres lineedits (via, número i ciutat) i un botó. Habilita el botó quan els tres tenen contingut, i quan aquest és clicat fa la cerca
Per consultar un nou cercador cal implementar la funció geocodificaGlobal, que ha de retornar adreces en ETRS89 31N.
Es pot fer servir la funció transforma, que converteix dades de la projecció self.projIn a la projecció 'EPSG:25831'
Si la font de dades ens les dóna en un altre sistema de referència, simplement redeclarem aquest atribut
    '''
    projIn = 'EPSG:4326'

    def __init__(self, leCarrer: QLineEdit, leNumero: QLineEdit, leCiutat: QLineEdit, boto: QPushButton, project: QgsProject):
        super().__init__()
        self._leCarrer = leCarrer
        self._leNumero = leNumero
        self._leCiutat = leCiutat
        self._boto = boto
        self._boto.setEnabled(False)

        self._canvas = canvas
        self._project = project

        self._leCarrer.textChanged.connect(self.carrerEditat)
        self._leNumero.textChanged.connect(self.numeroEditat)
        self._leCiutat.textChanged.connect(self.actualitzaBoto)

    def carrerEditat(self):
        self._leNumero.clear()
        self.actualitzaBoto()

    def numeroEditat(self):
        self._leCiutat.clear()
        self.actualitzaBoto()

    def actualitzaBoto(self):
        self._boto.setEnabled(self._leCarrer.text(
        ) != '' and self._leNumero.text() != '' and self._leCiutat.text() != '')

    # Ha de retornar una llista amb els resultats que trobi, o None si hi ha algun error
    # El format de la llista ha de ser el següent: [((x0, y0),adr0),((x1,y1),adr1),...]
    @abstractmethod
    def geocodificaGlobal(self, carrer, numero, ciutat):
        pass

    def transforma(self, long, lat):
        transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(
            self.projIn), QgsCoordinateReferenceSystem("EPSG:25831"), self._project)
        return transform.transform(QgsPointXY(long, lat))

    def cerca(self):
        try:
            return self.geocodificaGlobal(self._leCarrer.text(), self._leNumero.text(), self._leCiutat.text())
        except:
            # La geocodificació ha fallat.
            return []


class QCercadorGlobalCartociudad(QCercadorGlobal):
    def geocodificaGlobal(self, carrer, numero, ciutat):
        try:
            url = 'http://www.cartociudad.es/CartoGeocoder/GeocodeAddress?province=Barcelona&municipality=%s&road_name=%s&road_number=%s&max_results=20' % (
                ciutat, carrer, numero)
            res = json.loads(urlopen(url).read().decode('ISO 8859-1'))
            return [(self.transforma(x['longitude'], x['latitude']), '%s %s %s' % (x['road_type'], x['road_name'], x['numpk_name'])) for x in res['result']]
        except Exception as e:
            print(e)
            return None


class QCercadorGlobalGeopy(QCercadorGlobal, ABC):
    '''
Classe base per tots els geocodificadors fets a partir de geopy
Per fer una subclasse només cal declarar l'atribut de classe geocodificador, com per exemple:
class ElMeuGeocod(QCercadorGlobalGeopy):
    geocodificador = ...
    '''
    @property
    @abstractmethod
    def geocodificador(self):
        # Si intenta accedir al geocodificador, falla. El geocodificador no ha de ser un mètode sino un atribut, però python ens porta problemes amb això :(
        raise NotImplementedError

    def geocodificaGlobal(self, carrer, numero, ciutat):
        res = self.geocodificador.geocode(
            carrer+' '+numero+' '+ciutat, exactly_one=False)
        if not isinstance(res, list):
            res = [res]
        return [(self.transforma(x.longitude, x.latitude), x.address) for x in res]


class QCercadorGlobalArcGIS(QCercadorGlobalGeopy):
    if 'geopy' in sys.modules:
        from geopy.geocoders import ArcGIS
        geocodificador = ArcGIS()


class QCercadorGlobalNominatim(QCercadorGlobalGeopy):
    if 'geopy' in sys.modules:
        from geopy.geocoders import Nominatim
        geocodificador = Nominatim(user_agent='qVista')


class QvCercadorGlobal(QWidget):
    geocodificadors = Enum('Geocodificador', 'ArcGIS Cartociudad Nominatim')

    def __init__(self, canvas, project, geocod=geocodificadors.Cartociudad, parent=None):
        super().__init__(parent)
        self._canvas = canvas
        self._project = project
        lay = QVBoxLayout()
        self.setLayout(lay)
        le1 = QLineEdit()
        le1.setPlaceholderText('Carrer')
        le2 = QLineEdit()
        le2.setPlaceholderText('Número')
        le3 = QLineEdit()
        le3.setPlaceholderText('Ciutat')
        boto = QPushButton('Cercar')

        layCerc = QHBoxLayout()
        layCerc.addWidget(le1)
        layCerc.addWidget(le2)
        layCerc.addWidget(le3)
        layCerc.addWidget(boto)
        lay.addLayout(layCerc)

        if geocod == self.geocodificadors.Cartociudad:
            self._cercador = QCercadorGlobalCartociudad(
                le1, le2, le3, boto, self._project)
            info = 'Aquest cercador fa servir la base de dades de Cartociudad, un servei del Ministeri de Foment del Govern d\'Espanya.'\
                "L'abast en el qual podeu cercar és la província de Barcelona"
        elif geocod == self.geocodificadors.ArcGIS:
            self._cercador = QCercadorGlobalArcGIS(
                le1, le2, le3, boto, self._project)
            info = "Aquest cercador fa servir la base de dades d'ArcGIS, una plataforma de mapes online."\
                "L'abast en el qual podeu cercar és tot el món."\
                "Degut a això, la cerca a vegades pot no ser massa precisa. Intenteu introduir, juntament amb la ciutat, més informació com la província, el codi postal i similars."
        elif geocod == self.geocodificadors.Nominatim:
            self._cercador = QCercadorGlobalNominatim(
                le1, le2, le3, boto, self._project)
            info = ""
        else:
            raise NotImplementedError('No existeix el geocodificador indicat')

        self._tree = QTreeView()
        lay.addWidget(self._tree)
        self._tree.hide()
        self._model = QStandardItemModel()
        self._tree.setModel(self._model)
        self._tree.selectionModel().selectionChanged.connect(self.resultatTriat)
        self._tree.setHeaderHidden(True)
        for i in range(self._model.columnCount()):
            if i == 0:
                self._tree.setColumnHidden(i, False)
                self._tree.resizeColumnToContents(i)
                self._tree.resizeColumnToContents(i)
            else:
                self._tree.setColumnHidden(i, True)
        self._tree.setEditTriggers(QTreeView.NoEditTriggers)

        self._lblResultat = QLabel()
        lay.addWidget(self._lblResultat)

        # info=QTextEdit()
        # info.setText('''Aquest widget funciona a través de dades mundials, a través del servei ArcGIS. Intenteu introduir l'adreça amb el màxim de precisió, incloent ciutat i fins i tot país si cal, per garantir que el resultat sigui correcte.''')
        # info.setReadOnly(True)
        # lay.addWidget(info)

        boto.clicked.connect(self.cerca)
        le3.returnPressed.connect(self.cerca)
        self._marcaLloc = QgsVertexMarker(self._canvas)

    def cerca(self):
        self._resultat = self._cercador.cerca()

        if self._resultat is None:
            self._resultat = []
            QMessageBox.warning(self, 'El servei extern de cerca ha fallat',
                                'El servei extern de cerca ha fallat. Reviseu la connexió a Internet i torneu a intentar-ho més tard')

        if len(self._resultat) == 1:
            self._tree.hide()
            self.resultatTriat()
        elif len(self._resultat) == 0:
            self._lblResultat.setText('Adreça no trobada')
        else:
            self._model.setRowCount(len(self._resultat))
            for i, x in enumerate(self._resultat):
                self._model.setItem(i, QStandardItem(x[1]))
            self._tree.show()
            pass

    def resultatTriat(self):
        act = self._tree.currentIndex().row() if self._tree.isVisible() else 0
        res, adreca = self._resultat[act]
        self._marcaLloc.setCenter(res)
        self._marcaLloc.setColor(QColor(255, 0, 0))
        self._marcaLloc.setIconSize(15)
        self._marcaLloc.setIconType(QgsVertexMarker.ICON_BOX)
        self._marcaLloc.setPenWidth(3)
        self._marcaLloc.show()

        self._lblResultat.setText(adreca)
        # self._tree.hide()


if __name__ == '__main__':
    projecteInicial = 'mapesOffline/qVista default map.qgs'
    from moduls.QvCanvas import QvCanvas

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))

        # canvas = QgsMapCanvas()
        canvas = QvCanvas(llistaBotons=['panning', 'zoomIn', 'zoomOut'])
        canvas.setGeometry(10, 10, 1000, 1000)
        canvas.setCanvasColor(QColor(10, 10, 10))
        project = QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        cercador = QvCercadorGlobal(canvas, project, QvCercadorGlobal.geocodificadors.Cartociudad)

        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(cercador)
        lay.addWidget(canvas)
        wid = QWidget()
        wid.setLayout(lay)

        wid.show()
