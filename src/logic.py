import pywhatkit
import pandas as pd
import time
import os
import pyautogui
import random
import traceback
import platform
import subprocess
import webbrowser
import pyperclip
from datetime import datetime

# Helper para Mac: Copiar archivo al portapapeles
def copy_file_to_clipboard_mac(path):
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"No existe: {abs_path}")
        
    ext = os.path.splitext(abs_path)[1].lower()
    # Determinar tipo de archivo para AppleScript
    if ext == '.png':
        file_type = "«class PNGf»"
    elif ext in ['.jpg', '.jpeg']:
        file_type = "JPEG picture"
    elif ext == '.pdf':
        file_type = "«class PDF »"
    else:
        file_type = "TIFF picture"

    cmd = f'set the clipboard to (read (POSIX file "{abs_path}") as {file_type})'

    try:
        subprocess.run(["osascript", "-e", cmd], check=True)
    except Exception as e:
        # Fallback para archivos generales
        cmd_backup = f'set the clipboard to (POSIX file "{abs_path}")'
        subprocess.run(["osascript", "-e", cmd_backup], check=True)

# Helper para Windows: Copiar archivo al portapapeles (FileDropList)
def copy_file_to_clipboard_win(path):
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"No existe: {abs_path}")
    
    # PowerShell command to set file to clipboard as FileDropList
    ps_command = f'Add-Type -AssemblyName System.Windows.Forms; ' \
                 f'$file = Get-Item "{abs_path}"; ' \
                 f'[System.Windows.Forms.Clipboard]::SetFileDropList([System.Collections.Specialized.StringCollection]@($file.FullName))'
    
    try:
        subprocess.run(["powershell", "-Command", ps_command], check=True)
    except Exception as e:
        print(f"Error Windows Clipboard: {e}")
        raise e

# Función específica para Mac
def send_whatsapp_mac(phone, file_path, caption, log_callback, wait_time=15):
    # 1. Copiar archivo
    log_callback("   🍎 (Mac) Copiando archivo al portapapeles...")
    copy_file_to_clipboard_mac(file_path)
    
    # 2. Abrir WhatsApp Web limpio (solo teléfono)
    log_callback("   🍎 (Mac) Abriendo navegador...")
    url = f"https://web.whatsapp.com/send?phone={phone}"
    webbrowser.open(url)
    
    # 3. Esperar carga
    time.sleep(wait_time)
    
    # 4. Pegar Archivo (Cmd+V)
    log_callback("   🍎 (Mac) Pegando archivo...")
    pyautogui.hotkey('command', 'v')
    time.sleep(3) # Esperar modal de vista previa
    
    # 5. Pegar Caption
    if caption:
        log_callback("   🍎 (Mac) Pegando mensaje...")
        pyperclip.copy(caption)
        pyautogui.hotkey('command', 'v')
        time.sleep(1)

# Función específica para Windows
def send_whatsapp_win(phone, file_path, caption, log_callback, wait_time=15):
    # 1. Copiar archivo
    log_callback("   🪟 (Win) Copiando archivo al portapapeles...")
    copy_file_to_clipboard_win(file_path)
    
    # 2. Abrir WhatsApp Web
    log_callback("   🪟 (Win) Abriendo navegador...")
    url = f"https://web.whatsapp.com/send?phone={phone}"
    webbrowser.open(url)
    
    # 3. Esperar carga
    time.sleep(wait_time)
    
    # 4. Pegar Archivo (Ctrl+V)
    log_callback("   🪟 (Win) Pegando archivo...")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(3) # Esperar modal de vista previa
    
    # 5. Pegar Caption
    if caption:
        log_callback("   🪟 (Win) Pegando mensaje...")
        pyperclip.copy(caption)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)

