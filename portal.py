import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import time

# --- CONFIGURACIÓN MAESTRA ---
ID_CARPETA_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"
PASSWORD_ADMIN = "GEST_LA_2025"  # <--- Esta es tu clave para la pestaña GESTIÓN
DB_FILE = "clientes_db.json"

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal ASESORIACLARA", page_icon="⚖️", layout="centered")

# --- DISEÑO Y ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    
    /* Banner Principal */
    .header-box {
        background-color: #1e3a8a;
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-box h1 {
        color: white !important;
        margin: 0;
        letter-spacing: 3px;
        font-family: 'Verdana', sans-serif;
        font-size: 2.5rem;
    }
    .header-box p {
        color: #d1d5db;
        margin-top: 10px;
        font-size: 1.2rem;
        font-weight: 300;
    }

    /* Botones y Pestañas */
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 8px;
        height: 3em;
        transition: 0.3s;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        color: white;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
def cargar_clientes():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

def guardar_clientes(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

DICCIONARIO_CLIENTES = cargar_clientes()

# --- CONEXIÓN GOOGLE DRIVE ---
if not os.path.exists('token.pickle'):
    st.error("⚠️ Error: Archivo 'token.pickle' no encontrado. Por favor, vincula tu cuenta.")
    st.stop()

with open('token.pickle', 'rb') as token:
    creds = pickle.load(token)
service = build('drive', 'v3', credentials=creds)

# --- CABECERA ---
st.markdown("""
    <div class="header-box">
        <h1>ASESORIACLARA</h1>
        <p>Tu gestión, más fácil y transparente</p>
    </div>
    """, unsafe_allow_html=True)

# --- IDENTIFICACIÓN DE USUARIO ---
user_email = "asesoriaclara0@gmail.com" 

# --- MENÚ DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

# --- TAB 1: SUBIDA DE DOCUMENTOS ---
with tab1:
    if user_email in DICCIONARIO_CLIENTES:
        nombre_cli = DICCIONARIO_CLIENTES[user_email]
        st.info(f"Sesión iniciada como: **{nombre_cli}**")
        
        col1, col2 = st.columns(2)
        ano_sel = col1.selectbox("Selecciona el Año", [str(datetime.now().year), str(datetime.now().year-1)])
        trim_sel = col2.selectbox("Selecciona el Trimestre", ["1T", "2T", "3T", "4T"])
        
        tipo = st.radio("Clasificación del documento:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
        archivo = st.file_uploader("Arrastra aquí tu factura (PDF, JPG o PNG)", type=['pdf', 'jpg', 'png', 'jpeg'])
        
        if archivo and st.button("🚀 SUBIR A ASESORIACLARA"):
            with st.spinner("Procesando envío..."):
                try:
                    q = f"name = '{nombre_cli}' and '{ID_CARPETA_RAIZ}' in parents"
                    res = service.files().list(q=q).execute().get('files', [])
                    
                    if res:
                        id_cli = res[0]['id']
                        
                        def get_id(name, p_id):
                            q_f = f"name='{name}' and '{p_id}' in parents and mimeType='application/vnd.google-apps.folder'"
                            r_f = service.files().list(q=q_f).execute().get('files', [])
                            if r_f: return r_f[0]['id']
                            return service.files().create(body={'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[p_id]}, fields='id').execute()['id']
                        
                        id_ano = get_id(ano_sel, id_cli)
                        id_tipo = get_id(tipo, id_ano)
                        id_trim = get_id(trim_sel, id_tipo)
                        
                        with open(archivo.name, "wb") as f: f.write(archivo.getbuffer())
                        media = MediaFileUpload(archivo.name, resumable=True)
                        service.files().create(body={'name':archivo.name,'parents':[id_trim]}, media_body=media).execute()
                        
                        del media
                        time.sleep(1)
                        try: os.remove(archivo.name)
                        except: pass
                        
                        st.success(f"✅ ¡Perfecto! El archivo se ha guardado en {tipo} > {trim_sel}")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error al subir: {e}")
    else:
        st.warning("⚠️ Este correo electrónico no está registrado en el sistema.")

# --- TAB 2: DESCARGA DE IMPUESTOS ---
with tab2:
    if user_email in DICCIONARIO_CLIENTES:
        nombre_cli = DICCIONARIO_CLIENTES[user_email]
        st.subheader("Documentos presentados por la Gestoría")
        
        q_cli = f"name = '{nombre_cli}' and '{ID_CARPETA_RAIZ}' in parents"
        res_cli = service.files().list(q=q_cli).execute().get('files', [])
        
        if res_cli:
            q_imp = f"name='IMPUESTOS PRESENTADOS' and '{res_cli[0]['id']}' in parents"
            res_imp = service.files().list(q=q_imp).execute().get('files', [])
            
            if res_imp:
                archivos = service.files().list(q=f"'{res_imp[0]['id']}' in parents and trashed=false").execute().get('files', [])
                if archivos:
                    for a in archivos:
                        c1, c2 = st.columns([4, 1])
                        c1.write(f"📄 {a['name']}")
                        if c2.button("Descargar", key=a['id']):
                            req = service.files().get_media(fileId=a['id'])
                            fh = io.BytesIO()
                            downloader = MediaIoBaseDownload(fh, req)
                            done = False
                            while not done: _, done = downloader.next_chunk()
                            st.download_button("Confirmar", fh.getvalue(), file_name=a['name'], key=f"dl_{a['id']}")
                else:
                    st.info("No hay documentos disponibles para descarga en este momento.")
            else:
                st.info("Se creará la carpeta de impuestos en cuanto subamos tu primer modelo.")

# --- TAB 3: GESTIÓN INTERNA (ADMIN) ---
with tab3:
    st.subheader("⚙️ Panel de Control ASESORIACLARA")
    acceso = st.text_input("Clave de Administradora:", type="password")
    
    if acceso == PASSWORD_ADMIN:
        st.success("Acceso Administrador Activo")
        with st.expander("➕ DAR DE ALTA NUEVO CLIENTE"):
            email_n = st.text_input("Correo electrónico del cliente:")
            folder_n = st.text_input("Nombre exacto de su carpeta en Drive:")
            if st.button("Guardar Cliente"):
                if email_n and folder_n:
                    DICCIONARIO_CLIENTES[email_n] = folder_n
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success("✅ Cliente registrado")
                    st.rerun()
        
        st.write("### Clientes Registrados")
        for em, fol in DICCIONARIO_CLIENTES.items():
            col_a, col_b, col_c = st.columns([2, 2, 1])
            col_a.write(em)
            col_b.write(fol)
            if col_c.button("Eliminar", key=f"del_{em}"):
                del DICCIONARIO_CLIENTES[em]
                guardar_clientes(DICCIONARIO_CLIENTES)
                st.rerun()
    elif acceso:
        st.error("Contraseña incorrecta")