# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition, QgsVectorFileWriter,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange, QgsAggregateCalculator,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsReadWriteContext)
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtXml import QDomDocument
from moduls.QvSqlite import QvSqlite


from qgis.PyQt.QtWidgets import (QFileDialog, QWidget, QPushButton, QFormLayout, QComboBox, QLabel, QLineEdit,
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
    "Total": ""
    # "Per m2": "/ Z.AREA",
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

_TRANS = str.maketrans('ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöüºª€@$·.,;:()[]¡!¿?|@#%&ç*',
                       'AEIOUaeiouAEIOUaeiouAEIOUaeiouAEIOUaeiouoaEaD____________________')

_RUTA_LOCAL = 'C:/temp/qVista/dades/'
_RUTA_DADES = 'D:/qVista/Codi/Dades/'

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

    def calcColorsGradient(self, iniAlpha):
        colorIni = QColor(self.colorBase)
        colorIni.setAlpha(iniAlpha)
        colorFi = QColor(self.colorBase)
        colorFi.setAlpha(255 - iniAlpha)
        return colorIni, colorFi

    def calcRenderer(self, mapLyr, numCategories, modeCategories, format, iniAlpha=8):
        colorIni, colorFi = self.calcColorsGradient(iniAlpha)
        colorRamp = QgsGradientColorRamp(colorIni, colorFi)
        labelFormat = QgsRendererRangeLabelFormat(format, self.numDecimals)
        symbol = QgsSymbol.defaultSymbol(mapLyr.geometryType())
        # modeCategories:
        # QgsGraduatedSymbolRenderer.EqualInterval,
        # QgsGraduatedSymbolRenderer.Quantile,
        # QgsGraduatedSymbolRenderer.Jenks,
        # QgsGraduatedSymbolRenderer.StdDev,
        # QgsGraduatedSymbolRenderer.Pretty
        renderer = QgsGraduatedSymbolRenderer.createRenderer(mapLyr, self.campCalculat,
            numCategories, modeCategories, symbol, colorRamp, labelFormat)
        return renderer

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

    def calcColor(self, color):
        defColor = _COLORS["Blau"]
        if isinstance(color, str) and color in _COLORS.keys():
            return _COLORS[color]
        if isinstance(color, QColor):
            return color
        return defColor

    def netejaString(self, txt):
        s = txt.strip()
        s = s.replace(' ', '_')
        s = s.translate(_TRANS)
        return s

    def agregacio(self, llegenda, nomCapa, tipusAgregacio, campCalculat='RESULTAT', campAgregat='', tipusDistribucio="Total",
                  filtre='', numDecimals=-1, numCategories=4, modeCategories=QgsGraduatedSymbolRenderer.Pretty,
                  colorBase='Blau', format='%1 - %2', veure=True):

        self.fMapa = ''

        if campAgregat is not None and campAgregat != '':
            self.campAgregat = campAgregat
        elif tipusAgregacio == 'Recompte' and campAgregat == '':
            self.campAgregat = '*'
        else:
            return

        if tipusAgregacio is None or tipusAgregacio not in _AGREGACIO.keys():
            return
        self.tipusAgregacio = _AGREGACIO[tipusAgregacio].format(self.campAgregat)

        if tipusDistribucio is None or tipusDistribucio not in _DISTRIBUCIO.keys():
            return
        self.tipusDistribucio = _DISTRIBUCIO[tipusDistribucio]

        self.colorBase = self.calcColor(colorBase)            

        if numDecimals >= 0:
            self.numDecimals = numDecimals
        elif self.tipusAgregacio.startswith('COUNT'):
            self.numDecimals = 0
        else:
            self.numDecimals = 2

        self.filtre = filtre
        self.campCalculat = campCalculat
        self.nomCapa = self.netejaString(nomCapa)

        # Carga de capa base de zona
        zonaLyr = QgsVectorLayer(_RUTA_DADES + self.valZona[1], 'Zona', 'ogr')
        zonaLyr.setProviderEncoding("UTF-8")
        if zonaLyr.isValid():
            llegenda.project.addMapLayer(zonaLyr, False)

        # Lista de campos de zona que se incluirán en la mapificación
        zonaCamps = []
        for field in zonaLyr.fields():
            name = field.name().upper()
            if not name.startswith('QVISTA_') and not name.startswith('OGC_'):
                zonaCamps.append(name)

        # Carga de capa de datos zonificados
        infoLyr = QgsVectorLayer(self.fZones, 'Info', 'ogr')
        infoLyr.setProviderEncoding(self.code)
        if infoLyr.isValid():
            llegenda.project.addMapLayer(infoLyr, False)

        # Creación de capa virtual que construye la agregación
        select = self.calcSelect(zonaCamps)
        virtLyr = QgsVectorLayer("?query=" + select, nomCapa, "virtual")
        virtLyr.setProviderEncoding("UTF-8")            

        if virtLyr.isValid():
            # Guarda capa de agregación en SQLite
            QgsVectorFileWriter.writeAsVectorFormat(virtLyr, _RUTA_LOCAL + self.nomCapa + ".sqlite", "UTF-8", zonaLyr.crs(), "SQLite")

            # Elimina capas de base y datos
            llegenda.project.removeMapLayer(zonaLyr.id())
            llegenda.project.removeMapLayer(infoLyr.id())

            # Carga capa SQLite de agregación
            mapLyr = QgsVectorLayer(_RUTA_LOCAL + self.nomCapa + ".sqlite", nomCapa , "ogr")
            mapLyr.setProviderEncoding("UTF-8")
            if mapLyr.isValid():

                # Renderer para mapificar
                renderer = self.calcRenderer(mapLyr, numCategories, modeCategories, format)
                mapLyr.setRenderer(renderer)

                # Guarda capa qlr con agregación + mapificación
                self.fMapa = _RUTA_LOCAL + self.nomCapa + '.qlr'
                try:
                    domDoc = QgsLayerDefinition.exportLayerDefinitionLayers([mapLyr], QgsReadWriteContext())
                    txt = domDoc.toString()
                    txt = txt.replace(_RUTA_LOCAL, '')
                    with open(self.fMapa, "w+", encoding="UTF-8") as qlr:
                        qlr.write(txt)
                except Exception as e:
                    self.fMapa = ''
                    print(e)

                # Mostar qlr de mapificación, si es el caso
                if veure and self.fMapa != '':
                    ok, txt = QgsLayerDefinition.loadLayerDefinition(self.fMapa, llegenda.project, llegenda.root)
                    if not ok:
                        print('No se pudo importar mapificación')
                    QgsApplication.processEvents()


class QvFormMapificacio(QWidget):

    def __init__(self, llegenda):

        super().__init__(minimumWidth=360)
        self.llegenda = llegenda
        self.setWindowTitle('Afegir capa de mapificació')

        self.layout = QFormLayout()
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
        self.capa.setMaxLength(30)

        self.tipus = QComboBox(self)
        self.tipus.setEditable(False)
        self.tipus.addItem('Selecciona tipus…')
        self.tipus.addItems(_AGREGACIO.keys())

        self.calcul = QLineEdit(self)

        self.filtre = QLineEdit(self)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.color.addItem('Selecciona color…')
        self.color.addItems(_COLORS.keys())

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)

        self.layout.addRow('Arxiu dades:', self.arxiu)
        self.layout.addRow('Zona:', self.zona)
        self.layout.addRow('Tipus agregació:', self.tipus)
        self.layout.addRow('Nom capa:', self.capa)
        self.layout.addRow('Formula càlcul :', self.calcul)
        self.layout.addRow('Filtre:', self.filtre)
        self.layout.addRow('Color mapa:', self.color)
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

    def avis(self, txt):
        msgBox = QMessageBox()
        msgBox.setText(txt)
        msgBox.exec()

    def valida(self):
        ok = False
        if self.arxiu.filePath() == '':
            self.avis("S'ha de seleccionar un arxiu de dades")
            self.arxiu.setFocus()
        elif self.zona.currentIndex() <= 0:
            self.avis("S'ha de seleccionar una zona")
            self.zona.setFocus()
        elif self.tipus.currentIndex() <= 0:
            self.avis("S'ha de seleccionar un tipus d'agregació")
            self.tipus.setFocus()
        elif self.capa.text().strip() == '':
            self.avis("S'ha de introduir un nom de capa")
            self.capa.setFocus()
        elif self.calcul.text().strip() == '' and self.tipus.currentText() != 'Recompte':
            self.avis("S'ha de introduir un cálcul per fer l'agreagació")
            self.calcul.setFocus()
        elif self.color.currentIndex() <= 0:
            self.avis("S'ha de seleccionar una color per al mapa")
            self.color.setFocus()
        else:
            ok = True
        return ok

    def mapifica(self):
        z = QvMapificacio(self.arxiu.filePath(), self.zona.currentText(), numMostra=0)
        z.agregacio(self.llegenda, self.capa.text().strip(), self.tipus.currentText(),
                    campAgregat=self.calcul.text().strip(),
                    filtre=self.filtre.text().strip(),
                    colorBase=self.color.currentText())

        # Falta: num categorias, metodo de clasificacion, desactivar formulario, progreso...

    @pyqtSlot()
    def ok(self):
        if self.valida():
            self.mapifica()
            self.close()

    @pyqtSlot()
    def cancel(self):
        self.close()


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()

        z = QvMapificacio('CarrecsANSI.csv', 'Barri')
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
