@echo off
title Vigilante EPP - Apagando...
chcp 65001 >nul
cd /d "%~dp0.."
echo.
echo  ========================================================
echo    3/3  VIGILANTE EPP - APAGADO SEGURO
echo  ========================================================
echo.
echo  Cerrando servidor Streamlit y liberando camara...
echo.

taskkill /F /IM streamlit.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo  [OK] Servidor detenido.
echo  [OK] Camara liberada.
echo.
echo  ========================================================
echo    El sistema esta completamente apagado.
echo  ========================================================
echo.
timeout /t 2 >nul
