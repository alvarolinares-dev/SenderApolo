#!/bin/bash

# Obtener la ruta del directorio donde está este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "======================================================="
echo "   CONFIGURACION AUTOMATICA (MAC) - SENDER BOLETIN"
echo "======================================================="

# 1. Verificar si Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] No se encuentra 'python3'."
    echo "Por favor, ejecuta el archivo 'descargar_python_mac.command' primero."
    exit 1
fi

# 2. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "[INFO] Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Falló al crear el entorno virtual."
        exit 1
    fi
    echo "[OK] Entorno virtual creado."
fi

# 3. Activar entorno e instalar dependencias
echo "[INFO] Activando entorno y verificando librerías..."
source venv/bin/activate

# Actualizar pip
echo "[INFO] Actualizando PIP..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Instalar dependencias
echo "[INFO] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Falló al instalar las dependencias. Revisa tu internet."
    exit 1
fi
echo "[OK] Dependencias instaladas."

# 4. Iniciar la aplicación
echo ""
echo "======================================================="
echo "   INICIANDO LA APLICACION"
echo "======================================================="
echo ""
echo "Si te pide permisos de Accesibilidad/Pantalla, DASELOS."
echo "Son necesarios para controlar el mouse en WhatsApp."
echo ""

python -m streamlit run src/app.py
