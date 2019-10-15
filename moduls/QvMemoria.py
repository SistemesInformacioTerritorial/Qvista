from configuracioQvista import *
from moduls.QvSingleton import Singleton

arxiuTmpAvis=dadesdir+'ultimAvisObert'
arxiuTmpNews=dadesdir+'ultimaNewOberta'
arxiuMapesRecents=dadesdir+'mapesRecents'
arxiuDirectoriDesar=dadesdir+'directoriDesar'

class QvMemoria(Singleton):
    def __init__(self):
        if hasattr(self,'jaCreat'):
            return
        self.jaCreat=True
        if os.path.isfile(arxiuMapesRecents):
            self.mapesRecents=open(arxiuMapesRecents,encoding='utf-8').readlines()
        if os.path.isfile(arxiuDirectoriDesar):
            self.directoriDesar=open(arxiuDirectoriDesar,encoding='utf-8').read()
        pass
    def getUltimaNew(self):
        try:
            return os.path.getmtime(arxiuTmpNews)
        except:
            return 0
            #Retornar l'inici dels temps
    def setUltimaNew(self):
        with open(arxiuTmpNews,'w',encoding='utf-8') as f:
            f.write('(╯°□°)╯︵ ┻━┻')#Escrivim el que sigui, l'important és la data de l'arxiu
    def getUltimAvis(self):
        try:
            return os.path.getmtime(arxiuTmpAvis)
        except:
            return 0
            #Retornar l'inici dels temps
    def setUltimAvis(self):
        with open(arxiuTmpAvis,'w',encoding='utf-8') as f:
            f.write('ᕦ(ò_óˇ)ᕤ')
    def getMapesRecents(self):
        try:
            return self.mapesRecents
        except:
            return []
        pass
    def setMapesRecents(self,recents):
        self.mapesRecents=recents
    def getDirectoriDesar(self):
        try:
            return self.directoriDesar
        except:
            return str(Path.home().resolve())
    def setDirectoriDesar(self,directori):
        self.directoriDesar=directori
    def pafuera(self):
        if hasattr(self,'mapesRecents'):
            with open(arxiuMapesRecents,'w',encoding='utf-8') as f:
                for x in self.mapesRecents:
                    f.write(x+'\n')
        if hasattr(self,'directoriDesar'):
            with open(arxiuDirectoriDesar,'w',encoding='utf-8') as f:
                f.write(self.directoriDesar)