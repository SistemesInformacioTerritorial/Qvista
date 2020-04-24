import time
import builtins
from moduls.QvSingleton import Singleton

class QvMesuraImports(Singleton):
    def __init__(self):
        if hasattr(self,'temps'): return
        # import pathlib
        # for p in pathlib.Path('.').rglob('*.py[co]'):
        #     p.unlink()
        # for p in pathlib.Path('.').rglob('__pycache__'):
        #     p.rmdir()
        self.temps={}
        self.original_import=builtins.__import__
        builtins.__import__=self._import
    def _import(self, name, *args, **kwargs):
        comenca = time.time()
        res = self.original_import(name, *args, **kwargs)
        tempsPassat = time.time()-comenca
        if not name in self.temps:
            self.temps[name]=tempsPassat
        return res
    def getTemps(self):
        return sorted(filter(lambda x: x[1]>0.0,self.temps.items()),key=lambda x: x[1])

QvMesuraImports()