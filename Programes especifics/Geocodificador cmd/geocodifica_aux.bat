@REM Còpia modificada de l'arxiu python-qgis-ltr.bat
@REM Crida al geocodifica.py, garantint que el directori de treball sigui el de la carpeta de codi, i no el de la carpeta on està el .py
@REM NO EXECUTAR DIRECTAMENT
@REM Enlloc d'això, cal fer un .bat que doni valor a la variable d'entorn PATH_QGIS, donant-li com a valor la carpeta on està instal·lat el QGIS, i faci "call" a aquest codi
@REM Quan fem el call, hem de passar-li els paràmetres
@REM Exemple de codi:
@REM    @echo off
@REM    set PATH_QGIS="C:\OSGeo4W64\bin"
@REM    call geocodifica_aux.bat %*

pushd "../../"

pushd %PATH_QGIS%
call o4w_env.bat
call qt5_env.bat
call py3_env.bat
path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%
popd
set PYTHONPATH=%CD%;%PYTHONPATH%
rem SI NO POSES EL DIRECTORI ORIGINAL EL QVAPP POT FALLAR
"%PYTHONHOME%\python" "%CD%\Programes especifics\Geocodificador cmd\geocodifica.py" %*
popd