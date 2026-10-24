@echo off
title Vigilante EPP - Apagado
chcp 65001 >nul
cd /d "%~dp0.."

echo.
echo [3/3] Vigilante EPP - Detencion de servicios
echo.
echo ⚙ Cerrando procesos de Streamlit y liberando camara...

taskkill /F /IM streamlit.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo ● Servidor detenido y puertos de red liberados.
echo ● Recursos de camara liberados.
echo ■ El sistema esta completamente apagado.
echo.
timeout /t 2 >nul 2>&1
