@echo off
rem ---------------------------------------------------------------
rem  CUADRAR - ChannelEngine vs Business Central
rem  Doble clic: coge el Cruce_pedidos_*.xlsx (log BC) y el
rem  orders-report*.csv (export CE) mas recientes de esta carpeta
rem  y genera Cuadre_CE_vs_BC_<periodo>.xlsx.
rem  Desde cmd se pueden anadir opciones: CUADRAR.bat --periodo 2026-09
rem ---------------------------------------------------------------
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Cuadre ChannelEngine vs BC
set "PYTHONIOENCODING=utf-8"
set "PY=python"
where python >nul 2>nul || set "PY=py"

set "BC="
for /f "delims=" %%f in ('dir /b /o-d "Cruce_pedidos_*.xlsx" 2^>nul') do if not defined BC set "BC=%%f"
set "CE="
for /f "delims=" %%f in ('dir /b /o-d "orders-report*.csv" 2^>nul') do if not defined CE set "CE=%%f"

if not defined BC ( echo No encuentro ningun Cruce_pedidos_*.xlsx en esta carpeta. & pause & exit /b 1 )
if not defined CE ( echo No encuentro ningun orders-report*.csv en esta carpeta. & pause & exit /b 1 )

echo ==================================================
echo   CUADRE CHANNELENGINE vs BC   %DATE% %TIME:~0,5%
echo   Log BC:    %BC%
echo   Export CE: %CE%
echo ==================================================
echo.
%PY% cuadre_ce_bc.py --bc "%BC%" --ce "%CE%" %*
if errorlevel 1 (
    echo.
    echo *** ERROR: el cuadre no se ha completado. Revisa el mensaje de arriba. ***
    echo.
    pause
    exit /b 1
)
echo.
for /f "delims=" %%f in ('dir /b /o-d "Cuadre_CE_vs_BC_*.xlsx" 2^>nul') do (
    echo Se abre %%f
    start "" "%%f"
    goto :fin
)
:fin
echo.
echo Hecho. Puedes cerrar esta ventana.
pause >nul
endlocal
