@REM Batch per cridar el geocodificador
@REM Exemple de crida:
@REM geocodifica_distribuit.bat "RUTA_CSV.csv" --codi-barri Codi_barri --via Nom_via --num Numero_via --tipus-via Tipus_via --sortida "RUTA_CSV_SORTIDA.csv"
@REM Més informació:
@REM    geocodifica_distribuit.bat --help

@echo off
set PATH_QGIS_BIN="C:\OSGeo4W\bin"
call qMaBIM_aux.bat %*
