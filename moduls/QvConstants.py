# "Constants" útils
from qgis.PyQt.QtGui import QFont, QColor
from qgis.PyQt.QtWidgets import QGraphicsDropShadowEffect, QWidget
from moduls.QvImports import * 
# Per poder indicar a una funció que rep una seqüència (tupla, llista)
from typing import Sequence


class QvConstants:
    '''Classe amb mètodes i "constants" estàtiques pel qVista
    Nota: No canviar el valor de les constants. No són constants
    '''
    # Fonts del qVista
    NOMFONT='Arial'
    NOMFONTTITOLS='Segoe UI Light'
    MIDAFONTTITOLS=18
    MIDAFONTSUBTITOLS=14
    MIDAFONTCAPCALERES=12
    MIDAFONTTEXT=10
    FONTCAPCALERES = QFont(NOMFONT, MIDAFONTCAPCALERES, QFont.Bold)
    FONTTITOLS=QFont(NOMFONTTITOLS,MIDAFONTTITOLS)
    FONTSUBTITOLS=QFont(NOMFONTTITOLS,MIDAFONTSUBTITOLS)
    FONTTEXT = QFont(NOMFONT,MIDAFONTTEXT)

    # Colors del qVista, utilitzant el seu codi HTML
    COLORFOSCHTML = '#38474F'
    COLORMIGHTML = '#465A63'
    COLORCLARHTML = '#79909B'
    COLORGRISHTML = '#DDDDDD'
    COLORGRISCLARHTML='#F0F0F0'
    COLORBLANCHTML = '#F9F9F9'
    COLORDESTACATHTML = '#FF6215'
    # COLOROMBRAHTML = '#666666DD'
    COLOROMBRAHTML = '#66000000'
    COLORCERCADORHTML='#B6C2C9'
    COLORTEXTHINTHTML='#A0A0A0'
    # Colors del qVista, utilitzant QColor
    COLORFOSC = QColor(COLORFOSCHTML)
    COLORMIG = QColor(COLORMIGHTML)
    COLORCLAR = QColor(COLORCLARHTML)
    COLORCLARSEMITRANS=QColor(121,144,155,70)
    COLORGRIS = QColor(COLORGRISHTML)
    COLORGRISCLAR=QColor(COLORGRISCLARHTML)
    COLORBLANC = QColor(COLORBLANCHTML)
    COLORDESTACAT = QColor(COLORDESTACATHTML)
    COLOROMBRA = QColor(COLOROMBRAHTML)
    COLORCERCADOR=QColor(COLORCERCADORHTML)
    COLORTEXTHINT=QColor(COLORTEXTHINTHTML)

    #No podem crear una QPixMap sense 
    CURSORFLETXA=Qt.ArrowCursor
    CURSORCLICK=Qt.PointingHandCursor
    CURSORZOOMIN=None
    CURSORZOOMOUT=None
    CURSORDIT=None
    CURSORANOTACIO=None
    CURSOROCUPAT=Qt.WaitCursor

    @staticmethod
    def afegeixOmbraWidget(widget: QWidget):
        """Afegeix una ombra de widget (offset x=3, y=3) al widget rebut
        Arguments:
            widget{QWidget} -- Widget al que afegim la ombra
        """
        return QvConstants.aplicaOmbra(widget, QvConstants.ombraWidget(widget))
    def afegeixOmbraWidgetSeleccionat(widget: QWidget):
        return QvConstants.aplicaOmbra(widget,QvConstants.ombraWidgetSeleccionat(widget))
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
        return QvConstants.aplicaOmbra(widget, QvConstants.ombraHeader(widget))

    # FUNCIONS "PRIVADES"
    # Cap funció de les de sota hauria de ser cridada des de fora de la classe

    # La funció que crea la ombra. Totes les altres tiren d'aquesta
    @staticmethod
    def ombra(parent: QWidget = None, offset: Sequence[int] = (3, 3), radius: int = 15, color: QColor = COLOROMBRA) -> QGraphicsDropShadowEffect:
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
        return QvConstants.ombra(parent)
    def ombraWidgetSeleccionat(parent: QWidget=None) -> QGraphicsDropShadowEffect:
        return QvConstants.ombra(parent,offset=(0,0),radius=20, color=QColor('#444444'))
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
        return ombra
    
    @staticmethod
    def cursorZoomIn():
        if QvConstants.CURSORZOOMIN is None:
            QvConstants.CURSORZOOMIN=QCursor(QPixmap(os.path.join(imatgesDir,'zoom_in.cur')))
        return QvConstants.CURSORZOOMIN
    @staticmethod
    def cursorZoomOut():
        if QvConstants.CURSORZOOMOUT is None:
            QvConstants.CURSORZOOMOUT=QCursor(QPixmap(os.path.join(imatgesDir,'zoom_out.cur')))
        return QvConstants.CURSORZOOMOUT
    @staticmethod
    def cursorDit():
        if QvConstants.CURSORDIT is None:
            QvConstants.CURSORDIT=QCursor(QPixmap(os.path.join(imatgesDir,'dedo.cur')))
        return QvConstants.CURSORDIT
    @staticmethod
    def cursorAnotacio():
        if QvConstants.CURSORANOTACIO is None:
           QvConstants.CURSORANOTACIO=QCursor(QPixmap(os.path.join(imatgesDir,'anotacions.ico')), 0, 23)
        return QvConstants.CURSORANOTACIO
    @staticmethod
    def cursorFletxa():
        return QvConstants.CURSORFLETXA
    @staticmethod
    def cursorClick():
        return QvConstants.CURSORCLICK
    @staticmethod
    def cursorOcupat():
        return QvConstants.CURSOROCUPAT

    # No s'ha d'instanciar la classe, de manera que si fem un init es queixa
    def __init__(self):
        raise TypeError('No es poden crear instàncies de QvConstants')