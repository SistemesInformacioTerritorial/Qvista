from typing import Dict, List, Optional, Tuple
from qgis.PyQt.QtWidgets import QVBoxLayout, QLabel, QWidget, QSpacerItem, QSizePolicy
from qgis.core import QgsExpressionContextUtils, QgsProject
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import Qt, QUrl, pyqtSignal
import os
import re
from urllib.parse import urlparse
from moduls.utils import get_links

PREFIX_SEARCH = 'qV_button'

class QvEnllac(QWidget):
    """Una classe del tipus QWidget que servirà per mostrar els enllaços que haurem guardat com a variables de les capes.
    """
    
    def __init__(self, llista_enllacos):
        QWidget.__init__(self)

        self.llista_enllacos = llista_enllacos

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