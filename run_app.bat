@echo off
echo Instalando dependencias necesarias (esto solo pasa la primera vez o si hay cambios)...
pip install -r requirements.txt

echo.
echo Iniciando la aplicacion...
streamlit run src/app.py
pause
