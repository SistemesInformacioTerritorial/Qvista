import time
start = time.time()
print ('Inici')
from qgis.core import *
end = time.time()
print ('core', end-start)
from qgis.gui import *
print ('gui', end-start)

from qgis.core.contextmanagers import qgisapp

from qgis.PyQt.QtCore import *
print ('qtcore', end-start)
from qgis.PyQt.QtGui import *
print ('qtgui', end-start)
from qgis.PyQt.QtWidgets import *
print ('qtwidgets', end-start)
from qgis.PyQt import QtSql
end = time.time()
print ('qtsql', end-start)

from qgis.PyQt.QtXml import QDomDocument, QDomElement, QDomAttr, QDomText    
from qgis.PyQt.QtCore import pyqtSignal

from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings

import csv, codecs
import os
import sys
import time
import sqlite3
from threading import Thread
import urllib.request, json 
import subprocess
from time import sleep

#Fitxer de configuració de variables d'inici.
from configuracioQvista import *

# Plantilla del qVista
from cubista3 import Ui_MainWindow

# import plotly
# import plotly.graph_objs as go



# Widget de propietats del layer. Designer.
from dlgLayerProperties import LayerProperties

from calculadora import Ui_Calculadora

# Dialeg per definir delimitadors en el CSV. Designer.
from finestraDelimitadors import Ui_Dialog

# Botonera lateral
# from Botonera_ui import Ui_Frame

# Panell d'informació
from info_ui import Ui_Informacio

# Cataleg de layers
from cataleg_ui import Ui_Cataleg

# Eines de dibuix
# Icones SVG
# import images_rc
