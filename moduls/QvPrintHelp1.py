import sys
import pydoc
import importlib
import inspect
import re

def output_help_to_file(filepath, request):
    """ Escribe en fichero el resultado de help(request)

    Arguments:
        filepath {[type]} -- Path del fichero de salida
        request {[object]} -- modulo, clase.... 
    """


    f = open(filepath, 'a+')
    # f = open(filepath, 'w')
    sys.stdout = f
    # pydoc.help(request)
    """
    help()
    To get a list of available modules, keywords, symbols, or topics, type
                "modules", "keywords", "symbols", or "topics".  Each module also comes
    with a one-line summary of what it does; to list the modules whose name
    or summary contain a given string such as "spam", type "modules spam"." 
    help"""
    help(request)
    f.close()
    sys.stdout = sys.__stdout__
    return



modulo_a_tratar='QvAtributs'
modulo_a_tratar='QvMapeta'
modulo_a_tratar='QvMapetaBrujulado'
modulo_a_tratar='QvMapRenderer'
modulo_a_tratar='QVCercadorAdreca'
modulo_a_tratar='QvMapeta'
modulo_a_tratar='QvAnotacions'
modulo_a_tratar='QvAnotacions'
modulo_a_tratar='QvAnotacions'

modulo_a_tratar='QvDocumentacio'
modulo_a_tratar='QVCercadorAdreca'
modulo_a_tratar='qVista'

import glob
import os.path

mylist = [f for f in glob.glob("moduls/*.py")]


def splitfilename(filename):
    sname=""
    sext=""
    i=filename.rfind(".")
    if(i!=0):
        n=len(filename)
        j=n-i-1
        sname=filename[0:i]
        sext=filename[-j:]    
    return sname, sext


for modulo in mylist:
    for f in glob.glob(modulo):
        # name= os.path.split(f)[-1]
        
        sext, sfilename = splitfilename(os.path.split(f)[-1])
        print(sext)


            

my_module = importlib.import_module(modulo_a_tratar)
fichero=my_module.__file__

f = open(r'salidaHelp.txt', 'w')
f.close()
# with open(r"D:\qVista\Codi\moduls\QvMapetaBrujulado.py","r") as f:
with open(fichero,"r") as f:
    for l in f:
        m = re.match(r"class.*",l)
        if m:

            nn0=m[0].replace('class ','')
            mi_clase=nn0[:nn0.find("(")]
            print(my_module,mi_clase)   
            request=getattr(my_module, mi_clase)

            # help(request)

              

            output_help_to_file(r'salidaHelp.txt',request)                     

