@REM Batch per cridar el geocodificador si tenim instal·lat QGIS al directori C:\Program Files\QGIS 3.4\
@REM Exemple de crida:
@REM geocodifica_distribuit-3-4.bat "RUTA_CSV.csv" --codi-barri Codi_barri --via Nom_via --num Numero_via --tipus-via Tipus_via --sortida "RUTA_CSV_SORTIDA.csv"
@REM Més informació:
@REM    geocodifica_distribuit-3-4.bat --help

@echo off
set PATH_QGIS="C:\Program Files\QGIS 3.4\bin"
call geocodifica_aux.bat %*