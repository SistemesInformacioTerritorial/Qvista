from  moduls.QvImports import *
from qgis.core.contextmanagers import qgisapp
import threading

def printit():
  threading.Timer(5.0, printit).start()
  print ("Hello, World!")

with qgisapp() as app:
    printit()