import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import time

# --- 1. FUNCIÓN DE SEGURIDAD Y LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if st.session_state["password_correct"]:
        return True

    st.set_page_config(page_title="Acceso ASESORIACLARA", page_icon="⚖️", layout="centered")

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h1 style="color: white !important; margin: 0; font-family: 'Verdana', sans-serif;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Introduce la contraseña para acceder al portal</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña de acceso:", type="password")
        if st.button("ENTRAR AL PORTAL"):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

# --- 2. INICIO DEL PORTAL ---
if check_password():
    # --- CONFIGURACIÓN MAESTRA ---
    ID_CARPETA_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    # --- IDENTIFICACIÓN REAL DEL USUARIO ---
    # Usamos st.user para detectar el correo de quien inicia sesión en Streamlit
    if st.user.email:
        user_email = st.user.email
    else:
        st.warning("⚠️ Por favor, inicia sesión en Streamlit con tu cuenta de Google arriba a la derecha.")
        st.stop()

    # --- DISEÑO Y ESTILOS CSS ---
    st.markdown("""
        <style>
        .main { background-color: #fcfcfc; }
        .header-box {
            background-color: #1e3a8a; padding: 2.5rem; border-radius: 15px;
            text-align: center; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .header-box h1 { color: white !important; margin: 0; letter-spacing: 3px; font-family: 'Verdana', sans-serif; font-size: 2.5rem; }
        .header-box p { color: #d1d5db; margin-top: 10px; font-size: 1.2rem; font-weight: 300; }
        .stButton>button { background-color: #1e3a8a; color: white; border-radius: 8px; height: 3em; transition: 0.3s; border: none; width: 100%; }
        .stButton>button:hover { background-color: #2563eb; color: white; }
        .stTabs [data-baseweb="tab"] { font-weight: 600; padding: 10px 20px; }
        </style>
        """, unsafe_allow_html=True)

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(data):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

    # --- VERIFICACIÓN DE ACCESO ---
    if user_email not in DICCIONARIO_CLIENTES:
        st.error(f"🚫 El correo **{user_email}** no tiene permiso de acceso. Contacta con la gestoría.")
        st.stop()

    # --- CONEXIÓN GOOGLE DRIVE ---
    if not os.path.exists('token.pickle'):
        st.error("⚠️ Error: Archivo 'token.pickle' no encontrado.")
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

    # --- PESTAÑAS ---
    tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

    with tab1:
        nombre_cli = DICCIONARIO_CLIENTES[user_email]
        st.info(f"Sesión iniciada como: **{nombre_cli}**")
        
        col1, col2 = st.columns(2)
        ano_sel = col1.selectbox("Año", [str(datetime.now().year), str(datetime.now().year-1)])
        trim_sel = col2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
        tipo = st.radio("Clasificación:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
        archivo = st.file_uploader("Sube tu factura", type=['pdf', 'jpg', 'png', 'jpeg'])
        
        if archivo and st.button("🚀 SUBIR A MI CARPETA"):
            with st.spinner("Subiendo..."):
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
                        os.remove(archivo.name)
                        st.success(f"✅ ¡Hecho! Guardado en tu carpeta de {nombre_cli}")
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

    # Pestaña de gestión (solo para ti)
    with tab3:
        st.subheader("⚙️ Panel de Control")
        acceso = st.text_input("Clave de Administradora:", type="password")
        if acceso == PASSWORD_ADMIN:
            st.success("Acceso Administrador")
            # Aquí verás tu lista de clientes y podrás añadir nuevos

