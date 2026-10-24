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

REM Verificacion de ejecutable Streamlit (.venv prioritario con fallback global)
if exist ".venv\Scripts\streamlit.exe" (
    echo ● Entorno virtual .venv validado.
    echo ● Iniciando servidor Streamlit desde .venv...
    echo.
    echo Telemetria y panel disponibles en:
    echo http://localhost:8501
    echo.
    echo Para apagar la aplicacion:
    echo - Presiona Ctrl + C en esta consola, o
    echo - Ejecuta scripts\3_apagar.bat
    echo.
    .venv\Scripts\streamlit.exe run app.py
) else (
    echo ▲ [AVISO] .venv no detectado o incompleto.
    echo ● Iniciando servidor Streamlit con Python global...
    echo.
    echo Telemetria y panel disponibles en:
    echo http://localhost:8501
    echo.
    echo Para apagar la aplicacion:
    echo - Presiona Ctrl + C en esta consola, o
    echo - Ejecuta scripts\3_apagar.bat
    echo.
    streamlit run app.py
)

pause
