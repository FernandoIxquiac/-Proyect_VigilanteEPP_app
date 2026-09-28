@echo off
title Vigilante EPP - Publicar en GitHub
cd /d "%~dp0.."

echo.
echo  ================================================================
echo    4/4  VIGILANTE EPP - PUBLICAR EN GITHUB (Modo Seguro)
echo  ================================================================
echo.

REM ---------------------------------------------------------------
REM  BLOQUE 1: Verificaciones previas
REM ---------------------------------------------------------------

REM Verificar que git esta instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git no esta instalado en este equipo.
    echo  Descargalo desde: https://git-scm.com/
    echo.
    pause
    exit /b 1
)

REM Verificar que existe el repositorio git inicializado
if not exist ".git" (
    echo  [AVISO] Este proyecto no tiene un repositorio Git iniciado.
    echo.
    set /p init_confirm="  Deseas inicializarlo ahora? (s/n): "
    if /i "%init_confirm%"=="s" (
        git init
        git branch -M main
        echo  [OK] Repositorio inicializado.
    ) else (
        echo  Operacion cancelada.
        pause
        exit /b 0
    )
)

REM ---------------------------------------------------------------
REM  BLOQUE 2: Escaneo de seguridad ANTES de hacer git add
REM ---------------------------------------------------------------
echo.
echo  Ejecutando escaneo de seguridad...
echo  ----------------------------------------------------------------

set FOUND_RISK=0

REM Verificar que data/ y captures/ esten blindados en .gitignore
git check-ignore "data/vigilante_epp.db" >nul 2>&1
if errorlevel 1 (
    echo  [ALERTA CRITICA] data/ no esta protegido en .gitignore - Riesgo de fuga de BD
    set FOUND_RISK=1
)
git check-ignore "captures/evidencia.jpg" >nul 2>&1
if errorlevel 1 (
    echo  [ALERTA CRITICA] captures/ no esta protegido en .gitignore - Riesgo de fuga de capturas
    set FOUND_RISK=1
)

REM Verificar que ningun archivo de data/ o captures/ este en el indice de Git (tracked)
for /f "tokens=*" %%i in ('git ls-files "data" "captures" 2^>nul') do (
    echo  [ALERTA CRITICA] Archivo sensible rastreado en Git: %%i
    set FOUND_RISK=1
)

REM Verificar que .gitignore existe
if not exist ".gitignore" (
    echo  [ALERTA] .gitignore no encontrado - Riesgo de subir archivos sensibles
    set FOUND_RISK=1
)

REM Verificar archivos de entorno con posibles credenciales
if exist ".env" (
    echo  [ALERTA] .env detectado - Puede contener claves API o contrasenas
    set FOUND_RISK=1
)
if exist ".streamlit\secrets.toml" (
    echo  [ALERTA] .streamlit\secrets.toml - Contiene credenciales de Streamlit
    set FOUND_RISK=1
)

if "%FOUND_RISK%"=="1" (
    echo.
    echo  ----------------------------------------------------------------
    echo  [!] Se detectaron archivos de riesgo listados arriba.
    echo      Revisalos antes de continuar.
    echo.
    set /p risk_confirm="  Deseas continuar de todas formas? (s/n): "
    if /i not "%risk_confirm%"=="s" (
        echo.
        echo  Publicacion cancelada. Revisa los archivos y vuelve a intentarlo.
        echo.
        pause
        exit /b 0
    )
) else (
    echo  [OK] Escaneo completado. No se detectaron archivos de riesgo.
)

REM ---------------------------------------------------------------
REM  BLOQUE 3: Mostrar preview de cambios antes de confirmar
REM ---------------------------------------------------------------
echo.
echo  ----------------------------------------------------------------
echo  Archivos que se enviaran a GitHub:
echo  ----------------------------------------------------------------
git status --short
echo.

set /p preview_confirm="  Deseas continuar con estos archivos? (s/n): "
if /i not "%preview_confirm%"=="s" (
    echo.
    echo  Publicacion cancelada por el usuario.
    echo.
    pause
    exit /b 0
)

REM ---------------------------------------------------------------
REM  BLOQUE 4: Commit y push
REM ---------------------------------------------------------------
echo.
set /p commit_msg="  Escribe una nota del cambio (Enter = 'Actualizacion del proyecto'): "
if "%commit_msg%"=="" set commit_msg=Actualizacion del proyecto

git add .
git commit -m "%commit_msg%"

if errorlevel 1 (
    echo.
    echo  [INFO] No habia archivos nuevos por confirmar. Continuando con el envio a GitHub...
)

echo.
echo  Enviando cambios a GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo  [ERROR] No se pudo conectar con GitHub.
    echo  Verifica:
    echo    1. Que tienes internet.
    echo    2. Que el repositorio remoto esta configurado:
    echo       git remote add origin https://github.com/TU-USUARIO/REPO.git
    echo.
) else (
    echo.
    echo  ================================================================
    echo    PUBLICADO CON EXITO EN GITHUB
    echo    Commit: "%commit_msg%"
    echo  ================================================================
)
echo.
pause
