import streamlit as st
import os, pickle, json, io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

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
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(diccionario):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

    # --- DISEÑO DEL ENCABEZADO (TU FORMATO FAVORITO) ---
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

    with open('token.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    # --- PESTAÑA 3: GESTIÓN ---
    with tab3:
        st.subheader("⚙️ Panel de Gestión")
        ad_pass = st.text_input("Clave Maestra:", type="password", key="adm_key")
        if ad_pass == PASSWORD_ADMIN:
            st.success("Acceso Administradora")
            col_a, col_b = st.columns(2)
            n_em = col_a.text_input("Email Gmail:")
            n_no = col_b.text_input("Nombre Carpeta:")
            if st.button("REGISTRAR CLIENTE"):
                if n_em and n_no:
                    DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success("¡Registrado!")
                    st.rerun()
            
            st.write("### 👥 Clientes Actuales")
            for email, nombre in list(DICCIONARIO_CLIENTES.items()):
                c_i, c_d = st.columns([3, 1])
                c_i.write(f"**{nombre}** ({email})")
                if c_d.button("ELIMINAR", key=f"del_{email}"):
                    del DICCIONARIO_CLIENTES[email]
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.rerun()

    # --- LÓGICA DE USUARIO ---
    if "user_email" not in st.session_state:
        with tab1:
            st.info("👋 Identifícate con tu correo para empezar.")
            em_log = st.text_input("Correo electrónico:")
            if st.button("ACCEDER AL PORTAL"):
                if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = em_log.lower().strip()
                    st.rerun()
                else: st.error("No registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]



