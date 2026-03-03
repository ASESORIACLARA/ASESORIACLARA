import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
    .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px; text-align: center; font-size: 0.9rem; }
    .estado-box { background-color: #fff9c4; padding: 10px; border-radius: 10px; color: #827717; font-weight: bold; margin-bottom: 15px; text-align: center; border: 1px solid #fbc02d; }
    .aviso-rojo { padding: 15px; border-radius: 10px; background-color: #ffebee; border-left: 6px solid #f44336; color: #b71c1c; margin: 10px 0; }
    .aviso-azul { padding: 15px; border-radius: 10px; background-color: #e3f2fd; border-left: 6px solid #2196f3; color: #0d47a1; margin: 10px 0; }
    .aviso-tarea { padding: 15px; border-radius: 10px; background-color: #fff3e0; border-left: 6px solid #ff9800; color: #e65100; margin: 10px 0; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pw = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if pw == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Incorrecta")
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE, AVISOS_FILE = "clientes_db.json", "avisos_db.json"

    def cargar_j(arch, def_v):
        if os.path.exists(arch):
            try:
                with open(arch, "r", encoding="utf-8") as f: return json.load(f)
            except: return def_v
        return def_v

    def guardar_j(arch, datos):
        with open(arch, "w", encoding="utf-8") as f: json.dump(datos, f, indent=4, ensure_ascii=False)

    D_CLI = cargar_j(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    D_AVI = cargar_j(AVISOS_FILE, {})

    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenida al Portal")
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            em = st.text_input("Correo registrado:")
            if st.button("ACCEDER", use_container_width=True):
                if em.lower().strip() in D_CLI:
                    st.session_state["user_email"] = em.lower().strip()
                    st.rerun()
                else: st.error("No registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = D_CLI[email_act]

        c_l1, c_l2 = st.columns([4,1])
        c_l1.markdown(f'<div class="user-info">Sesión: {
