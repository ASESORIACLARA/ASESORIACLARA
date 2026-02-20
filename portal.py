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
    ID_CARPETA_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"
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

    # --- DISEÑO ---
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
        admin_pass = st.text_input("Introduce la Clave Maestra:", type="password")
        
        if admin_pass == PASSWORD_ADMIN:
            st.success("✅ Modo Administradora Activo")
            
            # SECCIÓN PARA AÑADIR CLIENTES
            st.write("---")
            st.write("### ➕ Añadir Nuevo Cliente")
            nuevo_email = st.text_input("Correo Gmail del cliente:").lower().strip()
            nuevo_nombre = st.text_input("Nombre de la carpeta en Drive (Exacto):")
            
            if st.button("REGISTRAR CLIENTE"):
                if nuevo_email and nuevo_nombre:
                    DICCIONARIO_CLIENTES[nuevo_email] = nuevo_nombre
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success(f"¡{nuevo_nombre} añadido correctamente!")
                    st.rerun()
                else:
                    st.warning("Rellena ambos campos")

            st.write("---")
            if st.button("🔄 CERRAR SESIÓN DE CLIENTE ACTUAL"):
                if "user_email" in st.session_state:
                    del st.session_state["user_email"]
                st.rerun()
            
            st.write("### Clientes actuales:")
            st.json(DICCIONARIO_CLIENTES)
            
            # Opción para borrar (por si te equivocas)
            borrar_email = st.selectbox("Selecciona un correo para borrar:", [""] + list(DICCIONARIO_CLIENTES.keys()))
            if borrar_email and st.button("Eliminar cliente seleccionado"):
                del DICCIONARIO_CLIENTES[borrar_email]
                guardar_clientes(DICCIONARIO_CLIENTES)
                st.rerun()

    # --- LÓGICA DE SUBIDA (Pestaña 1) ---
    with tab1:
        if "user_email" not in st.session_state:
            st.info("👋 Por favor, identifícate para subir archivos.")
            email_acc = st.text_input("Tu correo electrónico:")
            if st.button("ACCEDER"):
                if email_acc.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = email_acc.lower().strip()
                    st.rerun()
                else:
                    st.error("🚫 Correo no registrado.")
        else:
            user_email = st.session_state["user_email"]
            nombre_cli = DICCIONARIO_CLIENTES[user_email]
            st.markdown(f'<div class="user-info">Sesión iniciada como: {nombre_cli}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            ano_sel = col1.selectbox("Año", ["2026", "2025"])
            trim_sel = col2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo = st.radio("Clasificación:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            archivo = st.file_uploader("Arrastra tu factura", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if archivo and st.button("🚀 SUBIR A ASESORIACLARA"):
                try:
                    with open('token.pickle', 'rb') as t:
                        creds = pickle.load(t)
                    service = build('drive', 'v3', credentials=creds)

                    with st.spinner("Subiendo..."):
                        # Buscar carpeta
                        q = f"name = '{nombre_cli}' and '{ID_CARPETA_RAIZ}' in parents"
                        res = service.files().list(q=q).execute().get('files', [])
                        
                        if res:
                            id_cli = res[0]['id']
                            def get_id(name, p_id):
                                q_f = f"name='{name}' and '{p_id}' in parents"
                                r_f = service.files().list(q=q_f).execute().get('files', [])
                                if r_f: return r_f[0]['id']
                                return service.files().create(body={'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[p_id]}, fields='id').execute()['id']
                            
                            id_ano = get_id(ano_sel, id_cli)
                            id_tipo = get_id(tipo, id_ano)
                            id_trim = get_id(trim_sel, id_tipo)
                            
                            with open(archivo.name, "wb") as f: f.write(archivo.getbuffer())
                            media = MediaFileUpload(archivo.name, resumable=True)
                            service.files().create(body={'name':archivo.name, 'parents':[id_trim]}, media_body=media).execute()
                            os.remove(archivo.name)
                            st.success("✅ ¡Factura enviada con éxito!")
                            st.balloons()
                        else:
                            st.error(f"No existe la carpeta '{nombre_cli}' en Drive.")
                except Exception as e:
                    st.error(f"Error: {e}")


