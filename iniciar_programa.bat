@echo off
setlocal

echo =======================================================
echo    CONFIGURACION AUTOMATICA - SENDER BOLETIN
echo =======================================================

REM 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encuentra el comando 'python'.
    echo Por favor, instala Python desde: https://www.python.org/downloads/
    echo ASEGURATE DE MARCAR LA CASILLA "Add Python to PATH" DURANTE LA INSTALACION.
    echo.
    echo Una vez instalado, cierra esta ventana y vuelve a ejecutar este archivo.
    pause
    exit /b
)

REM 1.5 Ensure PIP is installed (Fix for 'pip not recognized' if python exists)
echo [INFO] Verificando instalacion de PIP...
python -m ensurepip --default-pip >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] No se pudo ejecutar ensurepip, intentando continuar...
)

REM 2. Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Fallo al crear el entorno virtual.
        pause
        exit /b
    )
    echo [OK] Entorno virtual creado.
)

REM 3. Activate virtual environment and install requirements
echo [INFO] Activando entorno y verificando librerias...
call venv\Scripts\activate.bat

REM Update pip and build tools
echo [INFO] Actualizando PIP y herramientas de construccion...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM Install requirements (prefer binaries to avoid compilation errors)
echo [INFO] Instalando dependencias (forzando binarios)...
pip install -r requirements.txt --prefer-binary

if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar las dependencias. Revisa tu conexion a internet.
    pause
    exit /b
)
echo [OK] Streamlit y dependencias instaladas correctamente.

REM 4. Run the application
echo.
echo =======================================================
echo    INICIANDO LA APLICACION
echo =======================================================
echo.
echo Si el navegador no se abre automaticamente, copia la URL que aparece abajo.
echo Para detener la aplicacion, cierra esta ventana.
echo.

python -m streamlit run src/app.py

pause
