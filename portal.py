import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

# --- 2. FUNCIÓN DE SEGURIDAD (ACCESO GENERAL) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Introduce la contraseña de acceso al portal</p>
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

# --- 3. INICIO DEL PORTAL ---
if check_password():
    # Configuración de IDs de Google Drive y Base de Datos
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    # Funciones para manejar la base de datos de clientes
    def cargar_clientes():
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(diccionario):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

    # Estilos CSS personalizados
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

    # Conexión con Google Drive
    try:
        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error("Error crítico: No se encuentra el archivo 'token.pickle'.")
        st.stop()

    # --- PESTAÑA 3: GESTIÓN (ADMINISTRADORA) ---
    with tab3:
        st.subheader("⚙️ Panel de Administración")
        ad_pass = st.text_input("Clave Maestra de Administradora:", type="password", key="adm_key")
        
        if ad_pass == PASSWORD_ADMIN:
            st.success("Acceso Autorizado")
            
            # Registrar nuevos
            st.write("### ➕ Registrar Nuevo Cliente")
            col_a, col_b = st.columns(2)
            n_em = col_a.text_input("Nuevo Email Gmail:")
            n_no = col_b.text_input("Nombre Carpeta Exacto:")
            
            if st.button("REGISTRAR CLIENTE"):
                if n_em and n_no:
                    email_limpio = n_em.lower().strip()
                    DICCIONARIO_CLIENTES[email_limpio] = n_no
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success(f"¡{n_no} guardado!")
                    st.rerun()
            
            st.divider()
            
            # Eliminar clientes existentes
            st.write("### 👥 Gestionar Bajas de Clientes")
            for email, nombre in list(DICCIONARIO_CLIENTES.items()):
                c_info, c_del = st.columns([3, 1])
                c_info.write(f"👤 **{nombre}** ({email})")
                if c_del.button("ELIM

