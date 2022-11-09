from configuracioQvista_default import ConfigBase
from moduls.QvSingleton import singleton


# Per canviar algun atribut definit a configuracioQvista_default, modificar aquí
# En principi està definit per fer canvis només a les coses definides en majúscula
# Es poden modificar altres coses, up to you
@singleton
class Config(ConfigBase):
    # EXEMPLE de modificació:
    # TITOLFINESTRA = "qVista versio {} - {}"
    # def GETTITOLFINESTRA(self):
    #     return self.TITOLFINESTRA.format(self.VERSIO, datetime.date.today().strftime("%d/%m/%Y"))
    pass


# NO TOCAR. 
# Intercepta l'accés als atributs del mòdul per anar directament als de Config
# EXEMPLE:
# import configuracioQvista
# print(configuracioQvista.versio) # imprimeix configuracioQvista.Config().versio
def __getattr__(nom):
    if nom == 'Config':
        return Config
    try:
        return getattr(Config(), nom)
    except AttributeError:
        try:
            return globals()[nom]
        except KeyError:
            pass
    
    raise AttributeError(f"configuracioQvista no té definit l'atribut {nom}")
