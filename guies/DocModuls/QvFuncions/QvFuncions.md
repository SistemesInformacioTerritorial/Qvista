# QvFuncions
QvFuncions és un mòdul pensat per agrupar funcions que puguin ser útils per a múltiples mòduls diferents. En aquest arxiu es documenten aquelles funcions que poden no ser trivials en algun aspecte, però no estaran totes

## creaEina
Pot semblar estrany que una classe estigui definida dins d'un arxiu de funcions. Però, donat que Python no distingeix entre funcions i cridables (*callable*) *[para muestra, un botón](https://docs.python.org/3/library/functions.html#built-in-funcs)*, aquí tampoc distingirem. 

La classe creaEina és una classe que serveix per fer de decorador i crear un QDockWidget a partir d'un QWidget. Els dos exemples següents són equivalents:

```Python
class ElMeuWidget(QWidget):
    ...

class ElMeuDockWidget(QDockWidget):
    titol = 'Hola'
    def __init__(self,parent=None):
        super().__init__(self.titol,parent)
```
```Python
@QvFuncions.creaEina(titol='Hola')
class ElMeuDockWidget(QWidget):
    ...

if __name__=='__main__':
    # main de prova. 
    print(issubclass(ElMeuDockWidget,QDockWidget)) # Imprimirà False
    with qgisapp() as app:
        wid = prova() # wid és un QWidget
        wid.show()
        sys.exit(app.exec())
else:
    print(issubclass(ElMeuDockWidget,QDockWidget)) # Imprimirà True
```

La seva utilitat principal és la de crear una eina a partir del widget que ha de contenir, evitant-nos repetir codi absurdament.

El seu funcionament és el següent: està definit com una classe, que en la constructora rep tants arguments amb nom com vulguem, i se'ls desa. El decorador el que fa és que es crida el mètode *\_\_call\_\_* passant-li la classe com a paràmetre la classe que estem construïnt (subclasse de QWidget). Si executem el mòdul com a main, el decorador no fa res, ja que quan executem el programa com a script standalone no volem posar-ho en un QDockWidget. En canvi, si és importat, el decorador genera un QDockWidget contenint el QWidget.