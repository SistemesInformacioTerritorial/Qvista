# La memòria de qVista

qVista és un programa que és capaç de conservar certa memòria sobre execucions anteriors. En concret és capaç de conservar:
* Quan hem vist les notícies per última vegadaa
* Quan hem vist els avisos per última vegada
* Mapes visualitzats recentment
* Directori on hem desat la última vegada
* Paràmetres amb els que creem la màscara
* Camps amb els que hem geocodificat un arxiu
* Arxiu resultant de la geocodificació
* Catàlegs locals

Tota aquesta memòria es gestiona des del QvMemoria. Aquesta classe Singleton pot ser invocada des de qualsevol lloc, i permet modificar aquesta memòria. Un exemple d'ús:

```Python
QvMemoria().setDirectoriDesar(os.path.abspath('../dades'))
```