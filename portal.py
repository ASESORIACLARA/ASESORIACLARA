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

    # --- IDENTIFICACIÓN CORREGIDA ---
    # Usamos st.experimental_user o st.user según la versión, pero con seguridad
    user_email = None
    try:
        if hasattr(st, "user") and st.user.get("email"):
            user_email = st.user.email
        elif hasattr(st, "experimental_user") and st.experimental_user.get("email"):
            user_email = st.experimental_user.email
    except:
        pass

    # Si Streamlit Cloud no detecta el email, pedimos que inicien sesión
    if not user_email:
        st.set_page_config(page_title="Portal ASESORIACLARA", page_icon="⚖️", layout="centered")
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.warning("⚠️ Para identificar tus carpetas, por favor haz clic en 'Sign in with Google' en la barra lateral o en el menú superior de Streamlit.")
        st.info("Nota: Una vez que inicies sesión con Google, el portal reconocerá automáticamente tus facturas.")
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
        .stButton>button { background-color: #1e3a8a; color: white; border-radius: 8px; height: 3em; transition: 0.3s; border: none; }
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
        st.error(f"🚫 El correo **{user_email}** no está registrado. Contacta con la gestoría.")
        st.stop()

    # --- CONEXIÓN DRIVE ---
    if not os.path.exists('token.pickle'):
        st.error("⚠️ Error: Archivo 'token.pickle' no encontrado.")
        st.stop()

    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    service = build('drive', 'v3', credentials=creds)

    st.markdown(f"""
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
            <p>Tu gestión, más fácil y transparente</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

    with tab1:
        nombre_cli = DICCIONARIO_CLIENTES[user_email]
        st.success(f"Hola, **{nombre_cli}**. Ya puedes gestionar tus documentos.")
        # ... (resto de tu código de subida)

