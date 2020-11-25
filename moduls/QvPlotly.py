# -*- coding: utf-8 -*-

import plotly.graph_objs as go
import plotly as py

from pathlib import Path
import os
import time

from moduls.QvConstants import QvConstants
from moduls.QvVisorHTML import QvVisorHTML
from moduls import QvFuncions
from configuracioQvista import tempdir


class QvPlot:
    '''Classe per crear un gràfic de manera senzilla, fent d'embolcall dels
     gràfics de plotly més utilitzats
El seu funcionament és molt senzill. Tenim una sèrie de mètodes de classe que
 construeixen instàncies de la classe.
Exemple de codi:
    graf = QvPlot.linia(['Districte 1', 'Districte 2', 'Districte 3'], [3, 4, 6],
     arxiu='C:/temp/qVista/dades/capaExemple.gpkg')
    graf.write()
El codi d'exemple crea un gràfic de línia, posant a l'eix X els valors de la
 primera llista, a l'eix Y els de la segona, i agafant com a base pel nom de
 l'arxiu la ruta donada
Això vol dir que el gràfic es desarà a un arxiu anomenat
 C:/temp/qVista/dades/capaExemple.html, com una manera d'associar-lo a l'arxiu donat.

La llista de paràmetres permesos es pot veure a la funció __init__. No obstant, la
 construcció de gràfics només s'hauria de fer amb els mètodes de classe, a saber:
 - QvPlot.linia
 - QvPlot.barres
 - QvPlot.punts
 - QvPlot.pastis

Sobre una instància de la classe es poden fer principalment dues coses: mostrar i escriure:

 - show(): mostra el gràfic en el navegador del sistema.
 - write(): escriu el gràfic a l'arxiu html associat (mètode preferit, ja que
             permet obrir-lo en un navegador intern dins del propi programa)

La classe té també un mètode estàtic per obtenir el nom de l'html associat
 a un altre arxiu. Per fer-lo servir només cal fer el següent:

rutaHtml = QvPlot.getFileName('C:/temp/qVista/dades/capaExemple.gpkg')
# rutaHtml valdrà 'C:/temp/qVista/dades/capaExemple.html'

Aquest mètode permet crear l'arxiu html en una part del codi, i mostrar-lo
 en una altra. Només cal crear la instància i fer el write en una part i,
 sense necessitat de desar el nom en cap variable, en una altra part del
 codi consultar-lo i fer el que es vulgui
    '''
    # classmethod és una funció decoradora que serveix per crear mètodes de classe
    # En python, un mètode de classe és aquell que enlloc de rebre una
    #  instància de la classe (habitualment anomenada self), rep la pròpia classe
    #  (habitualment anomenada cls). Treballen sobre la pròpia classe i no una
    #  instància d'aquesta. Així, doncs, es criden directament sobre la classe.
    # En aquest cas, els mètodes es fan servir per construir instàncies de la
    #  classe amb determinades propietats.
    @classmethod
    def barres(cls, *args, **kwargs):
        res = cls(*args, **kwargs)
        res.setBarres()
        return res

    @classmethod
    def linia(cls, *args, **kwargs):
        res = cls(*args, **kwargs)
        res.setLinia()
        return res

    @classmethod
    def punts(cls, *args, **kwargs):
        res = cls(*args, **kwargs)
        res.setPunts()
        return res

    @classmethod
    def pastis(cls, *args, **kwargs):
        res = cls(*args, **kwargs)
        res.setPastis()
        return res

    def write(self):
        if not hasattr(self, '_fig'):
            # llençar excepció
            pass
        py.offline.plot(self._fig, filename=str(self.arxiu), auto_open=False)

    def show(self):
        if not hasattr(self, '_fig'):
            # llençar excepció
            pass
        py.offline.plot(self._fig, filename=str(self.arxiu))
        # self._fig.show()

    @staticmethod
    def getFileName(nom):
        return Path(nom).with_suffix('.html')

    def __init__(self, eixX, eixY, arxiu=None, horitzontal=False, color=None, titol='', ordenat=False, invertit=False):
        self._eixX = eixX
        self._eixY = eixY
        if arxiu is None:
            arxiu = os.path.join(tempdir, str(time.time()))
        self.arxiu = self.getFileName(arxiu)
        self._horitzontal = horitzontal
        if color is None:
            color = QvConstants.COLORDESTACATHTML
        self._color = color

        self.titol = titol

        self.ordenat = ordenat

        self.invertit = invertit
        
        if self._horitzontal:
            alcada=max(42*len(self._eixY), QvChart.midaX-200)
        else:
            alcada=42*max(self._eixY)-200
        self._lay = go.Layout(
            title=titol,
            titlefont=dict(
                color=QvConstants.COLORDESTACATHTML
            ),
            barmode='stack',
            separators=',.',
            xaxis=dict(
                automargin=True
            ),
            yaxis=dict(
                automargin=True
            ),
            # bargap=0.7,
            height=max(42*len(self._eixY), QvChart.midaX-200) if self._horitzontal else None
        )

    def _getFiguraAux(self, fig, **kw):
        if self.ordenat:
            if self._horitzontal:
                kw['x'], kw['y'] = zip(*sorted(zip(kw['x'],kw['y']), reverse=self.invertit))
            else:
                kw['y'], kw['x'] = zip(*sorted(zip(kw['y'],kw['x']), reverse=self.invertit))
        return go.Figure(data=(fig(**kw),), layout=self._lay)

    def _getFiguraXY(self, fig):
        self.figuraPl=fig
        self.xy=True
        kw = {'x': self._eixX, 'y': self._eixY}
        if self._horitzontal is not None:
            kw['orientation'] = 'h' if self._horitzontal else 'v'
        figura = self._getFiguraAux(fig, **kw)
        # figura.update_traces(marker_color=self._color)
        return figura

    def _getFiguraLbl(self, fig):
        self.figuraPl=fig
        self.xy=False
        kw = {'labels': self._eixX, 'values': self._eixY}
        return self._getFiguraAux(fig, **kw)

    # converteix el plot en un gràfic de barres
    def setBarres(self):
        self._fig = self._getFiguraXY(go.Bar)


    # Converteix el plot en un gràfic de línies
    def setLinia(self):
        self._fig = self._getFiguraXY(go.Scatter)


    # Ídem però amb punts (com una línia però només amb els punts)
    def setPunts(self):
        def aux(*args, **kwargs):
            return go.Scatter(*args, mode='markers', **kwargs)
        self._fig = self._getFiguraXY(aux)


    # Ídem però amb un pastís (el típic formatget)
    def setPastis(self):
        self._fig = self._getFiguraLbl(go.Pie)
    

    def setOrdenat(self,ordenat):
        self.ordenat=ordenat
        if self.xy:
            self._fig=self._getFiguraXY(self.figuraPl)
        else:
            self._fig=self._getFiguraLbl(self.figuraPl)
    
    def setInvertit(self,invertit):
        self.invertit=invertit
        self.setOrdenat(self.ordenat)


