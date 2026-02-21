import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: clamp(1.5rem, 8vw, 2.5rem);">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Introduce la contraseña de acceso</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
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
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(diccionario):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

    st.markdown("""
        <style>
        .header-box { 
            background-color: #223a8e; 
            padding: 1.5rem; 
            border-radius: 20px; 
            text-align: center; 
            margin-bottom: 1rem; 
        }
        .header-box h1 { 
            color: white !important; 
            margin: 0; 
            letter-spacing: 2px; 
            font-size: clamp(1.5rem, 7vw, 2.5rem); 
            font-weight: bold; 
        }
        .user-info { 
            background-color: #e8f0fe; 
            padding: 10px; 
            border-radius: 10px; 
            color: #1e3a8a; 
            font-weight: bold; 
            margin-bottom: 15px; 
            text-align: center; 
            font-size: 0.9rem;
        }
        .justificante { 
            background-color: #dcfce7; 
            color: #166534; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid #166534; 
            margin: 10px 0; 
        }
        [data-testid="stSidebar"] { display: none; }
        </style>
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
        </div>
    """, unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenida al Portal")
        st.info("Introduce tu correo registrado para acceder.")
        c_mail1, c_mail2, c_mail3 = st.columns(
