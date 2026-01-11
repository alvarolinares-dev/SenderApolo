import pywhatkit
import pandas as pd
import time
import os
import pyautogui
import traceback
import random

# --- CONFIGURACIÓN ---
BASE_DIR = r"C:\Users\ALVARO\Desktop\sender"
EXCEL_FILE = os.path.join(BASE_DIR, "prueba.xlsx") 

# Detectar imagen (Prioridad)
POSIBLES_IMAGENES = ["Boletin_noticias_CAPITALIA.png"]
IMAGEN_PATH = None

for img_name in POSIBLES_IMAGENES:
    path = os.path.join(BASE_DIR, img_name)
    if os.path.exists(path):
        IMAGEN_PATH = path
        break

if not IMAGEN_PATH:
    print(f"❌ ERROR: No se encontró ninguna imagen en {BASE_DIR}")
    exit()

print(f"✅ Imagen seleccionada: {IMAGEN_PATH}")

# Cargar Excel
try:
    df = pd.read_excel(EXCEL_FILE)
    df = df.astype(str)
except Exception as e:
    print(f"❌ Error leyendo Excel: {e}")
    exit()

print("🚀 Iniciando envío masivo con PyWhatKit...")
print("⚠️  IMPORTANTE: NO TOQUES EL MOUSE NI EL TECLADO MIENTRAS EL SCRIPT CORRE.")
print("⚠️  Asegúrate de tener WhatsApp Web ya iniciado sesión en tu navegador por defecto.")
print("⏳ Empezando en 5 segundos...")
time.sleep(5)

exitosos = 0
errores = 0

for index, fila in df.iterrows():
    try:
        nombre = fila.iloc[0].replace("nan", "").strip()
        numero = fila.iloc[1].replace("nan", "").replace(".0", "").strip()

        if not numero:
            continue

        if not numero.startswith("+"):
            numero = "+" + numero

        print(f"\n--------------------------------------------------")
        print(f"📨 Procesando #{index+1}: {nombre} ({numero})")

        mensaje = f"""¡Hola!

Esperamos que hayas tenido un excelente inicio de año.✨

Te compartimos nuestra actualización quincenal de noticias. En esta ocasión, destacamos el análisis de nuestro co-fundador sobre el futuro de la banca alternativa y su impacto en el país.

Consulta la nota completa en: https://www.infobae.com/peru/2025/12/31/fintech-y-desarrollo-economico-una-oportunidad-que-el-peru-no-debe-dejar-pasar/

Saludos,
Relaciones Institucionales Capitalia.

　 Si deseas dejar de recibir este boletín, por favor háznoslo saber."""

        # Enviar Mensaje + Imagen
        # wait_time: tiempo (segundos) para que cargue WhatsApp Web antes de enviar
        # tab_close: cerrar pestaña después de enviar
        # close_time: tiempo esperar antes de cerrar
        print("   ⏳ Abriendo WhatsApp y adjuntando...")
        
        try:
            pywhatkit.sendwhats_image(
                receiver=numero,
                img_path=IMAGEN_PATH,
                caption=mensaje,
                wait_time=15, # Optimizando tiempo: 15s para cargar (Si tu internet es lento, súbelo a 20)
                tab_close=False 
            )
            
            # Esperamos a que la imagen se procese en el input
            print("   ⏳ Esperando adjunto...")
            time.sleep(3) 
            
            # Forzamos el ENTER para enviar
            print("   🚀 Enviando (Enter)...")
            pyautogui.press('enter')
            
            # Esperamos a que salga el mensaje (Tic gris/azul)
            time.sleep(2)
            
            # Cerramos la pestaña manualmente
            print("   ❌ Cerrando pestaña...")
            pyautogui.hotkey('ctrl', 'w')
            
            print("   ✅ Envío completado.")
            exitosos += 1
            
            # Pausa aleatoria anti-spam (Entre 8 y 15 segundos)
            segundos_espera = random.randint(8, 15)
            print(f"   🛡️ Anti-spam: Esperando {segundos_espera} segundos antes del siguiente...")
            time.sleep(segundos_espera)

        except Exception as e:
            print(f"   ❌ Error al enviar con PyWhatKit: {e}")
            errores += 1
            # A veces pywhatkit falla al cerrar la pestaña si hubo error
            # Intentamos asegurar que no queden ventanas locas (Opcional)

    except Exception as e:
        print(f"❌ Error procesando fila {index}: {e}")
        errores += 1

print(f"\n✅✅ Proceso finalizado.")
print(f"Enviados: {exitosos} | Errores: {errores}")