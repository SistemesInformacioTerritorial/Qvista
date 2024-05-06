from enum import Enum


class Resultat(Enum):
    CORRECTE=0
    ADRECA_BUIDA=1
    DIRECCIO_NO_AL_DICCIONARI=2
    ADRECA_NO_COINCIDENT=3
    NUMERO_BUIT=4
    NUMERO_NO_AL_DICCIONARI=5
    NUMERO_BLANC=6
    NUMERO_NO_COINCIDENT=7

class TipusCerca(Enum):
    ADRECAPOSTAL = "Adreça Postal"
    CRUILLA = "Cruïlla"