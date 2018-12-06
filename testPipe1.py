
from  moduls.QvImports import *
from multiprocessing import Process,Pipe

from qgis.core.contextmanagers import qgisapp

def f(child_conn):
    with qgisapp() as app: 
        canv = QgsMapCanvas()
        canv.show()
        # msg = "Hello"
        # child_conn.send(msg)
        print(child_conn.recv())
        # child_conn.close()