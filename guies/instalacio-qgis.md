# Instal·lació de QGIS LTR per desenvolupar 

* [Descarregar instal·lador](https://download.osgeo.org/osgeo4w/osgeo4w-setup-x86_64.exe) i executar-lo
* Indicar-li el directori en el qual volem instal·lar-lo (en l'exemple D:\OSGeo4W64, però pot ser qualsevol)
* Instal·lació avançada
* Instal·lar els mòduls **qgis-ltr**, **qgis-ltr-oracle-provider**, **python3-pywin32**, **python3-pandas**, **python3-geopandas**
* Si volem utilitzar el proxy de QGIS hem d'anar a Configuración / Opciones / Red: Check Usar proxy para acceso web; Tipo de proxy: DefaultProxy

# Connectar Visual Studio Code amb el QGIS:
```batch
@echo off
call "%~dp0\o4w_env.bat"
call qt5_env.bat
call py3_env.bat
@echo off
path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%
cd /d "C:\Program Files\Microsoft VS Code\Programs\Microsoft VS Code\"
Code.exe %*
```

* Crear un arxiu (vscode-ltr.bat) amb aquest contingut, i desar-lo a la carpeta bin (en l'exemple, D:\OSGeo4W64\bin)
* L'arxiu assumeix que el Visual Studio Code està instal·lat a C:\Program Files\Microsoft VS Code\Programs\Microsoft VS Code. Si no és així, cal posar el directori corresponent
* Crear un accés directe per accedir-hi, allà on vulguem (per exemple, a l'escriptori)

* Degut a un comportament estrany a l'hora de depurar mòduls, pot caldre editar l'arxiu launch.json, per afegir-li el següent:
```json
        "env": {
            "PYTHONPATH": "${workspaceFolder}"
        },
```

* Per fer servir la versió de Python correcta hem de modificar l'arxiu .vscode/settings.json dins de la carpeta on tinguem clonat qVista (per exemple, D:\qVista\codi\\.vscode\settings.json), per assegurar que aparegui el següent:

```json
"python.pythonPath": "${env.PYTHONHOME}/python.exe"
```