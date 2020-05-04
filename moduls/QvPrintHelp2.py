import sys
import pydoc
import importlib
import inspect
import re
import glob
import os.path
import configuracioQvista

tempdir=configuracioQvista.tempdir
fic_error=os.path.join(tempdir,"ERR_help.txt")
f_err = open(fic_error, 'w'); f_err.close()




def ejecuta1(modulo_a_tratar):

    my_module = importlib.import_module(modulo_a_tratar)
    fichero=my_module.__file__

    fic_salida= modulo_a_tratar+'.txt'
    fic_salida=os.path.join(tempdir,fic_salida)
 
    try:
        request='QvEinesGrafiques.QvSeleccioGrafica'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvMesuraGrafica'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.MascaraAux'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvMascaraEinaPlantilla'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvMascaraEinaClick'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvMascaraEinaDibuixa'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvMascaraEinaCercle'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvMesuraMultiLinia'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvMarcador'
        output_help_to_file(fic_salida,request)
        request='QvEinesGrafiques.QvSeleccioElement'
        output_help_to_file(fic_salida,request)




    except Exception as ee:
        print(str(ee))
                         
  
    
                  
def ejecuta(modulo_a_tratar):

    my_module = importlib.import_module(modulo_a_tratar)
    fichero=my_module.__file__

    fic_salida= modulo_a_tratar+'.txt'
    fic_salida=os.path.join(tempdir,fic_salida)
    f = open(fic_salida, 'w');   f.close()

    try:
      with open(fichero,"r",encoding="utf8") as f:
            for l in f:
                m = re.match(r"class.*",l)
                if m:
                    nn0=m[0].replace('class ','')
                    mi_clase=nn0[:nn0.find("(")]
                    print(my_module,mi_clase)   
                    request=getattr(my_module, mi_clase)
                    # help(request)
                    try:
                        output_help_to_file(fic_salida,request)
                    except Exception as ee:
                        print(str(ee))
                         
    except Exception as ee:
        with open(fic_error,"a+") as f_err:
            f_err.writelines("error lectura: ",modulo_a_tratar,str(ee)+'\n')
        print("error lectura:",modulo_a_tratar,str(ee))


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


# QvEinesGrafiques.QvMesuraMultiLinia

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

# Lista de ficheros py de la carpeta moduls
mylist = [f for f in glob.glob("moduls/*.py")]

# recorrido de lista, seleccionando los que empiezan por Qv 
# y no son este programa
for modulo in mylist:
    for f in glob.glob(modulo):
        sext, sfilename = splitfilename(os.path.split(f)[-1])
        nn= sext.find('Qv') 
        if nn==0 and sext != "QvPrintHelp2":
            print("voy a tratar",sext)
            # with open(fic_error,"a+") as f_err:
            #     f_err.writelines("voy a tratar: "+ sext +'\n')
            try:
                ejecuta(sext)
            except Exception as ee:
                with open(fic_error,"a+") as f_err:
                    f_err.writelines("error en ejecuta: "+sext+"  "+str(ee)+ '\n' )

                print("error en ejecuta: ",sext,str(ee))
            


try:
    soloUno= 'qVista'
    # with open(fic_error,"a+") as f_err:
    #     f_err.writelines("voy a tratar" +soloUno +'\n')
    ejecuta(soloUno)
except Exception as ee:
    with open(fic_error,"a+") as f_err:
        f_err.writelines("error en ejecuta: "+soloUno+str(ee)+ '\n' )    
    print("error: "+soloUno)





# parche porque me peta esta clase
try:
    soloUno= 'QvEinesGrafiques'
    with open(fic_error,"a+") as f_err:
        f_err.writelines("voy a tratar" +soloUno +'\n')
    ejecuta1(soloUno)
except Exception as ee:
    with open(fic_error,"a+") as f_err:
        f_err.writelines("error en ejecuta: "+soloUno+str(ee)+ '\n' )    
    print("error: "+soloUno)

    
