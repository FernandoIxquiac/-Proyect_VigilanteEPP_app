@echo off
title Vigilante EPP - Instalador
chcp 65001 >nul
cd /d "%~dp0.."

echo.
echo [1/3] Vigilante EPP - Aprovisionamiento e instalacion
echo.

set "PY_CMD="

REM Deteccion de Python en el sistema
python --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=python"
    goto :python_ready
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py -3"
    goto :python_ready
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :python_ready
)

if exist "C:\Program Files\Python311\python.exe" (
    set "PY_CMD=C:\Program Files\Python311\python.exe"
    goto :python_ready
)

REM Descarga e instalacion desatendida si Python no esta presente
echo ▲ [AVISO] Python no detectado en el sistema.
echo ⚙ Descargando instalador oficial de Python 3.11.9 (64-bit)...

set "PY_INSTALLER=%TEMP%\python_installer.exe"
set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

where curl.exe >nul 2>&1
if not errorlevel 1 (
    curl.exe -L -o "%PY_INSTALLER%" "%PY_URL%"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%'"
)

if not exist "%PY_INSTALLER%" (
    echo [ERROR] No se pudo descargar el instalador de Python.
    echo Por favor instale Python 3.11 manualmente desde https://www.python.org/
    pause
    exit /b 1
)

echo ⚙ Instalando Python 3.11.9 de forma silenciosa para el usuario...
start /wait "" "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 SimpleInstall=1
if exist "%PY_INSTALLER%" del /f /q "%PY_INSTALLER%" >nul 2>&1

set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not exist "%PY_CMD%" (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=python"
    ) else (
        echo [ERROR] No se pudo localizar Python tras la instalacion.
        pause
        exit /b 1
    )
)

:python_ready
echo ● Python configurado: %PY_CMD%

REM Creacion de entorno virtual .venv
if not exist ".venv\Scripts\python.exe" (
    echo ⚙ Creando entorno virtual .venv en la raiz del proyecto...
    if "%PY_CMD%"=="py -3" (
        py -3 -m venv .venv
    ) else if "%PY_CMD%"=="python" (
        python -m venv .venv
    ) else (
        "%PY_CMD%" -m venv .venv
    )
    if errorlevel 1 (
        echo [ERROR] Fallo al crear el entorno virtual .venv.
        pause
        exit /b 1
    )
) else (
    echo ● Entorno virtual .venv existente.
)

REM Verificacion de requirements.txt
if not exist "requirements.txt" (
    echo [ERROR] No se encontro requirements.txt en la raiz del proyecto.
    pause
    exit /b 1
)

echo ⚙ Actualizando pip dentro del entorno virtual...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Fallo al actualizar pip en el entorno virtual.
    pause
    exit /b 1
)

echo ⚙ Instalando PyTorch CPU optimizado (sin dependencias CUDA)...
.venv\Scripts\pip.exe install torch==2.2.2+cpu torchvision==0.17.2+cpu --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo [ERROR] Fallo al instalar PyTorch CPU.
    pause
    exit /b 1
)

echo ⚙ Instalando librerias del proyecto desde requirements.txt...
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Fallo al instalar las librerias del proyecto.
    pause
    exit /b 1
)

REM Deteccion de Git en el sistema
git --version >nul 2>&1
if errorlevel 1 (
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "PATH=%PATH%;C:\Program Files\Git\cmd"
    )
    if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" (
        set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Git\cmd"
    )
)

git --version >nul 2>&1
if errorlevel 1 (
    echo ▲ [AVISO] Git no detectado en el sistema.
    echo ⚙ Instalando Git para Windows de forma desatendida...
    where winget >nul 2>&1
    if not errorlevel 1 (
        winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
    ) else (
        set "GIT_INSTALLER=%TEMP%\git_installer.exe"
        set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
        where curl.exe >nul 2>&1
        if not errorlevel 1 (
            curl.exe -L -o "%GIT_INSTALLER%" "%GIT_URL%"
        ) else (
            powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%GIT_INSTALLER%'"
        )
        if exist "%GIT_INSTALLER%" (
            start /wait "" "%GIT_INSTALLER%" /VERYSILENT /NORESTART /NOCANCEL /SP-
            if exist "%GIT_INSTALLER%" del /f /q "%GIT_INSTALLER%" >nul 2>&1
        )
    )
    set "PATH=%PATH%;C:\Program Files\Git\cmd;%LOCALAPPDATA%\Programs\Git\cmd"
)

git --version >nul 2>&1
if not errorlevel 1 (
    echo ● Git configurado correctamente.
    if not exist ".git" (
        echo ⚙ Vinculando repositorio Git remoto...
        git init -q
        git remote add origin https://github.com/FernandoIxquiac/-Proyect_VigilanteEPP_app.git
        git fetch origin main --depth=1 -q
        git branch -M main >nul 2>&1
        git reset --mixed origin/main >nul 2>&1
        git branch -u origin/main main >nul 2>&1
        echo ● Repositorio vinculado a origin/main.
    )
) else (
    echo ▲ [AVISO] Git no disponible en la sesion actual.
)

echo.
echo ■ Instalacion completada con exito.
echo ■ Ejecuta scripts\2_iniciar.bat para arrancar la aplicacion.
echo.
pause
