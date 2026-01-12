#!/bin/bash
echo "Instalando dependencias necesarias..."
pip3 install -r requirements.txt

echo ""
echo "Iniciando la aplicación..."
python3 -m streamlit run src/app.py
