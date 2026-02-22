import streamlit as st
import os, pickle, json, io, datetime, pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

ID_ARCHIVO_CLIENTES = "1itfmAyRcHoS32bLf_bJFfoYJ3yW4pbED" 
ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
PASSWORD_ADMIN = "GEST_LA_2025"

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: 2.5rem; font-weight: bold;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña del portal:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

if check_password():
    try:
        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)
    except Exception:
        st.error("Error de conexión con Drive. Verifica token.pickle.")
        st.stop()

    def get_f(n, p):
        q_f = f"name='{n}' and '{p}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        rf = service.files().list(q=q_f).execute().get('files', [])
        if rf: return rf[0]['id']
        return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']

    def listar_archivos_carpeta(folder_id):
        query = f"'{folder_id}' in parents and trashed = false"
        return service.files().list(q=query, fields="files(id, name, webContentLink)").execute().get('files', [])

    def cargar_clientes_drive():
        clis = {"asesoriaclara0@gmail.com": "LORENA ALONSO"}
        try:
            req = service.files().get_media(fileId=ID_ARCHIVO_CLIENTES)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, req)
            done = False
            while not done: _, done = downloader.next_chunk()
            fh.seek(0)
            df = pd.read_csv(fh)
            df.columns = df.columns.str.strip().str.lower()
            for _, r in df.iterrows():
                email = str(r['email']).strip().lower()
                nombre = str(r['nombre']).strip()
                if email and nombre:
                    clis[email] = nombre
        except Exception: pass
        return clis

    def guardar_clientes_drive(dicc):
        df = pd.DataFrame(list(dicc.items()), columns=['email', 'nombre'])
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')
        service.files().update(fileId=ID_ARCHIVO_CLIENTES, media_body=media).execute()

    if 'diccionario' not in st.session_state:
        st.session_state['diccionario'] = cargar_clientes_drive()

    DICCIONARIO_CLIENTES = st.session_state['diccionario']

    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
        .header-box h1 { color: white !important; margin: 0; font-size: 2rem; font-weight: bold; }
        .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 15px; text-align: center; }
        </style>
        <div class="header-box"><h1>ASESORIACLARA</h1></div>
    """, unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenido/a")

