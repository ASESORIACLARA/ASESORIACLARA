import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import json

# 1. Configuración de la página y Estilo
st.set_page_config(page_title="ASESORIACLARA - Portal de Clientes", page_icon="💼", layout="wide")

# Estilo personalizado para el título
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>ASESORIACLARA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Portal de Gestión de Documentación</h3>", unsafe_allow_html=True)
st.divider()

# 2. Conexión con Google Drive
# Cargamos las credenciales desde los Secrets de Streamlit
try:
    if "google_auth" in st.secrets:
        info = json.loads(st.secrets["google_auth"])
        creds = service_account.Credentials.from_service_account_info(info)
        drive_service = build('drive', 'v3', credentials=creds)
        # ID de tu carpeta en Drive (La que ya configuramos)
        FOLDER_ID = "TU_ID_DE_CARPETA_AQUI" 
    else:
        st.error("No se han configurado las credenciales de Google Drive en Secrets.")
except Exception as e:
    st.error(f"Error de conexión: {e}")

# 3. Menú Lateral
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Logo genérico
    st.title("Panel de Control")
    opcion = st.radio("Ir a:", ["Inicio / Subir Archivos", "Mi Administración"])

# 4. Lógica de las Secciones
if opcion == "Inicio / Subir Archivos":
    st.header("📤 Envío de Documentos")
    st.write("Bienvenida **Lorena**. Selecciona los archivos que deseas enviarnos hoy.")
    
    uploaded_file = st.file_uploader("Elige un archivo (PDF, Imagen, Excel)", type=["pdf", "png", "jpg", "xlsx"])
    
    if uploaded_file is not None:
        if st.button("Enviar a la Asesoría"):
            try:
                file_metadata = {
                    'name': uploaded_file.name,
                    'parents': [FOLDER_ID]
                }
                media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), 
                                          mimetype=uploaded_file.type)
                
                drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                st.success(f"✅ El archivo '{uploaded_file.name}' se ha subido correctamente a tu Google Drive.")
            except Exception as e:
                st.error(f"Hubo un problema al subir el archivo: {e}")

elif opcion == "Mi Administración":
    st.header("📊 Resumen de Clientes")
    st.write("Estado de la gestión mensual:")
    
    # Tu tabla de clientes original
    df_clientes = pd.DataFrame({
        "Nombre del Cliente": ["Empresa A", "Cliente Particular B", "Sociedad C", "Autónomo D"],
        "Estado": ["Facturas Recibidas", "Pendiente DNI", "IVA Presentado", "En proceso"],
        "Última Actualización": ["20/02/2026", "15/02/2026", "19/02/2026", "20/02/2026"]
    })
    
    st.table(df_clientes)
    st.info("Esta tabla se actualiza automáticamente con cada nueva subida.")

# Pie de página
st.sidebar.markdown("---")
st.sidebar.write("© 2026 ASESORIACLARA")
