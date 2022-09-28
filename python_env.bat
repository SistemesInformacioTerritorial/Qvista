@REM Funcionament per utilitzar aquest script:
@REM 1. donar valor a PATH_QGIS_BIN (si no es fa, per defecte tenim C:/OSGeo4W/bin)
@REM 2. posar-nos al directori des d'on volem executar el script 
@REM 3. cridar aquest arxiu fent call
@REM 4. "%PYTHONHOME%\python" [ARXIU.py] [ARGS]

@REM Això s'utilitza per poder fer els imports dels mòduls de qVista assumint que es fan des de la carpeta arrel
@REM EXMPLE: moduls/QvCSV.bat


if %PATH_QGIS_BIN%=="" set PATH_QGIS_BIN="C:\OSGeo4W\bin"

@REM call C:\OSGeo4W\bin\python-qgis-ltr.bat -c ""
call %PATH_QGIS_BIN%\python-qgis-ltr.bat -c ""
set PYTHONPATH=%CD%;%PYTHONPATH%