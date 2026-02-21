import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Introduce la contraseña de acceso</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR AL PORTAL"):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

if check_password():
    # ID de tu carpeta "01_CLIENTES"
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(diccionario):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 3rem; border-radius: 20px; text-align: center; margin-bottom: 2rem; }
        .header-box h1 { color: white !important; margin: 0; letter-spacing: 5px; font-size: 3rem; font-weight: bold; }
        .header-box p { color: #d1d5db; margin-top: 15px; font-size: 1.2rem; }
        .user-info { background-color: #e8f0fe; padding: 15px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 20px; text-align: center; }
        </style>
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
            <p>Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

    # Carga de credenciales de Google
    with open('token.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    # --- PESTAÑA 3: GESTIÓN (Siempre accesible para ti) ---
    with tab3:
        st.subheader("⚙️ Panel de Control")
        admin_pass = st.text_input("Clave Maestra de Admin:", type="password", key="admin_key")
        if admin_pass == PASSWORD_ADMIN:
            st.success("Acceso Administradora")
            col_a, col_b = st.columns(2)
            n_email = col_a.text_input("Email Gmail del cliente:")
            n_nombre = col_b.text_input("Nombre Carpeta en Drive:")
            if st.button("REGISTRAR NUEVO CLIENTE"):
                if n_email and n_nombre:
                    DICCIONARIO_CLIENTES[n_email.lower().strip()] = n_nombre
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success("Cliente guardado")
                    st.rerun()
            
            st.write("### Clientes:", DICCIONARIO_CLIENTES)
            if st.button("🔄 CERRAR SESIÓN DE CLIENTE"):
                if "user_email" in st.session_state: del st.session_state["user_email"]
                st.rerun()

    # --- LÓGICA DE USUARIO ---
    if "user_email" not in st.session_state:
        with tab1:
            st.info("👋 Identifícate con tu correo para empezar.")
            em = st.text_input("Correo electrónico:")
            if st.button("ACCEDER"):
                if em.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = em.lower().strip()
                    st.rerun()
                else:
                    st.error("Correo no registrado.")
    else:
        user_email = st.session_state["user_email"]
        nombre_cli = DICCIONARIO_CLIENTES[user_email]

        # --- TAB 1: ENVIAR ---
        with tab1:
            st.markdown(f'<div class="user-info">Cliente: {nombre_cli}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            a_sel = c1.selectbox("Año", ["2026", "2025"], key="env_ano")
            t_sel = c2.selectbox("Trimestre", ["1T", "

