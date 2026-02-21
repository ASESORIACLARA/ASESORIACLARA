import streamlit as st
import os, pickle, json, io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True

    st.markdown('<div style="background-color:#1e3a8a;padding:2.5rem;border-radius:15px;text-align:center;color:white;"><h1>ASESORIACLARA</h1><p>Contraseña de acceso</p></div>', unsafe_allow_html=True)
    password_input = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR AL PORTAL"):
        if password_input == "clara2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Incorrecta")
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(db):
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

    st.markdown('<div style="background-color:#223a8e;padding:2rem;border-radius:20px;text-align:center;color:white;"><h1>ASESORIACLARA</h1><p>Tu gestión fácil y transparente</p></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

    with open('token.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    # --- TAB GESTIÓN ---
    with tab3:
        st.subheader("⚙️ Administración")
        if st.text_input("Clave Maestra:", type="password", key="adm") == PASSWORD_ADMIN:
            st.write("### Registrar")
            c1, c2 = st.columns(2)
            n_e = c1.text_input("Email:")
            n_n = c2.text_input("Nombre Carpeta:")
            if st.button("REGISTRAR"):
                DICCIONARIO_CLIENTES[n_e.lower().strip()] = n_n
                guardar_clientes(DICCIONARIO_CLIENTES)
                st.rerun()
            st.write("### Bajas")
            for em, nom in list(DICCIONARIO_CLIENTES.items()):
                col_i, col_d = st.columns([3, 1])
                col_i.write(f"👤 {nom}")
                if col_d.button("ELIMINAR", key=f"del_{em}"):
                    del DICCIONARIO_CLIENTES[em]
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.rerun()

    # --- LÓGICA USUARIO ---
    if "user_email" not in st.session_


