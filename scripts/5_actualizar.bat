@echo off
title Vigilante EPP - Actualizador
chcp 65001 >nul
cd /d "%~dp0.."

set "PATH=%PATH%;C:\Program Files\Git\cmd;%LOCALAPPDATA%\Programs\Git\cmd"

echo.
echo Vigilante EPP - Actualizador de Sistema
echo.

git --version >nul 2>&1
if errorlevel 1 (
    echo ▲ [AVISO] Git no detectado en el sistema.
    echo ⚙ Ejecuta scripts\1_instalar.bat para instalarlo y configurarlo automaticamente.
    echo.
    pause
    exit /b 1
)

if not exist ".git" (
    echo ▲ [AVISO] Repositorio Git no inicializado en este directorio.
    echo ⚙ Vinculando con el repositorio remoto...
    git init -q
    git remote add origin https://github.com/FernandoIxquiac/-Proyect_VigilanteEPP_app.git
    git fetch origin main --depth=1 -q
    git branch -M main >nul 2>&1
    git reset --mixed origin/main >nul 2>&1
    git branch -u origin/main main >nul 2>&1
    echo ● Repositorio vinculado correctamente a origin/main.
)

git diff --quiet 2>nul
if errorlevel 1 (
    echo ▲ [AVISO] Tienes cambios locales sin guardar que podrian sobreescribirse.
    set /p local_confirm="Deseas continuar de todas formas? (s/n): "
    if /i not "%local_confirm%"=="s" (
        echo ● Actualizacion cancelada por el usuario.
        echo.
        pause
        exit /b 0
    )
)

echo ⚙ Conectando con GitHub y consultando actualizaciones...
git fetch origin main >nul 2>&1

for /f %%i in ('git rev-list HEAD..origin/main --count 2^>nul') do set COMMITS_BEHIND=%%i

if "%COMMITS_BEHIND%"=="0" (
    echo ● El proyecto ya se encuentra en la version mas reciente.
    echo ■ No hay actualizaciones pendientes.
    echo.
    pause
    exit /b 0
)

echo ● Se detectaron %COMMITS_BEHIND% actualizacion(es) disponible(s).
echo.
echo Cambios a descargar:
git log HEAD..origin/main --oneline -n 10 2>nul
echo.

set /p update_confirm="Deseas descargar e instalar la actualizacion? (s/n): "
if /i not "%update_confirm%"=="s" (
    echo ● Actualizacion cancelada por el usuario.
    echo.
    pause
    exit /b 0
)

echo.
echo ⚙ Descargando actualizacion desde origin/main...
git pull origin main 2>&1

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo actualizar el proyecto. Verifica la conexion a internet.
    pause
    exit /b 1
)

echo ● Codigo actualizado correctamente.

if exist ".venv\Scripts\pip.exe" (
    echo ⚙ Sincronizando dependencias en el entorno virtual...
    .venv\Scripts\pip.exe install -r requirements.txt >nul 2>&1
    echo ● Dependencias sincronizadas.
)

echo.
echo ■ Actualizacion completada con exito.
echo ■ Ejecuta scripts\2_iniciar.bat para usar la nueva version.
echo.
pause
