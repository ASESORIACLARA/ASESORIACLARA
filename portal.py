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

    st.set_page_config(page_title="Acceso ASESORIACLARA", page_icon="⚖️", layout="centered")
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

# --- 2. PORTAL (SÓLO TRAS LA CONTRASEÑA) ---
if check_password():
    ID_CARPETA_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    # --- CARGAR CLIENTES ---
    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    DICCIONARIO_CLIENTES = cargar_clientes()

    # --- IDENTIFICACIÓN DEL USUARIO ---
    # Si Streamlit no detecta el email automáticamente, lo pedimos amablemente
    user_email = st.session_state.get("user_email")

    if not user_email:
        st.markdown("<h2 style='text-align: center;'>📧 Identificación de Cliente</h2>", unsafe_allow_html=True)
        email_input = st.text_input("Introduce tu correo electrónico para ver tus carpetas:")
        if st.button("VER MIS FACTURAS"):
            if email_input.lower() in DICCIONARIO_CLIENTES:
                st.session_state["user_email"] = email_input.lower()
                st.rerun()
            else:
                st.error("🚫 Este correo no está registrado en el sistema.")
        st.stop()

    # --- SI EL EMAIL ES CORRECTO, CARGAMOS TU DISEÑO ORIGINAL ---
    user_email = st.session_state["user_email"]
    nombre_cli = DICCIONARIO_CLIENTES[user_email]

    st.markdown("""
        <style>
        .header-box { background-color: #1e3a8a; padding: 2.5rem; border-radius: 15px; text-align: center; margin-bottom: 2rem; }
        .header-box h1 { color: white !important; margin: 0; font-size: 2.5rem; }
        .header-box p { color: #d1d5db; margin-top: 10px; }
        </style>
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
            <p>Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

    with tab1:
        st.info(f"Sesión iniciada como: **{nombre_cli}**")
        # Aquí va todo tu código de selección de año, trimestre y el botón de subir...
        # (El mismo que tenías en la primera foto que me mandaste)
        st.write("### Sube tus documentos aquí")
        # ... resto del código ...

