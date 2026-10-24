@echo off
title Vigilante EPP - Iniciando...
chcp 65001 >nul
cd /d "%~dp0.."

echo.
echo [2/3] Vigilante EPP - Iniciando aplicacion
echo.

REM Verificacion de existencia de app.py
if not exist "app.py" (
    echo [ERROR] No se encontro app.py en el directorio raiz.
    echo.
    pause
    exit /b 1
)

REM Verificacion de entorno virtual y ejecutable Streamlit
if not exist ".venv\Scripts\streamlit.exe" (
    echo ▲ [AVISO] Entorno virtual o Streamlit no detectado.
    echo ⚙ Ejecuta primero scripts\1_instalar.bat para aprovisionar las dependencias.
    echo.
    pause
    exit /b 1
)

echo ● Entorno virtual .venv validado.
echo ● Iniciando servidor Streamlit...
echo.
echo Telemetria y panel disponibles en:
echo http://localhost:8501
echo.
echo Para apagar la aplicacion:
echo - Presiona Ctrl + C en esta consola, o
echo - Ejecuta scripts\3_apagar.bat
echo.

.venv\Scripts\streamlit.exe run app.py

pause