def process_newsletter(df, file_path, message_template, log_callback, error_image_path=None):
    """
    Ejecuta la lógica de envío del boletín.
    """
    
    if not file_path or not os.path.exists(file_path):
        log_callback(f"❌ ERROR: No se encontró el archivo: {file_path}")
        return {"status": "error", "message": "Archivo no encontrado", "details": []}

    log_callback(f"✅ Archivo seleccionado: {file_path}")
    if error_image_path:
        log_callback(f"✅ Detección visual de errores ACTIVA 📸")
        
    log_callback("🚀 Iniciando envío masivo...")
    log_callback("⚠️  IMPORTANTE: NO TOQUES EL MOUSE NI EL TECLADO.")
    log_callback("⏳ Empezando en 5 segundos...")
    time.sleep(5)
    
    exitosos = 0
    errores = 0
    
    total = len(df)
    report_details = [] 
    
    valid_rows = []
    for index, fila in df.iterrows():
        n = str(fila.iloc[1]).replace("nan", "").replace(".0", "").strip()
        if n:
            valid_rows.append((index, fila))
            
    total_valid = len(valid_rows)
    log_callback(f"ℹ️ Se encontraron {total_valid} contactos válidos de {total} filas.")
    
    pyautogui.FAILSAFE = True
    is_mac = platform.system() == 'Darwin'

    for i, (original_index, fila) in enumerate(valid_rows):
        current_report = {
            "Nombre": str(fila.iloc[0]).replace("nan", "").strip(),
            "Telefono": "",
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Estado": "Pendiente",
            "Detalle": ""
        }
        
        try:
            nombre = str(fila.iloc[0]).replace("nan", "").strip()
            numero = str(fila.iloc[1]).replace("nan", "").replace(".0", "").strip()
            
            if not numero.startswith("+"):
                numero = "+" + numero
            
            current_report["Telefono"] = numero
            log_callback(f"📨 [{i+1}/{total_valid}] Procesando: {nombre} ({numero})")

            mensaje = message_template.replace("{Nombre}", nombre)

            log_callback("   ⏳ Abriendo WhatsApp...")
            
            try:
                if is_mac:
                    # Lógica MacOS
                    send_whatsapp_mac(numero, file_path, mensaje, log_callback, wait_time=15)
                    # Al salir de aquí, estamos en la pantalla de vista previa con texto pegado
                else:
                    # Lógica Windows (Copia-Pega mejorada para PDF/Imagen)
                    send_whatsapp_win(numero, file_path, mensaje, log_callback, wait_time=15)
                
                log_callback("   ⏳ Esperando adjunto/preparación...")
                time.sleep(3)
                
                # --- VISUAL ERROR CHECK START ---
                error_detected = False
                if error_image_path:
                    try:
                        # Busca la imagen de error en la pantalla
                        pos = pyautogui.locateOnScreen(error_image_path, confidence=0.8)
                        if pos:
                            log_callback("   🚨 DETECTADO AVISO DE NÚMERO INVÁLIDO")
                            error_detected = True
                    except Exception as visual_e:
                        log_callback(f"   ⚠️ Falló chequeo visual: {visual_e}")
                
                if error_detected:
                    log_callback("   ❌ Marcando como ERROR (Número inválido o no existe).")
                    errores += 1
                    current_report["Estado"] = "Error"
                    current_report["Detalle"] = "Número Inválido (Visual)"
                    report_details.append(current_report)
                    
                    # Cerrar pestaña del error
                    if is_mac:
                        pyautogui.hotkey('command', 'w')
                    else:
                        pyautogui.hotkey('ctrl', 'w')
                    time.sleep(1)
                    continue 
                # --- VISUAL ERROR CHECK END ---
                
                log_callback("   🚀 Enviando (Enter)...")
                pyautogui.press('enter')
                
                time.sleep(2)
                
                log_callback("   ❌ Cerrando pestaña...")
                if is_mac:
                    pyautogui.hotkey('command', 'w')
                else:
                    pyautogui.hotkey('ctrl', 'w')
                
                log_callback("   ✅ Envío completado.")
                exitosos += 1
                
                current_report["Estado"] = "Procesado"
                current_report["Detalle"] = "OK"
                report_details.append(current_report)
                
                if i < total_valid - 1:
                    segundos_espera = random.randint(8, 15)
                    log_callback(f"   🛡️ Anti-spam: Esperando {segundos_espera}s...")
                    time.sleep(segundos_espera)

            except pyautogui.FailSafeException:
                log_callback("🛑 DETENIDO POR EL USUARIO (Fail-Safe activado).")
                current_report["Estado"] = "Detenido"
                current_report["Detalle"] = "Cancelado manualmente"
                report_details.append(current_report)
                return {"status": "stopped", "enviados": exitosos, "errores": errores, "details": report_details}

            except Exception as e:
                log_callback(f"   ❌ Error al enviar: {e}")
                errores += 1
                current_report["Estado"] = "Error"
                current_report["Detalle"] = str(e)
                report_details.append(current_report)
                traceback.print_exc()

        except Exception as e:
            log_callback(f"❌ Error fila {original_index}: {e}")
            errores += 1
            current_report["Estado"] = "Error Fila"
            current_report["Detalle"] = str(e)
            report_details.append(current_report)

    log_callback(f"\n✅✅ Proceso finalizado. Enviados: {exitosos} | Errores: {errores}")
    return {"status": "finished", "enviados": exitosos, "errores": errores, "details": report_details}
