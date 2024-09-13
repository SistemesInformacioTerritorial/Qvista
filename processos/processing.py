# -*- coding: utf-8 -*-

# Modulo para recubrir métodos del iface para uso desde qVista
# from processos.iface import iface
from moduls.QvIface import QvIface as iface

# QvProcess
processingClass = None

class QvProcessing:

    @staticmethod
    def run(name, params):
        from moduls.QvFuncions import debugging
        try:
            if debugging(): print("RUN processing", name)
            if processingClass.canceled(): return None
            if processingClass is None: return None
            if processingClass.canceled(): return None
            return processingClass.run(name, params)
        except Exception as e:
            print(str(e))
            return None

processing = QvProcessing
