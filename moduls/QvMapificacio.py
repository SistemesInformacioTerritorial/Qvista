# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition, QgsVectorFileWriter,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange, QgsAggregateCalculator, QgsError,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsReadWriteContext, QgsExpressionContextUtils)
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor, QValidator, QIcon
from qgis.PyQt.QtXml import QDomDocument
from moduls.QvSqlite import QvSqlite


from qgis.PyQt.QtWidgets import (QFileDialog, QWidget, QPushButton, QFormLayout, QVBoxLayout, QHBoxLayout,
                                 QComboBox, QLabel, QLineEdit, QSpinBox, QGroupBox, QGridLayout,
                                 QMessageBox, QDialogButtonBox)

import os
import sys
import csv
import time
import unicodedata

_ZONES = {
    # Nom: (Camp, Arxiu)
    "Districte": ("DISTRICTE", "Districtes.sqlite"),
    "Barri": ("BARRI", "Barris.sqlite")
    # "Codi postal": "CODI_POSTAL",
    # "Illa": "ILLA",
    # "Solar": "SOLAR",
    # "Àrea estadística bàsica": "AEB",
    # "Secció censal": "SECCIO_CENSAL",
    # "Sector policial operatiu": "SPO"
}

_AGREGACIO = {
    "Recompte": "COUNT({})",
    "Recompte diferents": "COUNT(DISTINCT {})",
    "Suma": "SUM({})",
    "Mitjana": "AVG({})"
}

_DISTRIBUCIO = {
    "Total": "",
    "Per m2": "/ Z.AREA"
    # "Per habitant": "/ Z.POBLACIO"
}

_COLORS = {
    "Blau": QColor(0, 128, 255),
    "Gris": QColor(128, 128, 128),
    "Groc" : QColor(255, 192, 0),
    "Taronja": QColor(255, 128, 0),
    "Verd" : QColor(32, 160, 32),
    "Vermell" : QColor(255, 32, 32)
}

_METODES = {
    "Endreçat": QgsGraduatedSymbolRenderer.Pretty,
    "Intervals equivalents": QgsGraduatedSymbolRenderer.EqualInterval,
    "Quantils": QgsGraduatedSymbolRenderer.Quantile,
    "Divisions naturals (Jenks)": QgsGraduatedSymbolRenderer.Jenks,
    "Desviació estàndard": QgsGraduatedSymbolRenderer.StdDev
}

_METODES_MODIF = _METODES.copy()
_METODES_MODIF["Personalitzat"] = QgsGraduatedSymbolRenderer.Custom

_TRANS = str.maketrans('ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöüºª€@$·.,;:()[]¡!¿?|@#%&ç*',
                       'AEIOUaeiouAEIOUaeiouAEIOUaeiouAEIOUaeiouoaEaD____________________')

_RUTA_LOCAL = 'C:/temp/qVista/dades/'
_RUTA_DADES = 'D:/qVista/Codi/Dades/'

