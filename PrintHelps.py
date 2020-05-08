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
f_hlp_txt = open(fic_error, 'w'); f_hlp_txt.close()


def ejecuta1(modulo_a_tratar):
    """Chapuza para tratar QvEinesGrafiques
    En vez de buscar las clases las pongo a mano (me daba problemas)
    Si cambian las clases debera cambiarse esta funcion (o ver porque falla cuando se hace desde ejecuta)

    Arguments:
      modulo_a_tratar string -- nombre del modulo
    """

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
    """Recibe un modulo.\n
    Construye nombre de fichero de salida, como nombre del modulo pero con 
    extension .txt que estara en directorio temporal.\n
    Abre el modulo y busca las clases "class"\n
    Ejecuta help de cada clase y lo escribe en el fichero .txt\n

    Arguments:
        modulo_a_tratar string -- nombre del modulo
    """
    queModulo= modulo_a_tratar
    my_module = importlib.import_module(queModulo)
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
        with open(fic_error,"a+") as f_hlp_txt:
            f_hlp_txt.writelines("error lectura: ",modulo_a_tratar,str(ee)+'\n')
        print("error lectura:",modulo_a_tratar,str(ee))
def output_help_to_file(filepath, request):
    """ Escribe en fichero el resultado de help(request)

    Arguments:
        filepath string    -- Path del fichero de salida
        request {[object]} -- modulo, clase.... que es parametro del help
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
def splitfilename(filename):
    """
    extrae del path del fichero su nombre y su extension

    Arguments:
        filename string -- path del fichero a truncar

    Returns:
        sname  string -- nombre
        sext   string -- extension
    """
    
    sname=''
    sext=''
    i=filename.rfind(".")
    if(i!=0):
        n=len(filename)
        j=n-i-1
        sname=filename[0:i]
        sext=filename[-j:]    
    return sname, sext


"""
Obtengo lista con modulos
Trataré los que comienzan con Qv excluyendo QvPrintHelp2



"""

# Lista de ficheros py de la carpeta moduls
mylist = [f for f in glob.glob(r"d:\\qVista\\codi\\moduls\\*.py")]

# recorrido de lista, seleccionando los que empiezan por Qv 
# y no son este programa
for modulo in mylist:
    for f in glob.glob(modulo):
        sfilename, sext = splitfilename(os.path.split(f)[-1])
        nn= sfilename.find('Qv') 

        if nn!=0:
            continue

        print("voy a tratar",sfilename)
        try:
            ejecuta('moduls.'+sfilename)
        except Exception as ee:
            with open(fic_error,"a+") as f_hlp_txt:
                f_hlp_txt.writelines("error en ejecuta: "+sfilename+"  "+str(ee)+ '\n' )

            print("error en ejecuta: ",sext,str(ee))
            

try:
    soloUno= 'qVista'
    with open(fic_error,"a+") as f_hlp_txt:
        f_hlp_txt.writelines("voy a tratar" +soloUno +'\n')
    ejecuta(soloUno)
except Exception as ee:
    with open(fic_error,"a+") as f_hlp_txt:
        f_hlp_txt.writelines("error en ejecuta: "+soloUno+str(ee)+ '\n' )    
    print("error: "+soloUno)

# parche porque me peta esta clase
try:
    with open(fic_error,"a+") as f_hlp_txt:
        f_hlp_txt.writelines("voy a tratar" +'QvEinesGrafiques' +'\n')
    ejecuta1('moduls.'+'QvEinesGrafiques')
except Exception as ee:
    with open(fic_error,"a+") as f_hlp_txt:
        f_hlp_txt.writelines("error en ejecuta: "+soloUno+str(ee)+ '\n' )    
    print("error: "+soloUno)

    
