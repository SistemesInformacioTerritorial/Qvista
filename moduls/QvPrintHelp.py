import sys
import pydoc
import importlib
import inspect

modulo_a_tratar='QvMapetaBrujulado'
my_module = importlib.import_module(modulo_a_tratar)
# request=my_module.QvMapeta
aa=dir(my_module)
# buscar en lista aa los que contienen Qv
# mi_clase=aa[3]

# request=getattr(my_module, mi_clase)
# request=getattr(my_module, 'QvPlot')



for name, obj in inspect.getmembers(my_module):
    if inspect.isclass(obj):
        print("obj=",obj)
        # request=obj


# moduleName = ['QvMapeta'] 
# modul = map(__import__, moduleName)

# import my_module

def output_help_to_file(filepath, request):
    """
    Funcion help_to_file
    muy guapa por cierto
    """
    # f = open(filepath, 'a+')
    f = open(filepath, 'w')
    sys.stdout = f
    # pydoc.help(request)
    help(request)
    f.close()
    sys.stdout = sys.__stdout__
    return



# output_help_to_file(r'QvMapeta.txt',QvMapeta.QvMapeta)
# output_help_to_file(r'QvMapeta.txt',request)



