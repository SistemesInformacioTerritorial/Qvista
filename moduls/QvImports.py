
from qgis.core import *
from qgis.gui import *

from qgis.core.contextmanagers import qgisapp

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt import QtSql
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
from cubista2 import Ui_MainWindow

import plotly
import plotly.graph_objs as go

from moduls.QvUbicacions import QvUbicacions
from moduls.QvPrint import QvPrint
from moduls.QvAnotacions import QvAnotacions
from moduls.QvCanvas import QvCanvas
from moduls.QvToolTip import QvToolTip
from moduls.QvEinesGrafiques import QvSeleccioElement, QvSeleccioPerPoligon
from moduls.QvStreetView import QvStreetView
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
from moduls.QvMapeta import QvMapeta
from moduls.QVCercadorAdreca import QCercadorAdreca
from moduls.QVDistrictesBarris import QVDistrictesBarris
from moduls.QvCataleg import QvCataleg
from moduls.QvVistaMapa import QvVistaMapa
from moduls.QvWizard import QvWizard
from moduls.QvApp import QvApp


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
