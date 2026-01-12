@echo off
echo =======================================================
echo    DESCARGANDO PYTHON 3.11 (VERSION CORRECTA)
echo =======================================================
echo.
echo No cierres esta ventana... descargando el instalador...
echo.

REM Download Python 3.11.9 directly
curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

if %errorlevel% neq 0 (
    echo [ERROR] No se pudo descargar. Verifica tu internet.
    pause
    exit /b
)

echo.
echo [OK] Descarga completada.
echo.
echo =======================================================
echo    IMPORTANTE: AL INSTALAR
echo =======================================================
echo.
echo 1. Se abrira una ventana de intalacion.
echo 2. >>> MARCA LA CASILLA "Add python.exe to PATH" <<< (Esta abajo).
echo 3. Dale click a "Install Now".
echo.
echo Presiona una tecla para lanzar el instalador...
pause

start python_installer.exe

echo.
echo Cuando termines de instalar Python, cierra esta ventan y ejecuta 'iniciar_programa.bat'.
pause
