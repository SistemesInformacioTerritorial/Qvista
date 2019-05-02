#"Constants" útils
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class QvConstants:
    FONTTITOLS=QFont('Arial',15,QFont.Bold)
    FONTTEXT=QFont('Arial',10)

    COLORFOSC='#38474F'
    COLORMIG='#465A63'
    COLORCLAR='#79909B'
    COLORGRIS='#DDDDDD'
    COLORBLANC='#F0F0F0'
    COLORDESTACAT='#FF6215'
    COLOROMBRA='#666666'

    #Funció per retornar ombres amb els paràmetres donats
    #Nota: No assignar un mateix objecte a més d'un widget. Només es conservarà a l'últim
    def ombra(parent=None, offset=(3,3), radius=15, color=QColor(COLOROMBRA)):
        OMBRA=QGraphicsDropShadowEffect(parent)
        OMBRA.setBlurRadius(radius)
        OMBRA.setOffset(*offset)
        OMBRA.setColor(color)
        return OMBRA

    def ombraWidget(parent=None):
        return QvConstants.ombra(parent,offset=(3,3))
    def ombraHeader(parent=None):
        return QvConstants.ombra(parent,offset=(0,3))