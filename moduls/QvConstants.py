# "Constants" útils
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget, QScrollBar
import tempfile
# Per poder indicar a una funció que rep una seqüència (tupla, llista)
from typing import Sequence


class QvConstants:
    '''Classe amb mètodes i "constants" estàtiques pel qVista
    Nota: No canviar el valor de les constants. No són constants
    '''
    # Fonts del qVista
    NOMFONT='Arial'
    MIDAFONTTITOLS=12
    MIDAFONTTEXT=10
    FONTTITOLS = QFont(NOMFONT, MIDAFONTTITOLS, QFont.Bold)
    FONTTEXT = QFont(NOMFONT,MIDAFONTTEXT, 10)

    # Colors del qVista, utilitzant el seu codi HTML
    COLORFOSCHTML = '#38474F'
    COLORMIGHTML = '#465A63'
    COLORCLARHTML = '#79909B'
    COLORGRISHTML = '#DDDDDD'
    COLORBLANCHTML = '#F0F0F0'
    COLORDESTACATHTML = '#FF6215'
    COLOROMBRAHTML = '#666666'
    # Colors del qVista, utilitzant QColor
    COLORFOSC = QColor(COLORFOSCHTML)
    COLORMIG = QColor(COLORMIGHTML)
    COLORCLAR = QColor(COLORCLARHTML)
    COLORGRIS = QColor(COLORGRISHTML)
    COLORBLANC = QColor(COLORBLANCHTML)
    COLORDESTACAT = QColor(COLORDESTACATHTML)
    COLOROMBRA = QColor(COLOROMBRAHTML)

    # TEMPDIR='C:/temp/qVista/temp'
    # ARXIUAVIS = 'L:/DADES/SIT/Doc/QVISTA/Avisos.htm'
    # ARXIUTMPAVIS = TEMPDIR+'/ultimAvisObert'
    # ARXIUNEWS = 'L:/DADES/SIT/Doc/QVISTA/Noticies.htm'
    # ARXIUTMP = TEMPDIR+'/ultimaNewOberta'
    # Això de sota no hauria d'estar aquí
    SCROLLBARSTYLESHEET = """
            QScrollBar {
                background:%s;
                margin: 0px;
                border: 0px;
            }
            QScrollBar::handle {
                background: %s;
                min-height: 0px;
                border: 0px;
            }
            QScrollBar::sub-page {
                background: %s;
                height: 0 px;
                border: 0px;
            }
            QScrollBar::add-page {
                background: %s;
                height: 0 px;
                border: 0px;
            }""" % (COLORGRISHTML, COLORGRISHTML, COLORBLANCHTML, COLORBLANCHTML)

    @staticmethod
    def afegeixOmbraWidget(widget: QWidget):
        """Afegeix una ombra de widget (offset x=3, y=3) al widget rebut
        Arguments:
            widget{QWidget} -- Widget al que afegim la ombra
        """
        QvConstants.aplicaOmbra(widget, QvConstants.ombraWidget(widget))

    @staticmethod
    def afegeixOmbraHeader(widget: QWidget):
        """Afegeix una ombra de header (offset x=0, y=3) al widget rebut
        Per afegir ombra a un layout, s'ha de fer una cosa així:
            widget=QWidget()
            widget.setLayout(layout)
            QvConstants.afegeixOmbraHeader(widget)
        Arguments:
            widget{QWidget} -- Widget al que afegim la ombra
        """
        QvConstants.aplicaOmbra(widget, QvConstants.ombraHeader(widget))

    def formataScrollbar(scrollbar: QScrollBar):
        '''Dóna el format adequat a una scrollbar'''
        #scrollbar.setStyleSheet(QvConstants.SCROLLBARSTYLESHEET)
        pass
    # FUNCIONS "PRIVADES"
    # Cap funció de les de sota hauria de ser cridada des de fora de la classe

    # La funció que crea la ombra. Totes les altres tiren d'aquesta
    @staticmethod
    def ombra(parent: QWidget = None, offset: Sequence[int] = (3, 3), radius: int = 15, color: QColor = QColor(COLOROMBRA)) -> QGraphicsDropShadowEffect:
        ombra = QGraphicsDropShadowEffect(parent)
        ombra.setBlurRadius(radius)
        ombra.setOffset(*offset)
        ombra.setColor(color)
        return ombra
    # Funcions per retornar ombres
    # Nota: No assignar un mateix objecte ombra a més d'un widget. Només es conservarà a l'últim
    @staticmethod
    def ombraWidget(parent: QWidget = None) -> QGraphicsDropShadowEffect:
        """Retorna una ombra pensada per posar a un widget (amb un offset de x=3 i y=3)

        Keyword Arguments:
            parent{QWidget} -- Pare de l'ombra (default: {None})
        Returns:
            ombra{QGraphicsDropShadowEffect} - Ombra amb l'offset indicat"""
        return QvConstants.ombra(parent, offset=(3, 3))

    @staticmethod
    def ombraHeader(parent: QWidget = None) -> QGraphicsDropShadowEffect:
        """Retorna una ombra pensada per posar a un header (amb un offset de x=0 i y=3)

        Keyword Arguments:
            parent{QWidget} -- Pare de l'ombra (default: {None})
        Returns:
            ombra{QGraphicsDropShadowEffect} - Ombra amb l'offset indicat"""
        return QvConstants.ombra(parent, offset=(0, 3))

    # Aplica la ombra al Widget
    @staticmethod
    def aplicaOmbra(widget: QWidget, ombra: QGraphicsDropShadowEffect):
        widget.setGraphicsEffect(ombra)

    # No s'ha d'instanciar la classe, de manera que si fem un init es queixa
    def __init__(self):
        raise TypeError('No es poden crear instàncies de QvConstants')