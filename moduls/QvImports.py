print('CODI OBSOLET. No utilitzar QvImports.py!')
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

from qgis.PyQt.QtWebKitWidgets import QWebView , QWebPage
from qgis.PyQt.QtWebKit import QWebSettings


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
from pathlib import Path

#Fitxer de configuració de variables d'inici.
from configuracioQvista import *

# Plantilla del qVista
from cubista3 import Ui_MainWindow

# import plotly
# import plotly.graph_objs as go



# Widget de propietats del layer. Designer.
# from moduls.QvVisualitzacioCapa import QvVisualitzacioCapa

# from calculadora import Ui_Calculadora



# Botonera lateral
# from Botonera_ui import Ui_Frame

# Panell d'informació
from info_ui import Ui_Informacio


print ('QvImports: ',time.time()-start)
# Eines de dibuix
# Icones SVG
# import images_rc
