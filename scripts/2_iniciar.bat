@echo off
title Vigilante EPP - Iniciando...
chcp 65001 >nul
cd /d "%~dp0.."

echo.
echo  ========================================================
echo    2/3  VIGILANTE EPP - INICIANDO APLICACION
echo  ========================================================
echo.

REM --- Verificar que app.py existe ---
if not exist "app.py" (
    echo  [ERROR] No se encontro app.py.
    echo.
    pause
    exit /b 1
)

REM --- Verificar que streamlit esta instalado ---
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Streamlit no esta instalado.
    echo  Ejecuta primero "1_instalar.bat" para instalar las dependencias.
    echo.
    pause
    exit /b 1
)

echo  [OK] Todo listo. Iniciando servidor...
echo.
echo  Tu navegador se abrira automaticamente en:
echo  http://localhost:8501
echo.
echo  Para APAGAR la aplicacion:
echo    - Presiona Ctrl + C en esta ventana, o
echo    - Ejecuta "3_apagar.bat"
echo.
echo  ========================================================
echo.

streamlit run app.py

pause
