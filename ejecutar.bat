@echo off
title LegadoVivo - Preservacion de Memoria (Kivy Android)
cd /d "%~dp0"
echo ========================================================
echo   Iniciando LegadoVivo (Segundo Incremento Movil)
echo ========================================================
echo.
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error al iniciar la aplicacion.
    pause
)
