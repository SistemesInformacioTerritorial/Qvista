import time
start = time.time()
from qgis.core import *
from qgis.gui import *

from qgis.core.contextmanagers import qgisapp

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt import QtSql

from qgis.PyQt.QtXml import QDomDocument, QDomElement, QDomAttr, QDomText    
from qgis.PyQt.QtCore import pyqtSignal, QPoint

from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings


import csv, codecs
import os
import sys
import time
import requests
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
from QvVisualitzacioCapa import QvVisualitzacioCapa

# from calculadora import Ui_Calculadora

# Dialeg per definir delimitadors en el CSV. Designer.
from finestraDelimitadors import Ui_Dialog

# Botonera lateral
# from Botonera_ui import Ui_Frame

# Panell d'informació
from info_ui import Ui_Informacio

# Cataleg de layers
from cataleg_ui import Ui_Cataleg
print ('QvImports: ',time.time()-start)
# Eines de dibuix
# Icones SVG
# import images_rc
