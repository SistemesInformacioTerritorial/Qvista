# -*- coding: utf-8 -*-
"""
Módulo de funciones de goecodificación de Oracle
"""
from moduls.QvApp import QvApp


class QvGeocod:
    """Clase con métodos estáticos para uso de la geocodificación de Oracle
    """

    @staticmethod
    def coordsCarrerNum(tipusVia, nomCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        """Retorna las coordenadas de una dirección postal

        Arguments:
            tipusVia {str} -- Tipo de vía
            nomCarrer {str} -- Nombre o variante de la calle
            numIni {str} -- Número postal (primero)

        Keyword Arguments:
            lletraIni {str} -- Letra del primer número postal (default: {''})
            numFi {str} -- Segundo número postal (default: {''})
            lletraFi {str} -- Letra del segundo número postal (default: {''})

        Returns:
            x, y -- Coordenadas en formato ETRS89, o None si no se encuentra
        """
        return QvApp().geocod(tipusVia, nomCarrer, None, numIni, lletraIni, numFi, lletraFi)

    @staticmethod
    def coordsCodiNum(codiCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        """Retorna las coordenadas a partir de código de calle y número postal

        Arguments:
            codiCarrer {str} -- Código de calle
            numIni {str} -- Número postal (primero)

        Keyword Arguments:
            lletraIni {str} -- Letra del primer número postal (default: {''})
            numFi {str} -- Segundo número postal (default: {''})
            lletraFi {str} -- Letra del segundo número postal (default: {''})

        Returns:
            x, y -- Coordenadas en formato ETRS89, o None si no se encuentra
        """
        return QvApp().geocod('', '', codiCarrer, numIni, lletraIni, numFi, lletraFi)


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        x, y = QvGeocod.coordsCodiNum('001808', '23', '', '25')
        if x is None or y is None:
            print('No coords')
        else:
            print('001808', '23', '25', str(x), str(y))

        x, y = QvGeocod.coordsCodiNum('003406', '132', 'B')
        if x is None or y is None:
            print('No coords')
        else:
            print('003406', '132', 'B', str(x), str(y))

        x, y = QvGeocod.coordsCodiNum('dfadfadfadfadf', 'asdfadfad')
        if x is None or y is None:
            print('No coords')
        else:
            print('003406', '132', 'B', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('C', 'Mallorca', '100')
        if x is None or y is None:
            print('No coords')
        else:
            print('C', 'Mallorca', '100', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('Av', 'Diagonal', '220')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'Diagonal', '220', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('Av', 'Diagonal', '45', 'X')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'Diagonal', '45', 'X', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('', 'Msakjdaskjdlasdj', '220')
        if x is None or y is None:
            print('No coords')
        else:
            print('Msakjdaskjdlasdj', '220', str(x), str(y))
