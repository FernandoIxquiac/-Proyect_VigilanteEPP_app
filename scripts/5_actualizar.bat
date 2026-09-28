@echo off
title Vigilante EPP - Actualizador
chcp 65001 >nul
cd ..

echo.
echo  ================================================================
echo    VIGILANTE EPP - ACTUALIZADOR AUTOMATICO
echo    Descarga la ultima version del proyecto desde GitHub
echo  ================================================================
echo.

REM --- Verificar que git esta instalado ---
git --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git no esta instalado en este equipo.
    echo  Descargalo desde: https://git-scm.com/
    echo.
    pause
    exit /b 1
)

REM --- Verificar que es un repositorio git ---
if not exist ".git" (
    echo  [ERROR] Esta carpeta no es un repositorio Git.
    echo  Clona el proyecto primero con:
    echo  git clone https://github.com/FernandoIxquiac/-Proyect_VigilanteEPP_app.git
    echo.
    pause
    exit /b 1
)

REM --- Verificar si hay cambios locales sin guardar ---
git diff --quiet 2>nul
if errorlevel 1 (
    echo  [AVISO] Tienes cambios locales que podrian perderse.
    echo.
    set /p local_confirm="  Deseas continuar de todas formas? (s/n): "
    if /i not "%local_confirm%"=="s" (
        echo.
        echo  Actualizacion cancelada. Guarda tus cambios primero.
        echo.
        pause
        exit /b 0
    )
)

echo  Conectando con GitHub...
echo.

REM --- Obtener y mostrar cambios disponibles ---
git fetch origin main >nul 2>&1

for /f %%i in ('git rev-list HEAD..origin/main --count 2^>nul') do set COMMITS_BEHIND=%%i

if "%COMMITS_BEHIND%"=="0" (
    echo  [OK] Ya tienes la version mas reciente del proyecto.
    echo  No hay actualizaciones disponibles.
    echo.
    pause
    exit /b 0
)

echo  Se encontraron %COMMITS_BEHIND% actualizacion(es) disponible(s).
echo.
echo  Cambios que se descargaran:
echo  ----------------------------------------------------------------
git log HEAD..origin/main --oneline 2>nul
echo  ----------------------------------------------------------------
echo.

set /p update_confirm="  Deseas actualizar ahora? (s/n): "
if /i not "%update_confirm%"=="s" (
    echo.
    echo  Actualizacion cancelada.
    echo.
    pause
    exit /b 0
)

echo.
echo  Descargando actualizacion...
git pull origin main 2>&1

if errorlevel 1 (
    echo.
    echo  [ERROR] No se pudo actualizar el proyecto.
    echo  Verifica tu conexion a internet e intenta de nuevo.
) else (
    echo.
    echo  ================================================================
    echo    PROYECTO ACTUALIZADO CORRECTAMENTE
    echo    Ejecuta "2_iniciar.bat" para usar la nueva version.
    echo  ================================================================
)
echo.
pause
