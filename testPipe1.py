
from  moduls.QvImports import *
from multiprocessing import Process,Pipe

from qgis.core.contextmanagers import qgisapp

import threading
import pickle


def f(child_conn, prj):
    with qgisapp() as app:         
        try:
            infile = open('ordres','rb')
            mapa = pickle.load(infile)
            infile.close()
            print (mapa)
        except:
            pass
        canvas = QgsMapCanvas()
        project = QgsProject.instance()
        root = QgsProject.instance().layerTreeRoot()

        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        canvas.show()
        project.read(prj)
        global mapa2
        mapa2 = prj   
        def buscoPickle():
            global mapa2
            threading.Timer(5.0, buscoPickle).start()
            infile = open('ordres','rb')
            mapa = pickle.load(infile)
            infile.close()
            print ('rebo ',mapa, mapa2)
            if mapa != mapa2:
                print ('cargo ',mapa)
                project.read(mapa) 
                mapa2 = mapa
        buscoPickle()
        # msg = "Hello"
        # child_conn.send(msg)
        # print(child_conn.recv())
        # child_conn.close()