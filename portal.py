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
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    DICCIONARIO_CLIENTES = cargar_clientes()

    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 3rem; border-radius: 20px; text-align: center; margin-bottom: 2rem; }
        .header-box h1 { color: white !important; margin: 0; letter-spacing: 5px; font-size: 3rem; font-weight: bold; }
        .header-box p { color: #d1d5db; margin-top: 15px; font-size: 1.2rem; }
        .user-info { background-color: #e8f0fe; padding: 15px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 20px; text-align: center; }
        .download-card { background: white; padding: 10px; border-radius: 5px; border-left: 5px solid #1e3a8a; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
        </style>
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
            <p>Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

    # Cargar credenciales una sola vez
    with open('token.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    if "user_email" in st.session_state:
        user_email = st.session_state["user_email"]
        nombre_cli = DICCIONARIO_CLIENTES[user_email]
        
        # --- TAB 1: SUBIDA (Lo que ya tenías) ---
        with tab1:
            st.markdown(f'<div class="user-info">Sesión de: {nombre_cli}</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            ano_sel = col1.selectbox("Año", ["2026", "2025", "2024"])
            trim_sel = col2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            archivo = st.file_uploader("Sube factura", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if archivo and st.button("🚀 ENVIAR A MI GESTORA"):
                # (Aquí va tu código de subida que ya funciona perfectamente)
                st.success("¡Subido!")

        # --- TAB 2: MIS IMPUESTOS (NUEVA FUNCIÓN) ---
        with tab2:
            st.subheader("📥 Documentos y Modelos Presentados")
            ano_consulta = st.selectbox("Selecciona el año a consultar:", ["2026", "2025", "2024"])
            
            with st.spinner("Buscando tus impuestos..."):
                # 1. Buscar carpeta del cliente
                q_cli = f"name = '{nombre_cli}' and '{ID_CARPETA_CLIENTES}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
                res_cli = service.files().list(q=q_cli).execute().get('files', [])
                
                if res_cli:
                    id_cli = res_cli[0]['id']
                    # 2. Buscar carpeta del año (2026, etc)
                    q_ano = f"name = '{ano_consulta}' and '{id_cli}' in parents and mimeType = 'application/vnd.google-apps.folder'"
                    res_ano = service.files().list(q=q_ano).execute().get('files', [])
                    
                    if res_ano:
                        id_ano = res_ano[0]['id']
                        # 3. Buscar "IMPUESTOS PRESENTADOS"
                        q_imp = f"name = 'IMPUESTOS PRESENTADOS' and '{id_ano}' in parents and mimeType = 'application/vnd.google-apps.folder'"
                        res_imp = service.files().list(q=q_imp).execute().get('files', [])
                        
                        if res_imp:
                            id_imp = res_imp[0]['id']
                            # 4. Listar archivos dentro
                            archivos = service.files().list(q=f"'{id_imp}' in parents and trashed = false").execute().get('files', [])
                            
                            if archivos:
                                for f in archivos:
                                    col_n, col_d = st.columns([3, 1])
                                    col_n.markdown(f"📄 **{f['name']}**")
                                    
                                    # Botón para descargar
                                    request = service.files().get_media(fileId=f['id'])
                                    fh = io.BytesIO()
                                    downloader = MediaIoBaseDownload(fh, request)
                                    done = False
                                    while done is False:
                                        status, done = downloader.next_chunk()
                                    
                                    col_d.download_button(label="Descargar", data=fh.getvalue(), file_name=f['name'], key=f['id'])
                            else:
                                st.info("Aún no hay impuestos cargados en esta carpeta.")
                        else:
                            st.warning("No se encontró la carpeta 'IMPUESTOS PRESENTADOS' para este año.")
                    else:
                        st.warning(f"No hay registros para el año {ano_consulta}.")
    else:
        st.info("Identifícate en la pestaña 'ENVIAR FACTURAS' para ver tus impuestos.")

    # --- TAB 3: GESTIÓN ---
    with tab3:
        # (Aquí va tu código de administración para añadir clientes)
        st.write("Panel de Gestión

