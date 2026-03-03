import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN VISUAL Y ESTILOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; color: white; }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .st-rojo { background-color: #ffebee; color: #b71c1c; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #f44336; }
    .st-amarillo { background-color: #fff9c4; color: #827717; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #fbc02d; }
    .st-verde { background-color: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #4caf50; }
    .aviso-caja { padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 6px solid #2196f3; background-color: #f0f7ff; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
DB_F, AV_F = "clientes_db.json", "avisos_db.json"

def load_j(f, d):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as f1: return json.load(f1)
        except: return d
    return d

def save_j(f, d):
    with open(f, "w", encoding="utf-8") as f1: json.dump(d, f1, indent=4, ensure_ascii=False)

def check_password():
    if "pw_ok" not in st.session_state: st.session_state["pw_ok"] = False
    if st.session_state["pw_ok"]: return True
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Acceso Privado</p></div>', unsafe_allow_html=True)
    pw = st.text_input("Contraseña General:", type="password")
    if st.button("ENTRAR") and pw == "clara2026":
        st.session_state["pw_ok"] = True
        st.rerun()
    return False

# --- 3. LÓGICA PRINCIPAL ---
if check_password():
    ID_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PW_ADM = "GEST_LA_2025"
    D_CLI = load_j(DB_F, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    D_AVI = load_j(AV_F, {})

    if "u_mail" not in st.session_state:
        st.write("### 👋 Bienvenida al Portal")
        em = st.text_input("Introduce tu email registrado:")
        if st.button("ACCEDER") and em.lower().strip() in D_CLI:
            st.session_state["u_mail"] = em.lower().strip()
            st.rerun()
    else:
        mail = st.session_state["u_mail"]
        nom = D_CLI[mail]
        inf = D_AVI.get(mail, {})
        txt_av = inf.get("texto", "Bienvenido/a. Ya puedes subir tus documentos.")
        est_av = inf.get("estado", "Pte de documentación")

        clase_color = "st-rojo"
        if "revisión" in est_av.lower(): clase_color = "st-amarillo"
        elif "presentado" in est_av.lower(): clase_color = "st
