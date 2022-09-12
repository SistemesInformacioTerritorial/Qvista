@echo off
set PATH_QGIS_BIN=C:\OSGeo4W\bin
pushd "../"
call python_env.bat
"%PYTHONHOME%\python" "%CD%/moduls/QvCSV.py" %*
popd