class QvMapRender():

    INI_ALPHA = 8

    @staticmethod
    def calcColorsGradient(colorBase):
        colorIni = QColor(colorBase)
        colorIni.setAlpha(QvMapRender().INI_ALPHA)
        colorFi = QColor(colorBase)
        colorFi.setAlpha(255 - QvMapRender().INI_ALPHA)
        return colorIni, colorFi

    @staticmethod
    def calcRender(capa, campCalculat, numDecimals, colorBase,
                   numCategories, modeCategories, format):
        try:
            colorIni, colorFi = QvMapRender().calcColorsGradient(colorBase)
            colorRamp = QgsGradientColorRamp(colorIni, colorFi)
            labelFormat = QgsRendererRangeLabelFormat(format, numDecimals)
            symbol = QgsSymbol.defaultSymbol(capa.geometryType())
            renderer = QgsGraduatedSymbolRenderer.createRenderer(capa, campCalculat,
                numCategories, modeCategories, symbol, colorRamp, labelFormat)
            return renderer
        except Exception as e:
            return None

    @staticmethod
    def nomParam(param, llista):
        for nom, valor in llista.items():
            if param == valor:
                return nom
        return list(llista.keys())[0]

    @staticmethod
    def nomColor(param, llista):
        for nom, valor in llista.items():
            if param.red() == valor.red() and param.green() == valor.green() and param.blue() == valor.blue():
                return nom
        return list(llista.keys())[0]

    @staticmethod
    def paramsRender(capa):
        try:
            renderer = capa.renderer()
            campCalculat = renderer.classAttribute()
            numDecimals = renderer.labelFormat().precision()
            color = renderer.sourceColorRamp().color1()
            color.setAlpha(0)
            colorBase = QvMapRender().nomColor(color, _COLORS)
            numCategories = len(renderer.ranges())
            modeCategories = QvMapRender().nomParam(renderer.mode(), _METODES_MODIF)
            format = renderer.labelFormat().format()
            return campCalculat, numDecimals, colorBase, numCategories, modeCategories, format
        except Exception as e:
            return 'RESULTAT', 0, 'Blau', 4, 'Endreçat', '%1 - %2'

    @staticmethod
    def modifyRenderer(llegenda, capa=None):
        global f
        if capa is None:
            capa = llegenda.currentLayer()
            if capa is None:
                return
        f = QvFormSimbMapificacio(llegenda, capa)
        f.show()

