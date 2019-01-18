import traceback
import sys
from pprint import pprint
import os

def petada():
    3/0

def f():
    petada()

# f()

try:
    f()
except Exception as err:

    traceback.print_exc()

    exc_type, exc_value, exc_tb = sys.exc_info()
    formatted = traceback.format_exception(exc_type, exc_value, exc_tb)

    # formatted = traceback.format_exception(*trace)
    # Remove the 'Traceback (most recent call last)'
    formatted = formatted[1:]
    tb = ''.join(formatted)
    message = formatted[len(formatted)-1]

    print(message)
    print(tb)

    print('STACK')
    stack = traceback.extract_stack()
    pprint(stack)

    print('FORMAT')
    exc_type, exc_value, exc_tb = sys.exc_info()
    print('Last type', exc_type) # Clase del error
    print('Last value', exc_value) # Mensaje del error

    print('File', exc_tb.tb_frame.f_code.co_filename)
    print('Line', exc_tb.tb_lineno)

# https://docs.python.org/3/library/traceback.html

    # pprint(traceback.format_exception(exc_type, exc_value, exc_tb))
    # pprint(exc_tb.tb_frame.f_code.co_filename)
    # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    # print(exc_type, fname, exc_tb.tb_lineno)