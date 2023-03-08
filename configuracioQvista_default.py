from pathlib import Path, PurePath
import os


class ConfigBase:
    VERSIO = "1.00"
    TITOLFINESTRA = "qVista {}  Sistema d'Informació Territorial de Barcelona"
    CATALEGSCAPES = {
        'públic': "N:/9SITEB/Publicacions/qVista/Cataleg/Catàleg de capes corporatives/",
        'privat': 'L:/DADES/SIT/qVista/CATALEG/Catàleg de capes privades/',
        'local': '../dades/Catàleg de capes local'
    }
    CATALEGMAPES = {
        'públic': "N:/9SITEB/Publicacions/qVista/Cataleg/Mapes publics/",
        'privat': 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/'
    }

    PROJECTEINICIAL = 'mapesOffline/qVista default map.qgs'

    ESTATSCONNEXIO = ["Xarxa municipal: Desconnectat", "Xarxa municipal: Connectat"]

    PATHPLANTILLES = "plantillesMapes/"

    # el temp de l'usuari/sistema operatiu
    # una opció habitual seria tempfile.gettempdir()
    TMP = 'C:/temp'
    # el nom de la carpeta que penjarà de TMP
    QVTEMPDIR = 'qVista'
    # directoris que penjaran de QVTEMPDIR
    TEMPDIR = 'temp'
    DADESDIR = 'dades'
    CONFIGDIR = 'config'

    # directori on tenim documentacions i dades compartides entre usuaris
    DOCDIR = 'n:/siteb/apl/pyqgis/qvista/dades/'
    # coses que pengen de DOCDIR
    DOCDIRPLANTILLES = 'plantilles'
    NOMARXIUAVISOS = 'Avisos.htm'
    NOMARXIUNOTICIES = 'Noticies.htm'
    NOMCARPETADOCUMENTS = 'Documentacio'
    ARXIUINFOQVISTA = 'InfoQVista.pdf'

    def GETTITOLFINESTRA(self):
        return self.TITOLFINESTRA.format(self.VERSIO)

    def CHECKXARXAMUNICIPAL(self):
        return Path(self.CATALEGSCAPES['públic']).is_dir()

    def __init__(self):
        # if hasattr(self, 'versio'):
        #     # Ja l'hem instanciat una vegada. Ens assegurem de que estigui actualitzat i ja
        #     self.update()
        #     return
        self.versio = self.VERSIO
        self.titolFinestra = self.GETTITOLFINESTRA()

        self.carpetaCataleg = self.path(self.CATALEGSCAPES['públic'])
        self.carpetaCatalegPrivat = self.path(self.CATALEGSCAPES['privat'])
        self.carpetaCatalegLocal = self.path(self.CATALEGSCAPES['local'])
        self.carpetaCatalegLlista = [self.carpetaCataleg, self.carpetaCatalegPrivat, self.carpetaCatalegLocal]
        # Definim per separat els directoris de projectes públics i privats, de manera que puguem comprovar en qualsevol moment si un directori és de projectes públics o privats
        self.carpetaCatalegProjectesPublics = self.path(self.CATALEGMAPES['públic'])
        self.carpetaCatalegProjectesPrivats = self.path(self.CATALEGMAPES['privat'])
        self.carpetaCatalegProjectesLlista = [self.carpetaCatalegProjectesPublics, self.carpetaCatalegProjectesPrivats]

        self.projecteInicial = self.path(self.PROJECTEINICIAL)

        # Hi ha codi del qVista que assumeix que acaba amb '/'. Per si de cas, ho forcem
        self.pathPlantilles = self.path(self.PATHPLANTILLES)+'/'

        # serà modificat al update
        self.estatConnexio = self.ESTATSCONNEXIO[self.CHECKXARXAMUNICIPAL()]

        self.tmp = self.path(self.TMP)
        self.QvTempdir = self.path(self.tmp, self.QVTEMPDIR)
        self.tempdir = self.path(self.QvTempdir, self.TEMPDIR)  # Seran els arxius temporals de qVista que no s'han de guardar entre execucions
        self.dadesdir = self.path(self.QvTempdir, self.DADESDIR)  # Arxius temporals que volem conservar
        self.configdir = self.path(self.QvTempdir, self.CONFIGDIR)  # Configuracions i coses

        self.docdir = self.path(self.DOCDIR)
        self.imatgesDir = self.path('Imatges/')
        self.docdirPlantilles = self.path(self.docdir, self.DOCDIRPLANTILLES)

        self.arxiuAvis = self.path(self.docdir, self.NOMARXIUAVISOS)
        self.arxiuNews = self.path(self.docdir, self.NOMARXIUNOTICIES)
        self.carpetaDocuments = self.path(self.docdir, self.NOMCARPETADOCUMENTS)
        self.carpetaDocumentsLocal = self.path('documentacio/')
        self.arxiuInfoQVista = self.path(self.docdir, self.ARXIUINFOQVISTA)

        self.widthLlegenda = 250

        self.garanteixDirs()

    def garanteixDirs(self):
        for x in (self.tmp, self.QvTempdir, self.tempdir, self.dadesdir, self.configdir, self.carpetaCatalegLocal):
            Path(x).mkdir(parents=True, exist_ok=True)

    def path(self, *args):
        # https://discuss.python.org/t/pathlib-absolute-vs-resolve/2573/17
        # Path.resolve falla amb les unitats de xarxa, ja que converteix el path a un path UNC
        #  (estil "//servidor/...")
        #  Això provoca errors en mòduls no pensats per funcionar així
        # Path.absolute crea una ruta absoluta, però no elimina "." i ".."
        #  Path('../dades').absolute() # D:/qVista/Codi/../dades
        # os.path.abspath fa el que volem (resol '..' i '.', però no fa coses estranyes amb discs)
        # return str(Path(*args).absolute())
        # L'únic problema que té os.path.abspath és que utilitza "\". Per tant, fem un replace
        return os.path.abspath(PurePath(*args)).replace('\\','/')
