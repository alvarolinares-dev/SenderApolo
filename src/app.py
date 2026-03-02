import streamlit as st
import pandas as pd
import os
import tempfile
import io
from logic import process_newsletter

# Page Config
st.set_page_config(
    page_title="TechCO Sender",
    page_icon="🟢", # Green circle to match theme
    layout="wide", # Wider layout for table
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'campaign_running' not in st.session_state:
    st.session_state.campaign_running = False
if 'campaign_finished' not in st.session_state:
    st.session_state.campaign_finished = False

# --- CSS personalizado: Estilo TechCO (Dark & Green) ---
# --- CSS personalizado: Ajustes mínimos ---
st.markdown("""
    <style>
    /* Info/Warning Boxes - Hacerlos dinámicos sería ideal, pero por ahora simplificamos */
    .warning-box {
        padding: 15px;
        border-radius: 5px;
        border-left: 6px solid #ffcc00;
        background-color: rgba(255, 204, 0, 0.1);
        color: inherit; 
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* Buttons - Primary Green via config.toml mostly, but force width if needed */
    .stButton>button {
        width: 100%;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("((O)) TECHCO Sender")
st.markdown("Automatización de envíos masivos - **TechCO Edition**")

# --- Warning ---
st.markdown("""
    <div class="warning-box">
        ⚠️ IMPORTANTE: No toques el Mouse ni el Teclado durante el envío.
    </div>
""", unsafe_allow_html=True)

# --- Sidebar (Settings) ---
with st.sidebar:
    # st.image("https://techco.pe/wp-content/uploads/2023/10/logo-techco-blanco-1.png", width=150) # Removed by request
    st.header("Configuración")
    st.info("Asegúrate de tener WhatsApp Web activo.")
    
    # Template Download
    st.subheader("Plantilla")
    plantilla_data = {"Nombre": ["Ejemplo"], "Telefono": ["+51999999999"]}
    df_plantilla = pd.DataFrame(plantilla_data)
    
    @st.cache_data
    def convert_df(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Plantilla')
        return output.getvalue()

    st.download_button(
        label="📥 Descargar Plantilla",
        data=convert_df(df_plantilla),
        file_name="plantilla_contactos.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


# --- Main Form ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Base de Datos")
    uploaded_file = st.file_uploader("Sube tu Excel/CSV", type=["xlsx", "csv"])
    
    df_contactos = None
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_contactos = pd.read_csv(uploaded_file)
            else:
                df_contactos = pd.read_excel(uploaded_file)
            df_contactos = df_contactos.astype(str)
            st.success(f"✅ {len(df_contactos)} Contactos cargados")
            
            # Estimación
            # Tiempo: 15s (ws) + 3s (img) + 2s (send) + 2s (close) + 11s (avg spam) = ~33s
            est_seconds = len(df_contactos) * 35 
            est_minutes = est_seconds // 60
            st.info(f"⏱️ Tiempo estimado: ~{est_minutes} minutos ({est_seconds} s)")
            st.warning("🛑 Para detener el envío de emergencia: Mueve el mouse rápidamente a la esquina superior izquierda de tu pantalla.", icon="🛑")
        except Exception as e:
            st.error(f"Error: {e}")

    st.subheader("2. Archivo (Imagen o PDF)")
    uploaded_file = st.file_uploader("Imagen o PDF para enviar", type=["png", "jpg", "jpeg", "pdf"])
    
    # Removed Error Uploader as it is now auto-detected from src/assets/error_popup.png

with col2:
    st.subheader("3. Mensaje")
    default_message = """¡Hola {Nombre}!

Esperamos que hayas tenido un excelente inicio de año.✨

Te compartimos nuestra actualización quincenal de noticias. En esta ocasión, destacamos el análisis de nuestro co-fundador sobre el futuro de la banca alternativa y su impacto en el país.

Consulta la nota completa en: https://www.infobae.com/peru/2025/12/31/fintech-y-desarrollo-economico-una-oportunidad-que-el-peru-no-debe-dejar-pasar/

Saludos,
Relaciones Institucionales Capitalia.

　 Si deseas dejar de recibir este boletín, por favor háznoslo saber."""
    
    message_text = st.text_area("Cuerpo del mensaje", value=default_message, height=250)


# --- Execution ---
st.divider()

if st.button("🚀 INICIAR CAMPAÑA"):
    if df_contactos is None:
        st.error("❌ Faltan contactos.")
    elif not uploaded_file:
        st.error("❌ Falta el archivo (Imagen o PDF).")
    elif not message_text.strip():
        st.error("❌ Falta el mensaje.")
    else:
        # Save file with ORIGINAL NAME to a temporary directory
        # This ensures WhatsApp shows the real filename instead of 'tmpXYZ.pdf'
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Reset state
        st.session_state.campaign_running = True
        st.session_state.campaign_finished = False
        
        # Log area
        log_container = st.empty()
        
        def update_log(msg):
            log_container.code(msg, language="bash")
            print(msg) 

        # Auto-detect error image from assets
        temp_error_path = None
        default_error_asset = os.path.join("src", "assets", "error_popup.png")
        
        if os.path.exists(default_error_asset):
            temp_error_path = default_error_asset

        try:
            with st.spinner('Enviando mensajes...'):
                result = process_newsletter(
                    df_contactos, 
                    temp_file_path, 
                    message_text, 
                    update_log,
                    error_image_path=temp_error_path
                )
                st.session_state.campaign_running = False
                st.session_state.campaign_finished = True
            
            # --- Results Report ---
            if result["status"] == "finished":
                st.balloons()
                st.markdown("## 📊 Reporte de Resultados")
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Enviados", result["enviados"], delta_color="normal")
                m2.metric("Errores", result["errores"], delta_color="inverse")
                m3.metric("Total Procesados", len(df_contactos))
                
                # Detail Table
                if result.get("details"):
                    df_report = pd.DataFrame(result["details"])
                    
                    # Highlight errors
                    def highlight_status(val):
                        if val == 'Error' or val == 'Saltado':
                            return 'background-color: #550000; color: #ffcccc;'
                        elif val == 'Enviado':
                            return 'background-color: #003300; color: #ccffcc;'
                        return ''

                    st.dataframe(df_report.style.applymap(highlight_status, subset=['Estado']), use_container_width=True)
                    
                    # Download Report
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_report.to_excel(writer, index=False, sheet_name='Reporte')
                    excel_report = output.getvalue()
                    
                    st.download_button(
                        label="📥 Descargar Reporte Excel",
                        data=excel_report,
                        file_name=f"reporte_envio_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
        
        except Exception as e:
            st.error(f"Error crítico: {e}")
        
        finally:
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                try:
                    os.remove(temp_error_path)
                except:
                    pass
            st.session_state.campaign_running = False

if st.session_state.campaign_finished:
    st.success("✅ Campaña finalizada con éxito.")
    if st.button("🔄 Iniciar Nueva Campaña"):
        st.session_state.campaign_finished = False
        st.rerun()