class QvMapificacio(QObject):

    afegintZona = pyqtSignal(int)  # Porcentaje cubierto (0 - 100)
    zonaAfegida = pyqtSignal(int)  # Tiempo transcurrido (segundos)
    errorAdreca = pyqtSignal(dict) # Registro que no se pudo geocodificar

    def __init__(self, fDades, zona, code='ANSI', delimiter=';', prefixe='QVISTA_', numMostra=60):
        super().__init__()
        self.fDades = self.fZones = fDades
        self.zona = zona
        self.code = code
        self.delimiter = delimiter
        self.prefixe = prefixe
        self.numMostra = numMostra
        self.mostra = []
        self.fields = []
        self.rows = 0
        self.errors = 0
        self.cancel = False
        self.iniDades()
        self.db = QvSqlite()

    def iniDades(self):
        if not os.path.isfile(self.fDades):
            splitFile = os.path.split(self.fDades)
            local = _RUTA_LOCAL + splitFile[1]
            if not os.path.isfile(local):
                return
            else:
                self.fDades = self.fZones = local

        if self.zona is None or self.zona not in _ZONES.keys():
            return
        else:
            self.valZona = _ZONES[self.zona]

        self.campZona = self.prefixe + self.valZona[0]

        with open(self.fDades, "r", encoding=self.code) as csvInput:
            lenFile = os.path.getsize(self.fDades)
            data = csvInput.readline()
            self.fields = data.rstrip(csvInput.newlines).split(self.delimiter)
            self.mostra = []
            if self.numMostra > 0:
                lenMuestra = 0
                maxMuestra = self.numMostra
                num = 0
                for data in csvInput:
                    num += 1
                    data = data.encode(self.code)
                    self.mostra.append(data)
                    lenMuestra += len(data)
                    if num == maxMuestra:
                        break
                lenRow = lenMuestra / num
                self.rows = int(round(lenFile / lenRow))

    def verifCampsAdreca(self, camps):
        try:
            if len(camps) not in list(range(3, 6+1)):
                return False
            num = 0
            for camp in camps:
                num += 1
                if num in (2, 3): # Obligatorio
                    if camp is None or camp not in self.fields:
                        return False
                else: # Opcional
                    if camp is not None and camp != '' and camp not in self.fields:
                        return False
            return True
        except Exception:
            return False
    
    def valorCampAdreca(self, fila, num):
        try:
            camp = self.campsAdreca[num]
            if camp is None or camp == '':
                return ''
            else:
                return fila[camp]
        except Exception:
            return ''
    
    @pyqtSlot()
    def cancelZonificacio(self):
        self.cancel = True

    def zonificacio(self, campsAdreca=(), fZones='', substituir=True, afegintZona=None, zonaAfegida=None, errorAdreca=None):

        if self.verifCampsAdreca(campsAdreca):
            self.campsAdreca = campsAdreca
        else:
            return

        if fZones is None or fZones == '':
            base = os.path.basename(self.fDades)
            splitFile = os.path.splitext(base)
            self.fZones = _RUTA_LOCAL + splitFile[0] + '_' + self.zona + splitFile[1]
        else:
            self.fZones = fZones

        self.substituir = substituir

        if self.rows >= 100:
            nSignal = int(round(self.rows / 100))
        else:
            nSignal = 1

        if afegintZona is not None:
            self.afegintZona.connect(afegintZona)
        if zonaAfegida is not None:
            self.zonaAfegida.connect(zonaAfegida)
        if errorAdreca is not None:
            self.errorAdreca.connect(errorAdreca)

        self.cancel = False
        ini = time.time()

        # Fichero CSV de entrada
        with open(self.fDades, "r", encoding=self.code) as csvInput:

            # Fichero CSV de salida zonificado
            with open(self.fZones, "w", encoding=self.code) as csvOutput:

                # Cabeceras
                campoNuevo = False
                data = csv.DictReader(csvInput, delimiter=self.delimiter)
                if self.campZona not in self.fields:
                    self.fields.append(self.campZona)
                    campoNuevo = True

                writer = csv.DictWriter(csvOutput, delimiter=self.delimiter, fieldnames=self.fields, lineterminator='\n')
                writer.writeheader()

                # Lectura de filas y zonificación
                tot = num = 0
                for row in data:
                    tot += 1

                    if campoNuevo or self.substituir or row[self.campZona] is None or row[self.campZona] == '':
                        val = self.db.geoCampCarrerNum(self.valZona[0],
                              self.valorCampAdreca(row, 0), self.valorCampAdreca(row, 1), self.valorCampAdreca(row, 2),
                              self.valorCampAdreca(row, 3), self.valorCampAdreca(row, 4), self.valorCampAdreca(row, 5))
                        # Error en zonificación
                        if val is None:
                            self.errorAdreca.emit(dict(row))
                            num += 1
                        # Escritura de fila con campo
                        row.update([(self.campZona, val)])
                    
                    writer.writerow(row)
                    # Informe de progreso cada 1% o cada fila si hay menos de 100
                    if self.rows > 0 and tot % nSignal == 0:
                        self.afegintZona.emit(int(round(tot * 100 / self.rows)))

                    # Cancelación del proceso via slot
                    if self.cancel:
                        break

            fin = time.time()
            self.rows = tot
            self.errors = num

            # Informe de fin de proceso y segundos transcurridos
            if not self.cancel:
                self.afegintZona.emit(100)
            self.zonaAfegida.emit(fin - ini)

    def calcSelect(self, llistaCamps=[]):
        # Calculamos filtro
        if self.filtre is None or self.filtre == '':
            filtre = ''
        else:
            filtre = ' WHERE ' + self.filtre
        # Calculamos lista de campos de la zona
        camps = ''
        if llistaCamps is not None and len(llistaCamps) > 0:
            for item in llistaCamps:
                camps += ", Z." + item
        camps += ', Z.GEOMETRY as GEOM'
        # Calculamos SELECT comlpeto de agrupación
        select = "select round(I.AGREGAT " + self.tipusDistribucio + ", " + str(self.numDecimals) + ") AS " + self.campCalculat + \
                 camps + " from Zona AS Z, " + \
                 "(SELECT " + self.tipusAgregacio + " AS AGREGAT, " + self.campZona + " AS CODI " + \
                 "FROM Info" + filtre + " GROUP BY " + self.campZona + ") AS I WHERE Z.CODI = I.CODI"
        return select

    def netejaString(self, txt):
        s = txt.strip()
        s = s.replace(' ', '_')
        s = s.translate(_TRANS)
        return s

    def agregacio(self, llegenda, nomCapa, tipusAgregacio, campCalculat='RESULTAT', campAgregat='', tipusDistribucio="Total",
                  filtre='', numDecimals=-1, numCategories=4, modeCategories="Endreçat",
                  colorBase='Blau', format='%1 - %2', veure=True):

        self.fMapa = ''
        self.capaMapa = None
        self.fSQL = ''
        self.llegenda = llegenda

        if campAgregat is not None and campAgregat != '':
            self.campAgregat = campAgregat
        elif tipusAgregacio == 'Recompte' and campAgregat == '':
            self.campAgregat = '*'
        else:
            return False, "Error en campAgregat"

        if tipusAgregacio is None or tipusAgregacio not in _AGREGACIO.keys():
            return False, "Error en tipusAgregacio"
        self.tipusAgregacio = _AGREGACIO[tipusAgregacio].format(self.campAgregat)

        if tipusDistribucio is None or tipusDistribucio not in _DISTRIBUCIO.keys():
            return False, "Error en tipusDistribucio"
        self.tipusDistribucio = _DISTRIBUCIO[tipusDistribucio]

        if modeCategories is None or modeCategories not in _METODES.keys():
            return False, "Error en modeCategories"
        self.modeCategories = _METODES[modeCategories]

        if colorBase is None or colorBase not in _COLORS.keys():
            return False, "Error en colorBase"
        self.colorBase = _COLORS[colorBase]

        if numDecimals >= 0:
            self.numDecimals = numDecimals
        elif self.tipusAgregacio.startswith('COUNT'):
            self.numDecimals = 0
        else:
            self.numDecimals = 2

        self.numCategories = numCategories
        self.filtre = filtre
        self.campCalculat = campCalculat
        self.nomCapa = self.netejaString(nomCapa)

        # Carga de capa de datos zonificados
        infoLyr = QgsVectorLayer(self.fZones, 'Info', 'ogr')
        infoLyr.setProviderEncoding(self.code)
        if not infoLyr.isValid():
            return False, "No s'ha pogut carregar capa de dades: " + self.fZones

        # Carga de capa base de zona
        self.fBase = _RUTA_DADES + self.valZona[1]
        zonaLyr = QgsVectorLayer(self.fBase, 'Zona', 'ogr')
        zonaLyr.setProviderEncoding("UTF-8")
        if not zonaLyr.isValid():
            return False, "No s'ha pogut carregar capa de zones: " + self.fBase

        # Añadimos capas auxiliares a la leyenda (de forma no visible) para procesarlas
        self.llegenda.project.addMapLayer(infoLyr, False)
        self.llegenda.project.addMapLayer(zonaLyr, False)

        # Lista de campos de zona que se incluirán en la mapificación
        zonaCamps = []
        for field in zonaLyr.fields():
            name = field.name().upper()
            if not name.startswith('QVISTA_') and not name.startswith('OGC_'):
                zonaCamps.append(name)

        # Creación de capa virtual que construye la agregación
        select = self.calcSelect(zonaCamps)
        virtLyr = QgsVectorLayer("?query=" + select, nomCapa, "virtual")
        virtLyr.setProviderEncoding("UTF-8")            

        if not virtLyr.isValid():
            self.llegenda.project.removeMapLayer(zonaLyr.id())
            self.llegenda.project.removeMapLayer(infoLyr.id())
            return False, "No s'ha pogut generar capa de agregació"

        # Guarda capa de agregación en SQLite
        self.fSQL = _RUTA_LOCAL + self.nomCapa + ".sqlite"
        ret, msg = QgsVectorFileWriter.writeAsVectorFormat(virtLyr, self.fSQL, "UTF-8", zonaLyr.crs(), "SQLite")
        if ret != QgsVectorFileWriter.NoError:
            self.llegenda.project.removeMapLayer(zonaLyr.id())
            self.llegenda.project.removeMapLayer(infoLyr.id())
            return False, "No s'ha pogut desar capa de agregació: " + self.fSQL + " (Error - " + msg + ")"

        # Elimina capas de base y datos
        self.llegenda.project.removeMapLayer(zonaLyr.id())
        self.llegenda.project.removeMapLayer(infoLyr.id())

        # Carga capa SQLite de agregación
        mapLyr = QgsVectorLayer(self.fSQL, nomCapa , "ogr")
        mapLyr.setProviderEncoding("UTF-8")
        if not mapLyr.isValid():
            return False, "No s'ha pogut carregar capa de agregació: " + self.fSQL

        # Renderer para mapificar
        self.renderer = QvMapRender().calcRender(mapLyr, self.campCalculat, self.numDecimals,
            self.colorBase, self.numCategories, self.modeCategories, format)
        if self.renderer is None:
            return False, "No s'ha pogut elaborar el mapa"
        else:
            mapLyr.setRenderer(self.renderer)

        # Guarda capa qlr con agregación + mapificación
        self.fMapa = _RUTA_LOCAL + self.nomCapa + '.qlr'

        # Tipo de capa para qVista
        QgsExpressionContextUtils.setLayerVariable(mapLyr, 'qV_tipusCapa', 'MAPIFICACIÓ')

        try:
            # Leer DOM, eliminar path local y guardar en fichero
            domDoc = QgsLayerDefinition.exportLayerDefinitionLayers([mapLyr], QgsReadWriteContext())
            txt = domDoc.toString()
            txt = txt.replace(_RUTA_LOCAL, './')
            with open(self.fMapa, "w+", encoding="UTF-8") as qlr:
                qlr.write(txt)
        except Exception as e:
            fich = self.fMapa
            self.fMapa = ''
            print(e)
            return False, "No s'ha pogut desar capa mapificació: " + fich

        # Mostar qlr de mapificación, si es el caso
        if veure and self.fMapa != '':
            # Cargar qlr
            ok, txt = QgsLayerDefinition.loadLayerDefinition(self.fMapa,
                self.llegenda.project, self.llegenda.root)
            if not ok:
                return False, "No s'ha pogut carregar capa mapificació: " + self.fMapa
            QgsApplication.processEvents()

            # Incluir icono de modificación de simbologia en leyenda
            # node = self.llegenda.nodePerNom(mapLyr.name(), 'layer')
            # if node is not None:
            #     self.capaMapa = node.layer()
            #     self.llegenda.addIndicator(node, self.llegenda.iconaMap)
            #     self.llegenda.iconaMap.clicked.connect(lambda: QvMapRender().modifyRenderer(self.llegenda, self.capaMapa))
            #     self.capaMapa.nameChanged.emit()

        return True, ''

