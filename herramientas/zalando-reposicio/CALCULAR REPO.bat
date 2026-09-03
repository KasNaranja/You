@echo off
rem ---------------------------------------------------------------
rem  CALCULAR REPO - reposicio Zalando
rem  Doble clic: calcula la repo amb la data d'avui i obre l'HTML.
rem  Des de cmd s'hi poden afegir opcions: CALCULAR REPO.bat --mult 2
rem  Variable NOOPEN=1 -> no obre l'HTML al final.
rem ---------------------------------------------------------------
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Calcul reposicio Zalando
set "PYTHONIOENCODING=utf-8"
set "PY=python"
where python >nul 2>nul || set "PY=py"

echo ==================================================
echo   CALCUL REPOSICIO ZALANDO   %DATE% %TIME:~0,5%
echo ==================================================
echo.
%PY% repo_zalando.py %*
if errorlevel 1 (
    echo.
    echo *** ERROR: el calcul no s'ha completat. Revisa el missatge de dalt. ***
    echo.
    pause
    exit /b 1
)

echo.
if "%NOOPEN%"=="1" goto :fi
for /f "delims=" %%f in ('dir /b /o-d "REPO\REPO ZALANDO *.html" 2^>nul') do (
    echo S'obre REPO\%%f
    start "" "REPO\%%f"
    goto :fi
)
:fi
echo.
echo Fet. Pots tancar aquesta finestra.
pause >nul
endlocal
