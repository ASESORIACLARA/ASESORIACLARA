import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
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

    if "user_email" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>📧 Identificación de Cliente</h2>", unsafe_allow_html=True)
        email_input = st.text_input("Introduce tu correo electrónico:")
        if st.button("ACCEDER A MIS FACTURAS"):
            if email_input.lower() in DICCIONARIO_CLIENTES:
                st.session_state["user_email"] = email_input.lower()
                st.rerun()
            else:
                st.error("🚫 Este correo no está registrado.")
        st.stop()

    user_email = st.session_state["user_email"]
    nombre_cli = DICCIONARIO_CLIENTES[user_email]

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

    with tab1:
        st.markdown(f'<div class="user-info">Sesión iniciada como: {nombre_cli}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        ano_sel = col1.selectbox("Año", [str(datetime.now().year), "2025", "2024"])
        trim_sel = col2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
        tipo = st.radio("Tipo de factura:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
        archivo = st.file_uploader("Sube tu archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
        
        if archivo and st.button("🚀 SUBIR AHORA"):
            try:
                # 1. CONEXIÓN
                if not os.path.exists('token.pickle'):
                    st.error("Archivo token.pickle no encontrado.")
                    st.stop()
                with open('token.pickle', 'rb') as t:
                    creds = pickle.load(t)
                service = build('drive', 'v3', credentials=creds)

                with st.spinner("Conectando con Drive..."):
                    # 2. BUSCAR CARPETA DEL CLIENTE
                    q = f"name = '{nombre_cli}' and '{ID_CARPETA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder'"
                    res = service.files().list(q=q).execute().get('files', [])
                    
                    if not res:
                        st.error(f"No se encontró la carpeta '{nombre_cli}' en Google Drive. Verifica el nombre.")
                    else:
                        id_cli = res[0]['id']

                        def get_or_create(name, parent):
                            query = f"name='{name}' and '{parent}' in parents and mimeType='application/vnd.google-apps.folder'"
                            folders = service.files().list(q=query).execute().get('files', [])
                            if folders: return folders[0]['id']
                            return service.files().create(body={'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[parent]}, fields='id').execute()['id']

                        # 3. CREAR RUTA
                        id_ano = get_or_create(ano_sel, id_cli)
                        id_tipo = get_or_create(tipo, id_ano)
                        id_trim = get_or_create(trim_sel, id_tipo)

                        # 4. SUBIR
                        with open(archivo.name, "wb") as f:
                            f.write(archivo.getbuffer())
                        
                        media = MediaFileUpload(archivo.name, resumable=True)
                        service.files().create(body={'name':archivo.name, 'parents':[id_trim]}, media_body=media).execute()
                        
                        os.remove(archivo.name)
                        st.success("¡Archivo subido con éxito!")
                        st.balloons()
            except Exception as e:
                st.error(f"Error al subir: {e}")

    # Pestaña gestión
    with tab

