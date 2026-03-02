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
    
    # AppleScript: Set the clipboard to the file object itself
    # This ensures WhatsApp sees it as a file, not as raw data (like an image)
    cmd = f'set the clipboard to (POSIX file "{abs_path}")'
    
    try:
        subprocess.run(["osascript", "-e", cmd], check=True)
    except Exception as e:
        print(f"Error Mac Clipboard: {e}")
        raise e

# Helper para Windows: Copiar archivo al portapapeles (FileDropList)
def copy_file_to_clipboard_win(path):
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"No existe: {abs_path}")
    
    # PowerShell command to set file to clipboard as FileDropList (More robust version)
    ps_command = f'Add-Type -AssemblyName System.Windows.Forms; ' \
                 f'$path = [System.IO.Path]::GetFullPath("{abs_path}"); ' \
                 f'$fileList = New-Object System.Collections.Specialized.StringCollection; ' \
                 f'$fileList.Add($path); ' \
                 f'[System.Windows.Forms.Clipboard]::SetFileDropList($fileList)'
    
    try:
        subprocess.run(["powershell", "-Command", ps_command], check=True)
    except Exception as e:
        print(f"Error Windows Clipboard: {e}")
        raise e

# Función específica para Mac
def send_whatsapp_mac(phone, file_path, caption, log_callback, wait_time=20):
    # 1. Copiar archivo
    log_callback("   🍎 (Mac) Copiando archivo al portapapeles...")
    copy_file_to_clipboard_mac(file_path)
    
    # 2. Abrir WhatsApp Web limpio (solo teléfono)
    log_callback("   🍎 (Mac) Abriendo navegador...")
    url = f"https://web.whatsapp.com/send?phone={phone}"
    webbrowser.open(url)
    
    # 3. Esperar carga
    time.sleep(wait_time)
    
    # 3.5 Asegurar foco en navegador para Mac
    log_callback("   🍎 (Mac) Asegurando foco en navegador...")
    pyautogui.click(x=pyautogui.size().width // 2, y=200) # Clic en la parte superior del navegador
    time.sleep(1)
    
    # 4. Pegar Archivo (Cmd+V)
    log_callback("   🍎 (Mac) Pegando archivo...")
    pyautogui.hotkey('command', 'v')
    time.sleep(4) # Esperar modal de vista previa
    
    # 5. Pegar Caption
    if caption:
        log_callback("   🍎 (Mac) Pegando mensaje...")
        pyperclip.copy(caption)
        pyautogui.hotkey('command', 'v')
        time.sleep(1)

# Función específica para Windows
def send_whatsapp_win(phone, file_path, caption, log_callback, wait_time=20):
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
    time.sleep(4) # Esperar modal de vista previa
    
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
                    send_whatsapp_mac(numero, file_path, mensaje, log_callback, wait_time=20)
                    # Al salir de aquí, estamos en la pantalla de vista previa con texto pegado
                else:
                    # Lógica Windows (Copia-Pega mejorada para PDF/Imagen)
                    send_whatsapp_win(numero, file_path, mensaje, log_callback, wait_time=20)
                
                # --- ESPERA DINÁMICA SEGÚN TAMAÑO/TIPO ---
                # Si es un PDF o archivo pesado, necesitamos más tiempo para que cargue
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                wait_extra = 0
                if file_path.lower().endswith('.pdf') or file_size_mb > 5:
                    log_callback(f"   ⏳ Archivo pesado ({file_size_mb:.1f}MB). Esperando carga adicional...")
                    wait_extra = min(int(file_size_mb * 0.5), 15) # Máximo 15 segs extra
                
                log_callback("   ⏳ Esperando adjunto/preparación...")
                time.sleep(3 + wait_extra)
                
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
                
                # Esperamos suficiente para que el mensaje se envíe y desaparezca cualquier modal
                time.sleep(8 + (wait_extra // 2)) 
                
                log_callback("   ❌ Cerrando pestaña...")
                if is_mac:
                    # Mac: Navegar a about:blank en lugar de cerrar la pestaña
                    # Command+W cierra toda la VENTANA en Mac si es la última pestaña,
                    # lo que impide que webbrowser.open() funcione para el siguiente mensaje.
                    log_callback("   🍎 (Mac) Navegando a about:blank (mantener ventana abierta)...")
                    pyautogui.hotkey('command', 'l')  # Foco en barra de URL
                    time.sleep(0.5)
                    pyautogui.typewrite('about:blank', interval=0.02)
                    time.sleep(0.3)
                    pyautogui.press('enter')
                    time.sleep(2)
                else:
                    # Windows: Cerrar pestaña normalmente
                    pyautogui.hotkey('ctrl', 'w')
                    # Failsafe para el aviso "¿Quieres salir del sitio web?" del navegador
                    time.sleep(1)
                    pyautogui.press('enter')
                    time.sleep(1)
                
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
