import pywhatkit
import pandas as pd
import time
import os
import pyautogui
import random
import traceback
from datetime import datetime

def process_newsletter(df, image_path, message_template, log_callback, error_image_path=None):
    """
    Ejecuta la lógica de envío del boletín.
    
    Args:
        df (pd.DataFrame): DataFrame con columnas [Nombre, Telefono]
        image_path (str): Ruta absoluta a la imagen
        message_template (str): Plantilla del mensaje
        log_callback (func): Función para enviar logs a la UI (ej. st.write)
        error_image_path (str, optional): Ruta a la captura de pantalla de error (para detección visual)
    
    Returns:
        dict: Reporte de éxito/error + Lista detallada de envíos.
    """
    
    if not image_path or not os.path.exists(image_path):
        log_callback(f"❌ ERROR: No se encontró la imagen: {image_path}")
        return {"status": "error", "message": "Imagen no encontrada", "details": []}

    log_callback(f"✅ Imagen seleccionada: {image_path}")
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
    
    # Pre-filtering: Clean and remove empty numbers to avoid "ghost" loops
    valid_rows = []
    for index, fila in df.iterrows():
        n = str(fila.iloc[1]).replace("nan", "").replace(".0", "").strip()
        if n:
            valid_rows.append((index, fila))
            
    total_valid = len(valid_rows)
    log_callback(f"ℹ️ Se encontraron {total_valid} contactos válidos de {total} filas.")
    
    # Enable Fail-Safe: Moving mouse to corner will throw exception
    pyautogui.FAILSAFE = True

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

            # Personalización: Reemplazar {Nombre} con el nombre del contacto
            mensaje = message_template.replace("{Nombre}", nombre)

            log_callback("   ⏳ Abriendo WhatsApp...")
            
            try:
                pywhatkit.sendwhats_image(
                    receiver=numero,
                    img_path=image_path,
                    caption=mensaje,
                    wait_time=15, 
                    tab_close=False 
                )
                
                log_callback("   ⏳ Esperando adjunto...")
                time.sleep(3)
                
                # --- VISUAL ERROR CHECK START ---
                error_detected = False
                if error_image_path:
                    try:
                        # Busca la imagen de error en la pantalla
                        # confidence=0.8 ayuda a que sea un poco flexible
                        pos = pyautogui.locateOnScreen(error_image_path, confidence=0.8)
                        if pos:
                            log_callback("   🚨 DETECTADO AVISO DE NÚMERO INVÁLIDO")
                            error_detected = True
                    except Exception as visual_e:
                        # Si falla locateOnScreen (ej. si falta opencv), lo ignoramos
                        log_callback(f"   ⚠️ Falló chequeo visual: {visual_e}")
                
                if error_detected:
                    log_callback("   ❌ Marcando como ERROR (Número inválido o no existe).")
                    errores += 1
                    current_report["Estado"] = "Error"
                    current_report["Detalle"] = "Número Inválido (Visual)"
                    report_details.append(current_report)
                    
                    # Cerrar pestaña del error
                    pyautogui.hotkey('ctrl', 'w')
                    time.sleep(1)
                    continue 
                # --- VISUAL ERROR CHECK END ---
                
                log_callback("   🚀 Enviando (Enter)...")
                pyautogui.press('enter')
                
                time.sleep(2)
                
                log_callback("   ❌ Cerrando pestaña...")
                pyautogui.hotkey('ctrl', 'w')
                
                log_callback("   ✅ Envío completado.")
                exitosos += 1
                
                current_report["Estado"] = "Procesado" # Renamed from Enviado to be safer
                current_report["Detalle"] = "OK"
                report_details.append(current_report)
                
                # Don't sleep after the last one
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
                log_callback(f"   ❌ Error al enviar con PyWhatKit: {e}")
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
