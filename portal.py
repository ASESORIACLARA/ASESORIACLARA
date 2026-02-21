import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

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
    # ID de tu carpeta "01_CLIENTES"
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

    # --- ESTILOS ---
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

    # Conexión Drive
    with open('token.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    # --- PESTAÑA 3: GESTIÓN ---
    with tab3:
        st.subheader("⚙️ Gestión de Clientes")
        ad_pass = st.text_input("Clave Maestra:", type="password", key="adm_key")
        if ad_pass == PASSWORD_ADMIN:
            st.success("Acceso Administradora")
            c_a, c_b = st.columns(2)
            n_em = c_a.text_input("Email:")
            n_no = c_b.text_input("Carpeta Drive:")
            if st.button("REGISTRAR"):
                if n_em and n_no:
                    DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.rerun()
            st.write(DICCIONARIO_CLIENTES)
            if st.button("🔄 RESET SESIÓN CLIENTE"):
                if "user_email" in st.session_state: del st.session_state["user_email"]
                st.rerun()

    # --- PESTAÑA 1 Y 2 ---
    if "user_email" not in st.session_state:
        with tab1:
            st.info("👋 Identifícate con tu correo.")
            mail = st.text_input("Correo:")
            if st.button("ACCEDER"):
                if mail.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = mail.lower().strip()
                    st.rerun()
                else: st.error("No registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]

        with tab1:
            st.markdown(f'<div class="user-info">Sesión: {nombre_act}</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            a_v = col_a.selectbox("Año", ["2026", "2025"], key="a_v")
            t_v = col_b.selectbox("Trimestre", ["1T", "2T", "3T", "4T"], key="t_v")
            tipo_v = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Sube factura", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if arc and st.button("🚀 ENVIAR"):
                try:
                    q = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents"
                    res = service.files().list(q=q).execute().get('files', [])
                    if res:
                        id_c = res[0]['id']
                        def get_f(n, p):
                            q_f = f"name='{n}' and '{p}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                            rf = service.files().list(q=q_f).execute().get('files', [])
                            if rf: return rf[0]['id']
                            return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        
                        id_1 = get_f(a_v, id_c)
                        id_2 = get_f(tipo_v, id_1)
                        id_3 = get_f(t_v, id_2)
                        
                        with open(arc.name, "wb") as f: f.write(arc.getbuffer())
                        media = MediaFileUpload(arc.name, resumable=True)
                        service.files().create(body={'name':arc.name, 'parents':[id_3]}, media_body=media).execute()
                        os.remove(arc.name)
                        st.success("✅ ¡Subido!")
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            st.subheader("📥 Mis Impuestos")
            a_bus = st.selectbox("Año:", ["2026", "2025"], key="a_bus")
            q_c = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents"
            res_c = service.files().list(q=q_c).execute().get('files', [])
            if res_c:
                q_a = f"name = '{a_bus}' and '{res_c[0]['id']}' in parents"
                res_a = service.files().list(q=q_a).execute().get('files', [])
                if res_a:
                    q_i = f"name = 'IMPUESTOS PRESENTADOS' and '{res_a[0]['id']}' in parents"
                    res_i = service.files().list(


