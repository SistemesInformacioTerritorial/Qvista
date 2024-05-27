from qgis.PyQt.QtWidgets import QVBoxLayout, QLabel, QWidget, QSpacerItem, QSizePolicy
from qgis.core import QgsExpressionContextUtils, QgsProject
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import Qt, QUrl, pyqtSignal
import os
import re
from urllib.parse import urlparse

PREFIX_SEARCH = 'qV_button'

class QvEnllac(QWidget):
    """Una classe del tipus QWidget que servirà per mostrar els enllaços que haurem guardat com a variables de les capes.
    """
    
    def __init__(self):
        QWidget.__init__(self)

        self.llista_enllacos = []
        self.afegir_enllacos()

        self.mostrar_finestra()
        self.mostrar_enllacos()

    def mostrar_finestra(self) -> None:
        """
        Configura i mostra la finestra de l'aplicació.
        """
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(30,20,30,20)
        self.layout.setSpacing(20)
        
    def afegir_enllacos(self) -> None:
        """
        Afegeix enllaços a partir de les variables de les capes (que comencin per qV_button)
        """
        for layer in QgsProject.instance().mapLayers().values():
            totes_variables = QgsExpressionContextUtils.layerScope(layer).variableNames()

            for nom_variable in totes_variables:
                if nom_variable.startswith(PREFIX_SEARCH):
                    valor_variable = QgsExpressionContextUtils.layerScope(layer).variable(nom_variable)
                    self.gestionar_enllac(valor_variable, nom_variable, layer)

    def gestionar_enllac(self, valor_variable:str, nom_variable:str, layer:str) -> None:
        """
        Gestiona i extreu les dades necessàries d'una variable de tipus enllaç
        
        Args:
            valor_variable (str): El valor de la variable a gestionar.
            nom_variable (str): El nom de la variable a gestionar.
            layer(str): El nom de la capa que gestionem
        """
        desc_regex = re.compile(r'desc="([^"]*)"')
        link_regex = re.compile(r'link="([^"]*)"')
        desc_match = desc_regex.search(valor_variable)
        link_match = link_regex.search(valor_variable)

        if not desc_match or desc_match.group(1) == '':
            print("Falta la descripció en la variable:", nom_variable, "a la capa:", layer)
            return
        if not link_match or link_match.group(1) == '':
            print("Falta l'enllaç en la variable:", nom_variable, "a la capa:", layer)
            return
        self.afegir_cerca(desc_match.group(1), link_match.group(1))
    
    def afegir_cerca(self, desc_value:str, link_value:str) -> None:
        """
        Afegeix un nou enllaç/arxiu a la llista d'enllaços.
        
        Args:
            desc_value (str): La descripció de l'enllaç/arxiu a afegir.
            link_value (str): L'enllaç o la ruta de l'arxiu a afegir.
        """
        values_dict = {
            'desc': desc_value,
            'link': link_value,
        }
        self.llista_enllacos.append(values_dict)

    def mostrar_enllacos(self) -> None:
        """
        Mostra tots els enllaços recollits en la interfície de l'usuari.
        """
        for enllac in self.llista_enllacos:
            label = QLabel(self)
            label.setText(f"<a href='{enllac['link']}'>{enllac['desc']}</a>")
            label.setTextFormat(Qt.RichText)
            label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            label.linkActivated.connect(self.obrir_enllac)
            self.layout.addWidget(label)

        # Afegim un espaiador expansible al final del layout
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)
    
    def obrir_enllac(self, url:str) -> None:
        """
        Obre l'enllaç especificat, que pot ser un fitxer local o una URL web.
        
        Args:
            url (str): L'enllaç o la ruta de l'arxiu a obrir.
        """
        if os.path.isfile(url):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(url)))
        elif os.path.isfile(os.path.join(os.getcwd(), url)):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(os.path.join(os.getcwd(), url))))
        else:
            if urlparse(url).scheme == '':
                url = 'https://' + url
            QDesktopServices.openUrl(QUrl(url))