# class verifNumero(QValidator):
#     def validate(self, string, index):
#         txt = string.strip()
#         if txt == '':
#             state = QValidator.Intermediate
#         elif txt.isnumeric():
#             state = QValidator.Acceptable
#         else:
#             state = QValidator.Invalid
#         return (state, string, index)

class QvFormNovaMapificacio(QWidget):
    def __init__(self, llegenda):

        super().__init__(minimumWidth=360)
        self.llegenda = llegenda
        self.setWindowTitle('Afegir capa de mapificació')

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.setLayout(self.layout)

        self.arxiu = QgsFileWidget()
        self.arxiu.setStorageMode(QgsFileWidget.GetFile)
        self.arxiu.setDialogTitle('Selecciona fitxer de dades…')
        self.arxiu.setDefaultRoot(_RUTA_LOCAL)
        self.arxiu.setFilter('Arxius CSV (*.csv)')
        self.arxiu.setSelectedFilter('Arxius CSV (*.csv)')
        self.arxiu.lineEdit().setReadOnly(True)
        self.arxiu.fileChanged.connect(self.arxiuSeleccionat)

        self.zona = QComboBox(self)
        self.zona.setEditable(False)
        self.zona.addItem('Selecciona zona…')
        self.zona.addItems(_ZONES.keys())
        # self.zona.model().item(0).setEnabled(False)

        self.capa = QLineEdit(self)
        self.capa.setMaxLength(40)

        self.tipus = QComboBox(self)
        self.tipus.setEditable(False)
        self.tipus.addItem('Selecciona tipus…')
        self.tipus.addItems(_AGREGACIO.keys())

        self.distribucio = QComboBox(self)
        self.distribucio.setEditable(False)
        self.distribucio.addItems(_DISTRIBUCIO.keys())

        self.calcul = QLineEdit(self)

        self.filtre = QLineEdit(self)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.color.addItems(_COLORS.keys())

        self.metode = QComboBox(self)
        self.metode.setEditable(False)
        self.metode.addItems(_METODES.keys())

        self.intervals = QSpinBox(self)
        self.intervals.setMinimum(2)
        self.intervals.setMaximum(6)
        self.intervals.setSingleStep(1)
        self.intervals.setValue(4)
        self.intervals.setSuffix("  (depèn del mètode)")
        # self.intervals.valueChanged.connect(self.deselectValue)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)

        self.gZona = QGroupBox('Definició zona')
        self.lZona = QFormLayout()
        self.lZona.setSpacing(10)
        self.gZona.setLayout(self.lZona)

        self.lZona.addRow('Arxiu dades:', self.arxiu)
        self.lZona.addRow('Zona:', self.zona)
        self.lZona.addRow('Nom capa:', self.capa)

        self.gDades = QGroupBox('Dades agregació')
        self.lDades = QFormLayout()
        self.lDades.setSpacing(10)
        self.gDades.setLayout(self.lDades)

        self.lDades.addRow('Tipus agregació:', self.tipus)
        self.lDades.addRow('Camp o fòrmula càlcul:', self.calcul)
        self.lDades.addRow('Filtre:', self.filtre) 
        self.lDades.addRow('Distribució:', self.distribucio)

        self.gSimb = QGroupBox('Simbologia mapificació')
        self.lSimb = QFormLayout()
        self.lSimb.setSpacing(10)
        self.gSimb.setLayout(self.lSimb)

        self.lSimb.addRow('Color mapa:', self.color)
        self.lSimb.addRow('Mètode classificació:', self.metode)
        self.lSimb.addRow('Nombre intervals:', self.intervals)

        self.layout.addWidget(self.gZona)
        self.layout.addWidget(self.gDades)
        self.layout.addWidget(self.gSimb)
        self.layout.addWidget(self.buttons)

    def nouArxiu(self, nItem):
        self.zona.setCurrentIndex(nItem)
        self.tipus.setCurrentIndex(0)

    @pyqtSlot(str)
    def arxiuSeleccionat(self, nom):
        n = 0
        if nom != '':
            fNom = os.path.splitext(os.path.basename(nom))[0]
            nItems = self.zona.count()
            for i in range(1, nItems):
                item = self.zona.itemText(i)
                if fNom.upper().endswith('_' + item.upper()):
                    n = i
                    break
        self.nouArxiu(n)

    def msgInfo(self, txt):
        QMessageBox.information(self, 'Informació', txt)

    def msgAvis(self, txt):
        QMessageBox.warning(self, 'Avís', txt)

    def msgError(self, txt):
        QMessageBox.critical(self, 'Error', txt)

    def valida(self):
        ok = False
        if self.arxiu.filePath() == '':
            self.msgInfo("S'ha de seleccionar un arxiu de dades")
            self.arxiu.setFocus()
        elif self.zona.currentIndex() <= 0:
            self.msgInfo("S'ha de seleccionar una zona")
            self.zona.setFocus()
        elif self.capa.text().strip() == '':
            self.msgInfo("S'ha de introduir un nom de capa")
            self.capa.setFocus()
        elif self.tipus.currentIndex() <= 0:
            self.msgInfo("S'ha de seleccionar un tipus d'agregació")
            self.tipus.setFocus()
        elif self.calcul.text().strip() == '' and self.tipus.currentText() != 'Recompte':
            self.msgInfo("S'ha de introduir un cálcul per fer l'agregació")
            self.calcul.setFocus()
        else:
            ok = True
        return ok

    def mapifica(self):
        z = QvMapificacio(self.arxiu.filePath(), self.zona.currentText(), numMostra=0)
        ok, err = z.agregacio(self.llegenda, self.capa.text().strip(), self.tipus.currentText(), campAgregat=self.calcul.text().strip(),
                              filtre=self.filtre.text().strip(), tipusDistribucio=self.distribucio.currentText(),
                              modeCategories=self.metode.currentText(), numCategories=self.intervals.value(),
                              colorBase=self.color.currentText())
        if ok:
            return ''
        else: 
            return err

    @pyqtSlot()
    def ok(self):
        if self.valida():
            self.setDisabled(True)
            msg = self.mapifica()
            if msg == '':
                self.close()
            else:
                self.msgError(msg)
                self.setDisabled(False)
    
    @pyqtSlot()
    def cancel(self):
        self.close()

