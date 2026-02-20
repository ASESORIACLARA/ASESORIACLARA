import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import time

# --- 1. FUNCIÓN DE SEGURIDAD (EL CERROJO) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if st.session_state["password_correct"]:
        return True

    # Configuración de página CENTRADA para el login
    st.set_page_config(page_title="Acceso ASESORIACLARA", page_icon="⚖️", layout="centered")

    # Pantalla de inicio de sesión con tu estilo azul
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

# --- 2. TU PORTAL ORIGINAL (SÓLO SE MUESTRA SI LA CLAVE ES CORRECTA) ---
if check_password():
    # --- CONFIGURACIÓN MAESTRA ---
    ID_CARPETA_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    # Forzamos que el contenido del portal también esté CENTRADO (no expandido)
    # st.set_page_config ya se llamó arriba, Streamlit mantendrá el layout="centered"

    # --- DISEÑO Y ESTILOS CSS ORIGINALES ---
    st.markdown("""
        <style>
        .main { background-color: #fcfcfc; }
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
        .stButton>button {
            background-color: #1e3a8a;
            color: white;
            border-radius: 8px;
            height: 3em;
            transition: 0.3s;
            border: none;
            width: 100%;
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

    # Funciones de carga de datos
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
        st.error("⚠️ Error: Archivo 'token.pickle' no encontrado en el repositorio.")
        st.stop()

    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    service = build('drive', 'v3', credentials=creds)

    # --- CABECERA DEL PORTAL ---
    st.markdown("""
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
            <p>Tu gestión, más fácil y transparente</p>
        </div>
        """, unsafe_allow_html=True)

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

