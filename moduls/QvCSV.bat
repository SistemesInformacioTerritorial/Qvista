@REM NECESSARI PER QGIS ANTERIORS A 3.16 LTR
@REM Un cop es canviï de versió es pot modificar
@REM Còpia modificada de l'arxiu python-qgis-ltr.bat de QGIS 3.10
@REM S'ha de fer servir perquè el python-qgis-ltr.bat de QGIS 3.10 canvia el directori de treball
@REM En concret, un exemple: Si fem "python-qgis-ltr.bat moduls/QvCSV.py", QvCSV.py hauria de treballar al directori arrel, però treballa al directori moduls
@REM I això fa que si fem "import moduls.X", falli
@REM A partir de QGIS 3.16 LTR es pot canviar aquest arxiu per fer directament:
@REM set PATH_QGIS="C:\OSGeo4W\bin"
@REM pushd "../"
@REM "%PATH_QGIS%/python_qgis_ltr.bat" "%CD%/moduls/QvCSV.py" %*
@REM popd

set PATH_QGIS="C:\OSGeo4W\bin"

pushd "../"

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
"%PYTHONHOME%\python" "%CD%/moduls/QvCSV.py" %*
popd