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
    # --- LA RUTA DE TUS CARPETAS ---
    # ID de la carpeta "01_CLIENTES" (donde están Juan, Javier, etc.)
    # Si no estás segura de este ID, es el que aparece en la URL cuando abres 01_CLIENTES en Drive
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(diccionario):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

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

    # --- PESTAÑA GESTIÓN ---
    with tab3:
        st.subheader("⚙️ Panel de Control de Administración")
        admin_pass = st.text_input("Clave Maestra:", type="password")
        if admin_pass == PASSWORD_ADMIN:
            st.success("✅ Modo Administradora Activo")
            st.write("### ➕ Añadir Nuevo Cliente")
            nuevo_email = st.text_input("Correo Gmail del cliente:").lower().strip()
            nuevo_nombre = st.text_input("Nombre de su carpeta (Ej: JAVIER GARCIA):")
            if st.button("REGISTRAR CLIENTE"):
                if nuevo_email and nuevo_nombre:
                    DICCIONARIO_CLIENTES[nuevo_email] = nuevo_nombre
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success(f"¡{nuevo_nombre} registrado!")
                    st.rerun()
            
            if st.button("🔄 CERRAR SESIÓN DE CLIENTE ACTUAL"):
                if "user_email" in st.session_state: del st.session_state["user_email"]
                st.rerun()

    # --- PESTAÑA ENVÍO ---
    with tab1:
        if "user_email" not in st.session_state:
            st.info("👋 Identifícate para subir archivos.")
            email_acc = st.text_input("Tu correo:")
            if st.button("ACCEDER"):
                if email_acc.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = email_acc.lower().strip()
                    st.rerun()
                else:
                    st.error("🚫 Correo no registrado.")
        else:
            user_email = st.session_state["user_email"]
            nombre_cli = DICCIONARIO_CLIENTES[user_email]
            st.markdown(f'<div class="user-info">Sesión de: {nombre_cli}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            ano_sel = col1.selectbox("Año", ["2026", "2025", "2024"])
            trim_sel = col2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            archivo = st.file_uploader("Sube factura", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if archivo and st.button("🚀 ENVIAR A MI GESTORA"):
                try:
                    with open('token.pickle', 'rb') as t:
                        creds = pickle.load(t)
                    service = build('drive', 'v3', credentials=creds)

                    with st.spinner("Buscando tu carpeta en 01_CLIENTES..."):
                        # BUSCAMOS AL CLIENTE DENTRO DE "01_CLIENTES"
                        query = f"name = '{nombre_cli}' and '{ID_CARPETA_CLIENTES}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
                        res = service.files().list(q=query, fields="files(id, name)").execute().get('files', [])
                        
                        if not res:
                            st.error(f"❌ No encuentro la carpeta '{nombre_cli}' dentro de 01_CLIENTES.")
                        else:
                            id_cli = res[0]['id']

                            def conseguir_id_subcarpeta(nombre, padre_id):
                                q = f"name='{nombre}' and '{padre_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed = false"
                                f_res = service.files().list(q=q, fields="files(id)").execute().get('files', [])
                                if f_res: return f_res[0]['id']
                                return service.files().create(body={'name':nombre,'mimeType':'application/vnd.google-apps.folder','parents':[padre_id]}, fields='id').execute()['id']

                            # Creamos o buscamos: Año -> Tipo -> Trimestre
                            id_ano = conseguir_id_subcarpeta(ano_sel, id_cli)
                            id_tipo = conseguir_id_subcarpeta(tipo, id_ano)
                            id_trim = conseguir_id_subcarpeta(trim_sel, id_tipo)

                            # Subimos el archivo
                            with open(archivo.name, "wb") as f: f.write(archivo.getbuffer())
                            media = MediaFileUpload(archivo.name, resumable=True)
                            service.files().create(body={'name':archivo.name, 'parents':[id_trim]}, media_body=media).execute()
                            os.remove(archivo.name)
                            
                            st.success(f"✅ ¡Hecho! Archivo guardado en la carpeta de {nombre_cli}")
                            st.balloons()
                except Exception as e:
                    st.error(f"Error técnico: {e}")
