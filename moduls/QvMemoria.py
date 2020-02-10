from configuracioQvista import *
from moduls.QvSingleton import Singleton
import json

from PyQt5.QtGui import QColor

arxiuTmpAvis=dadesdir+'ultimAvisObert'
arxiuTmpNews=dadesdir+'ultimaNewOberta'
arxiuMapesRecents=dadesdir+'mapesRecents'
arxiuDirectoriDesar=dadesdir+'directoriDesar'
arxiuVolHints=dadesdir+'volHints'
arxiuDadesMascara=dadesdir+'dadesMascara'
arxiuCampsGeocod=dadesdir+'geocod.json'

def llegirArxiu(f,encoding='utf-8'):
    with open(f,encoding=encoding) as arxiu:
        return arxiu.read()
def llegirArxiuLinies(f,encoding='utf-8'):
    with open(f,encoding=encoding) as arxiu:
        return arxiu.readlines()


class QvMemoria(Singleton):
    def __init__(self):
        if hasattr(self,'jaCreat'):
            return
        self.jaCreat=True
        if os.path.isfile(arxiuMapesRecents):
            self.mapesRecents=llegirArxiuLinies(arxiuMapesRecents)
        if os.path.isfile(arxiuDirectoriDesar):
            self.directoriDesar=llegirArxiu(arxiuDirectoriDesar,encoding='utf-8')
        self.volHints=not os.path.isfile(arxiuVolHints) or llegirArxiu(arxiuVolHints)!='False'
        if os.path.isfile(arxiuCampsGeocod):
            self.campsGeocod=json.loads(open(arxiuCampsGeocod).read())
        else:
            self.campsGeocod={}
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
    def getVolHints(self):
        return False
        #Quan vulguem posar les hints només cal que traguem la línia superior i descomentem la inferior
        # return self.volHints
    def setVolHints(self,enVol=True):
        self.volHints=enVol
    def getParametresMascara(self):
        if not os.path.exists(arxiuDadesMascara):
            return QColor('white'),70
        with open(arxiuDadesMascara) as f:
            color, opacitat = f.read().split(' ')
            return QColor(color),int(opacitat)
    def setParametresMascara(self,color,opacitat):
        with open(arxiuDadesMascara,'w') as f:
            f.write('%s %i'%(color.name(),opacitat))
    def getCampsGeocod(self,file):
        if file in self.campsGeocod:
            return self.campsGeocod[file]
        return None
    def setCampsGeocod(self,file,camps):
        self.campsGeocod[file]=camps
        
    def pafuera(self):
        if hasattr(self,'mapesRecents'):
            with open(arxiuMapesRecents,'w',encoding='utf-8') as f:
                for x in self.mapesRecents:
                    f.write(x+'\n')
        if hasattr(self,'directoriDesar'):
            with open(arxiuDirectoriDesar,'w',encoding='utf-8') as f:
                f.write(self.directoriDesar)
        with open(arxiuVolHints,'w') as f:
            f.write(str(self.volHints))
        with open(arxiuCampsGeocod,'w') as f:
            f.write(json.dumps(self.campsGeocod))