class QvChart(QvVisorHTML):
    '''Un QvVisorHTML canviant alguna propietat per adaptar-lo al plotly
Es pot construir com qualsevol QvVisorHTML donant-li la ruta de l'arxiu a mostrar i el seu títol,
o passant-li un QvPlot com a paràmetre.
Cas 1:
    visor = QvChart('C:/temp/qVista/dades/prova.html','Gràfic de prova generat anteriorment')
    visor.show()
Cas 2:
    plot = QvPlot.barres(llista1, llista2, titol='hola')
    visor = QvChart.visorGrafic(plot)
    visor.show()
'''
    midaX = 960
    midaY = 720

    def __init__(self, *args, **kwargs):
        if len(args)==1:
            self.grafic=args[0]
            args=[self.grafic.arxiu, self.grafic.titol]
        super().__init__(*args, **kwargs)
        # El factor de zoom serà 1, ja que amb més factor es veu malament
        # La mida per defecte serà 960x720, una mica més gran, perquè es vegi bé
        self.setZoomFactor(1)
        self.resize(960, 720)
        if hasattr(self,'grafic'):
            from moduls.QvPushButton import QvPushButton
            self.ordenat=self.grafic.ordenat
            self.invertit=self.grafic.invertit
            # Afegir els botons
            self.bOrdenar=QvPushButton('Original' if self.ordenat else 'Ordenar')
            self.bOrdenar.clicked.connect(self.swapOrdenar)
            self.layoutBoto.insertWidget(0,self.bOrdenar)
            
            self.bInvertir=QvPushButton('Invertit: %s' %('Cert' if self.invertit else 'Fals'))
            self.bInvertir.clicked.connect(self.swapInvertir)
            self.layoutBoto.insertWidget(1,self.bInvertir)
            self.bInvertir.setVisible(self.ordenat)
    
    def swapInvertir(self):
        self.invertit = not self.invertit
        self.grafic.setInvertit(self.invertit)
        self.bInvertir.setText('Invertit: %s' %('Cert' if self.invertit else 'Fals'))
        self.ordenar()
    
    def swapOrdenar(self):
        self.ordenat = not self.ordenat
        self.grafic.setOrdenat(self.ordenat)
        self.bOrdenar.setText('Original' if self.ordenat else 'Ordenar')
        self.bInvertir.setVisible(self.ordenat)
        self.ordenar()
    
    @QvFuncions.mostraSpinner
    def ordenar(self):
        self.grafic.write()
        self.caixaText.reload()

    @classmethod
    def visorGrafic(cls, grafic: QvPlot):
        if not os.path.isfile(grafic.arxiu):
            grafic.write()
        # vis = cls(grafic.arxiu, grafic.titol, logo=True)
        vis = cls(grafic, logo=True)
        if grafic._horitzontal:
            vis.resize(cls.midaY, cls.midaX)
        else:
            vis.resize(cls.midaX, cls.midaY)
        return vis


if __name__ == '__main__':
    from qgis.core.contextmanagers import qgisapp
    pl = QvPlot.barres(['D', 'B', 'C'], [5, 2, 3], titol='Hola')
    with qgisapp() as app:
        # opció 1: mostrar dins d'un visor html
        visor = QvChart.visorGrafic(pl)
        visor.show()
    # opció 2: mostrar dins del navegador
    # pl.show()
