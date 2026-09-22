@echo off
rem ---------------------------------------------------------------
rem  CUADRAR - ECI (Mirakl) vs Business Central
rem  Doble clic: coge el "Mirakl Orders Import*.xlsx" (log BC) y el
rem  "pedidos*.xlsx" (export Mirakl) mas recientes de esta carpeta
rem  y genera Cuadre_ECI_vs_BC_<periodo>.xlsx (mes anterior al
rem  ultimo del log). Desde cmd: CUADRAR.bat --periodo 2026-09
rem ---------------------------------------------------------------
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Cuadre ECI vs BC
set "PYTHONIOENCODING=utf-8"
set "PY=python"
where python >nul 2>nul || set "PY=py"

set "BC="
for /f "delims=" %%f in ('dir /b /o-d "Mirakl Orders Import*.xlsx" 2^>nul') do if not defined BC set "BC=%%f"
set "MK="
for /f "delims=" %%f in ('dir /b /o-d "pedidos*.xlsx" 2^>nul') do if not defined MK set "MK=%%f"

if not defined BC ( echo No encuentro ningun "Mirakl Orders Import*.xlsx" en esta carpeta. & pause & exit /b 1 )
if not defined MK ( echo No encuentro ningun "pedidos*.xlsx" en esta carpeta. & pause & exit /b 1 )

echo ==================================================
echo   CUADRE ECI (MIRAKL) vs BC   %DATE% %TIME:~0,5%
echo   Log BC:        %BC%
echo   Export Mirakl: %MK%
echo ==================================================
echo.
%PY% cuadre_eci_bc.py --bc "%BC%" --mirakl "%MK%" %*
if errorlevel 1 (
    echo.
    echo *** ERROR: el cuadre no se ha completado. Revisa el mensaje de arriba. ***
    echo.
    pause
    exit /b 1
)
echo.
for /f "delims=" %%f in ('dir /b /o-d "Cuadre_ECI_vs_BC_*.xlsx" 2^>nul') do (
    echo Se abre %%f
    start "" "%%f"
    goto :fin
)
:fin
echo.
echo Hecho. Puedes cerrar esta ventana.
pause >nul
endlocal
