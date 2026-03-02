"""
TEST DE FLUJO MAC - Ejecutar en la Mac desde terminal:
    python3 test_mac_flow.py

Simula el envío de 2 mensajes de prueba para verificar que el flujo
multi-mensaje funciona correctamente en Mac.
"""

import time
import platform
import webbrowser
import pyperclip
import pyautogui

# --- CONFIGURACIÓN ---
NUMBER_1 = "+51999000001"  # <= Cambia por un número real tuyo para probar
NUMBER_2 = "+51999000002"  # <= Cambia por un segundo número tuyo
WAIT_FOR_LOAD = 15         # Segundos de espera para la carga (reducido para testing rápido)
# ---------------------

is_mac = platform.system() == 'Darwin'
print(f"[INFO] Sistema detectado: {platform.system()}")
print(f"[INFO] ¿Es Mac? {'SI' if is_mac else 'NO'}")

if not is_mac:
    print("[AVISO] Este script está hecho para ejecutarse en Mac.")
    print("[AVISO] Ejecutándolo de todas formas para ver el flujo...")

def log(msg):
    print(f"  {msg}")

def test_send_cycle(numero, label):
    print(f"\n{'='*50}")
    print(f"CICLO: {label} — {numero}")
    print(f"{'='*50}")

    # Paso 1: Abrir WhatsApp
    url = f"https://web.whatsapp.com/send?phone={numero}"
    log(f"[1] Abriendo nueva pestaña: {url}")
    webbrowser.open_new_tab(url)

    # Paso 2: Esperar carga
    log(f"[2] Esperando {WAIT_FOR_LOAD}s para que cargue WhatsApp...")
    for s in range(WAIT_FOR_LOAD, 0, -1):
        print(f"       {s}s...", end="\r")
        time.sleep(1)
    print()

    # Paso 3: Pegar texto de prueba (sin archivo para simplificar)
    caption = f"Mensaje de prueba para {label}"
    log(f"[3] Pegando caption al portapapeles...")
    pyperclip.copy(caption)
    pyautogui.hotkey('command', 'v')
    time.sleep(1)

    # Paso 4: Enviar
    log("[4] Presionando Enter para enviar...")
    pyautogui.press('enter')
    time.sleep(5)

    # Paso 5: Navegar a about:blank
    log("[5] Navegando a about:blank (evitar cierre de ventana)...")
    pyautogui.hotkey('command', 'l')
    time.sleep(0.5)
    pyperclip.copy('about:blank')
    pyautogui.hotkey('command', 'v')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(2)

    log(f"[OK] Ciclo '{label}' completado.")

# ---- MAIN ----
print("\n[INICIO] Test de flujo Mac — 2 contactos")
print("[INFO] NO TOQUES el mouse ni el teclado durante el test.")
print("[INFO] FAILSAFE: si necesitas detener, mueve el mouse a la esquina SUPERIOR IZQUIERDA.")
print()
print("Empezando en 5 segundos...")
time.sleep(5)

test_send_cycle(NUMBER_1, "Contacto 1")

ANTISPAM = 8
print(f"\n[ANTISPAM] Esperando {ANTISPAM}s antes del siguiente mensaje...")
for s in range(ANTISPAM, 0, -1):
    print(f"       {s}s...", end="\r")
    time.sleep(1)
print()

test_send_cycle(NUMBER_2, "Contacto 2")

print("\n[FIN] Test completado. Verifica que ambos mensajes fueron enviados.")
