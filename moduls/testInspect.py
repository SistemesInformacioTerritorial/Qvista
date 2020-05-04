import sys, inspect
import importlib



def print_classes():
    
    modulo_a_tratar='QvMapetaBrujulado'
    my_module = importlib.import_module(modulo_a_tratar)
    for name, obj in inspect.getmembers(my_module):
        # if inspect.isclass(obj):
        if inspect.isroutine(obj):
            print(obj)


print_classes()