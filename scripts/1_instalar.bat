@echo off
title SafeGuard AI - Instalador
chcp 65001 >nul
echo.
echo  ========================================================
echo    1/3  VIGILANTE EPP - INSTALACION DE DEPENDENCIAS
echo  ========================================================
echo.

REM --- Verificar que Python esta instalado ---
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python no encontrado en este equipo.
    echo  Descargalo desde: https://www.python.org/downloads/
    echo  Asegurate de marcar "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

REM --- Verificar que requirements.txt existe ---
if not exist "..\requirements.txt" (
    echo  [ERROR] No se encontro requirements.txt en la raiz del proyecto.
    echo  Asegurate de ejecutar este script desde la carpeta scripts\
    echo.
    pause
    exit /b 1
)

echo  [OK] Python detectado correctamente.
echo.
echo  Instalando librerias desde requirements.txt...
echo  (Esto puede tardar unos minutos la primera vez)
echo.

pip install -r ..\requirements.txt

if errorlevel 1 (
    echo.
    echo  [ERROR] Hubo un problema durante la instalacion.
    echo  Verifica tu conexion a internet e intenta de nuevo.
) else (
    echo.
    echo  ========================================================
    echo    INSTALACION COMPLETADA CON EXITO
    echo    Ejecuta "2_iniciar.bat" para arrancar la aplicacion.
    echo  ========================================================
)
echo.
pause
