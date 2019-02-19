# -*- coding: utf-8 -*-

import traceback
import sys

class QvError:

    @staticmethod
    def bug(exc_type=None, exc_value=None, exc_tb=None):
        try:
            if exc_type is None or exc_value is None or exc_tb is None:
                exc_type, exc_value, exc_tb = sys.exc_info()
            formatted = traceback.format_exception(exc_type, exc_value, exc_tb)

            fich = ''
            lin = ''
            error = formatted[len(formatted)-2] # ultimo error
            x = error.split(',')
            if len(x) >= 2:
                f = x[0].strip()
                q = 'qVista\\Codi\\'
                n = f.find(q) # buscamos nombre de .py y quitamos " del final
                if n >= 0:
                    fich = f[n+len(q):len(f)-1]
                    fich = fich.replace('\\', '/')
                    f = x[1].strip()
                    q = 'line' # buscamos número de linea y quitamos blancos
                    n = f.find(q)
                    if n >= 0:
                        lin = f[n+len(q):].strip()

            # msg = formatted[len(formatted)-1] # mensaje de error
            # des = ''.join(formatted[:len(formatted)-1])
            # des = ''.join(formatted)

            return fich, lin, formatted
        except:
            return '', '', ''

