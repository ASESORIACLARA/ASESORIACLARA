import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time

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
    ID_CARPETA_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    DICCIONARIO_CLIENTES = cargar_clientes()

    # --- DISEÑO ---
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

    # --- PESTAÑA GESTIÓN (La movemos arriba para que siempre puedas acceder) ---
    with tab3:
        st.subheader("⚙️ Panel de Control de Administración")
        admin_pass = st.text_input("Introduce la Clave Maestra para gestionar clientes:", type="password", key="admin_panel_pass")
        
        if admin_pass == PASSWORD_ADMIN:
            st.success("✅ Modo Administradora Activo")
            
            # Aquí aparecerá tu lista de clientes y el botón de reset
            if st.button("🔄 CERRAR SESIÓN DE CLIENTE ACTUAL"):
                if "user_email" in st.session_state:
                    del st.session_state["user_email"]
                st.rerun()
            
            st.write("---")
            st.write("### Lista de Clientes Registrados:")
            st.json(DICCIONARIO_CLIENTES)
        else:
            if admin_pass:
                st.error("Contraseña de administración incorrecta")

    # --- LÓGICA DE CLIENTE ---
    with tab1:
        if "user_email" not in st.session_state:
            st.info("👋 Por favor, identifícate en esta pestaña para subir archivos.")
            email_input = st.text_input("Introduce tu correo electrónico:")
            if st.button("ACCEDER A MI CARPETA"):
                if email_input.lower() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = email_input.lower()
                    st.rerun()
                else:
                    st.error("🚫 Correo no registrado.")
        else:
            # Si hay cliente, mostramos el formulario de subida
            user_email = st.session_state["user_email"]
            nombre_cli = DICCIONARIO_CLIENTES[user_email]
            st.markdown(f'<div class="user-info">Sesión iniciada como: {nombre_cli}</div>', unsafe_allow_html=True)
            
            # (Aquí va tu formulario de seleccionar año, trimestre y el botón de subir...)
            col1, col2 = st.columns(2)
            ano_sel = col1.selectbox("Año", [str(datetime.now().year), "2025"])
            trim_sel = col2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            archivo = st.file_uploader("Arrastra tu factura", type=['pdf', 'jpg', 'png'])
            
            if archivo and st.button("🚀 SUBIR"):
                # ... lógica de subida a Drive ...
                st.success("¡Subido!")

