# -*- coding: utf-8 -*-

from moduls.QvApp import QvApp


class QvGeocod:

    @staticmethod
    def coordsCarrerNum(tipusVia, nomCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        return QvApp().geocod(tipusVia, nomCarrer, None, numIni, lletraIni, numFi, lletraFi)

    @staticmethod
    def coordsCodiNum(codiCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
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

        x, y = QvGeocod.coordsCodiNum('003406', '132', 'B')
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