class QvFormSimbMapificacio(QWidget):
    def __init__(self, llegenda, capa):

        super().__init__(minimumWidth=400)
        self.llegenda = llegenda
        self.capa = capa
        if not self.iniParams():
            return

        self.setWindowTitle('Modificar categories de mapificació')

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.setLayout(self.layout)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.color.addItems(_COLORS.keys())

        self.metode = QComboBox(self)
        self.metode.setEditable(False)
        self.metode.addItems(_METODES_MODIF.keys())
        self.metode.currentIndexChanged.connect(self.canviaMetode)

        self.intervals = QSpinBox(self)
        self.intervals.setMinimum(2)
        self.intervals.setMaximum(6)
        self.intervals.setSingleStep(1)
        self.intervals.setValue(4)
        self.intervals.setSuffix("  (depèn del mètode)")
        # self.intervals.valueChanged.connect(self.deselectValue)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)

        self.gSimb = QGroupBox('Simbologia mapificació')
        self.lSimb = QFormLayout()
        self.lSimb.setSpacing(10)
        self.gSimb.setLayout(self.lSimb)

        self.lSimb.addRow('Color mapa:', self.color)
        self.lSimb.addRow('Mètode classificació:', self.metode)
        self.lSimb.addRow('Nombre intervals:', self.intervals)

        self.gInter = QGroupBox('Definició intervals')
        self.lInter = QGridLayout()
        self.lInter.setSpacing(10)
        self.gInter.setLayout(self.lInter)

        self.wInterval = []
        self.iniIntervals()

        self.layout.addWidget(self.gSimb)
        self.layout.addWidget(self.gInter)
        self.layout.addWidget(self.buttons)

        self.valorsInicials()

    @pyqtSlot()
    def afegirFila(self):
        f = self.sender().property('Fila')
        print('afegirFila', f)

    @pyqtSlot()
    def eliminarFila(self):
        f = self.sender().property('Fila')
        print('eliminarFila', f)

    @pyqtSlot()
    def nouTall(self):
        w = self.sender()
        if w.isModified():
            f = w.property('Fila')
            ini = self.wInterval[f+1][0]
            ini.setText(w.text())
            w.setModified(False)

    def valRang(self, val):
        v = round(val, self.numDecimals)
        if self.numDecimals == 0:
            v = int(v)
        return str(v)

    def iniIntervals(self, maxSize=28):
        renderer = self.capa.renderer()
        cats = renderer.ranges()
        numCats = len(cats)
        for fila, cat in enumerate(cats):
            ini = QLineEdit(self)
            ini.setText(self.valRang(cat.lowerValue()))
            if fila != 0:
                ini.setDisabled(True)
            sep = QLabel('-', self)
            fin = QLineEdit(self)
            fin.setText(self.valRang(cat.upperValue()))
            # Ultima fila: no hay + ni -
            if fila == (numCats - 1):
                widgets = (ini, sep, fin)
            else:
                fin.setProperty('Fila', fila)
                fin.editingFinished.connect(self.nouTall)
                add = QPushButton('+', self)
                add.setMaximumSize(maxSize, maxSize)
                add.setProperty('Fila', fila)
                add.clicked.connect(self.afegirFila)
                add.setFocusPolicy(Qt.NoFocus)
                # Primera fila: solo +
                if fila == 0:
                    widgets = (ini, sep, fin, add)
                # Resto de filas: + y -
                else:
                    rem = QPushButton('-', self)
                    rem.setMaximumSize(maxSize, maxSize)
                    rem.setProperty('Fila', fila)
                    rem.clicked.connect(self.eliminarFila)
                    rem.setFocusPolicy(Qt.NoFocus)
                    widgets = (ini, sep, fin, add, rem)
            # Añadir widgets a la fila
            for col, w in enumerate(widgets):
                self.lInter.addWidget(w, fila, col)
            # Guardar widgets
            self.wInterval.append(widgets)

    def iniParams(self):
        tipus = QgsExpressionContextUtils.layerScope(self.capa).variable('qV_tipusCapa')
        if tipus != 'MAPIFICACIÓ':
            return False
        self.campCalculat, self.numDecimals, self.colorBase, self.numCategories, \
            self.modeCategories, self.format = QvMapRender().paramsRender(self.capa)
        return True

    def valorsInicials(self):        
        self.color.setCurrentIndex(self.color.findText(self.colorBase))
        self.metode.setCurrentIndex(self.metode.findText(self.modeCategories))
        self.intervals.setValue(self.numCategories)

    def valorsFinals(self):
        self.colorBase = self.color.currentText()
        self.modeCategories = self.metode.currentText()
        self.numCategories = self.intervals.value()

    def msgInfo(self, txt):
        QMessageBox.information(self, 'Informació', txt)

    def msgAvis(self, txt):
        QMessageBox.warning(self, 'Avís', txt)

    def msgError(self, txt):
        QMessageBox.critical(self, 'Error', txt)

    def mapifica(self):
        self.valorsFinals()
        self.renderer = QvMapRender().calcRender(self.capa, self.campCalculat, self.numDecimals,
            _COLORS[self.colorBase], self.numCategories, _METODES_MODIF[self.modeCategories], self.format)
        if self.renderer is None:
            return "No s'ha pogut modificar la simbologia"
        self.capa.setRenderer(self.renderer)
        self.capa.triggerRepaint()
        self.llegenda.modificacioProjecte('mapModified')
        return ''

    @pyqtSlot()
    def ok(self):
        self.setDisabled(True)
        msg = self.mapifica()
        if msg == '':
            self.close()
        else:
            self.msgError(msg)
            self.setDisabled(False)

    @pyqtSlot()
    def cancel(self):
        self.close()

    @pyqtSlot()
    def canviaMetode(self):
        custom = (self.metode.currentIndex() == QgsGraduatedSymbolRenderer.Custom)
        self.intervals.setEnabled(not custom)
        if custom: 
            self.intervals.setValue(self.numCategories)
        self.gInter.setVisible(custom)

        # label = self.lParms.labelForField(self.intervals)
        # if label is not None:
        #     label.setVisible(ok)


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()

        z = QvMapificacio('CarrecsANSI.csv', 'Districte')
        # z = QvMapificacio('CarrecsANSI.csv', 'Barri')
        print(z.rows, 'filas en', z.fDades)
        print('Muestra:', z.mostra)

        camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL')
        z.zonificacio(camps,
            afegintZona=lambda n: print('... Procesado', str(n), '% ...'),
            errorAdreca=lambda f: print('Fila sin geocodificar -', f),
            zonaAfegida=lambda n: print('Zona', z.zona, 'procesada en', str(n), 'segs. en ' + z.fZones + ' -', str(z.rows), 'registros,', str(z.errors), 'errores'))

        # zona = 'Barri'
        # camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL', '')
        # z.zonificacio(zona, camps)

        # exit(0)

        # z = QvZonificacio('D:/qVista/CarrecsUTF8.csv', 'UTF-8')
        # print(z.rows, 'filas en', z.fDades)

        # z = QvZonificacio('D:/qVista/GossosBCN.csv')
        # print(z.rows, 'filas en', z.fDades)
