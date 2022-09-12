@REM Batch per cridar el geocodificador si tenim instal·lat QGIS al directori D:\OSGeo4W64
@REM Exemple de crida:
@REM geocodifica_osgeo_D.bat "RUTA_CSV.csv" --codi-barri Codi_barri --via Nom_via --num Numero_via --tipus-via Tipus_via --sortida "RUTA_CSV_SORTIDA.csv"
@REM Més informació:
@REM    geocodifica_osgeo_D.bat --help

@echo off
set PATH_QGIS_BIN="D:\OSGeo4W64\bin"
call qMaBIM_aux.bat %*