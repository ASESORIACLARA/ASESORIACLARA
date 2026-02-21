import streamlit as st
import os
import pickle
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

# --- 2. GESTIÓN DE CONTRASEÑA DE ACCESO ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Introduce la contraseña de acceso al portal</p>
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

# --- 3. LÓGICA PRINCIPAL ---
if check_password():
    # Configuración de IDs y Archivos
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(diccionario):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

    # --- DISEÑO DEL ENCABEZADO ---
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

    # Conexión con Google Drive
    try:
        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error("Error al cargar las credenciales de Google Drive. Revisa token.pickle.")
        st.stop()

    # --- PESTAÑA 3: GESTIÓN (ADMINISTRADORA) ---
    with tab3:
        st.subheader("⚙️ Configuración del Portal")
        ad_pass = st.text_input("Clave Maestra de Administradora:", type="password", key="adm_key")
        if ad_pass == PASSWORD_ADMIN:
            st.success("Acceso Administradora Autorizado")
            col_a, col_b = st.columns(2)
            n_em = col_a.text_input("Nuevo Email Gmail:")
            n_no = col_b.text_input("Nombre Carpeta Exacto:")
            
            if st.button("REGISTRAR CLIENTE"):
                if n_em and n_no:
                    DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success(f"¡{n_no} registrado con éxito!")
                    st.rerun()
            
            st.write("### Base de datos de clientes:", DICCIONARIO_CLIENTES)
            if st.button("🔄 CERRAR SESIÓN DE CLIENTE ACTUAL"):
                if "user_email" in st.session_state: 
                    del st.session_state["user_email"]
                st.rerun()

    # --- LÓGICA DE IDENTIFICACIÓN DE CLIENTE ---
    if "user_email" not in st.session_state:
        with tab1:
            st.info("👋 Por favor, identifícate con tu correo para acceder a tus funciones.")
            mail = st.text_input("Introduce tu correo electrónico:")
            if st.button("ACCEDER AL PORTAL"):
                if mail.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = mail.lower().strip()
                    st.rerun()
                else:
                    st.error("🚫 El correo no está registrado en el sistema.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]

        # --- PESTAÑA 1: SUBIDA DE FACTURAS ---
        with tab1:
            st.markdown(f'<div class="user-info">Sesión iniciada: {nombre_act}</div>', unsafe_allow_html=True)
            col_1, col_2 = st.columns(2)
            a_sel = col_1.selectbox("Selecciona el Año", ["2026", "2025"], key="a_v")
            t_sel = col_2.selectbox("Selecciona el Trimestre", ["1T", "2T", "3T", "4T"], key="t_v")
            tipo_sel = st.radio("Tipo de factura:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            archivo = st.file_uploader("Sube tu archivo (PDF o Imagen)", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if archivo and st.button("🚀 ENVIAR FACTURA AHORA"):
                try:
                    # Buscar la carpeta del cliente dentro de 01_CLIENTES
                    q_c = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                    res_c = service.files().list(q=q_c).execute().get('files', [])
                    
                    if res_c:
                        id_cli = res_c[0]['id']
                        
                        def get_or_create_folder(name, parent_id):
                            query = f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                            found = service.files().list(q=query).execute().get('files', [])
                            if found: return found[0]['id']
                            # Si no existe, la creamos
                            body = {'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
                            return service.files().create(body=body, fields='id').execute().get('id')
                        
                        # Navegar/Crear estructura: Año -> Tipo -> Trimestre
                        id_ano = get_or_create_folder(a_sel, id_cli)
                        id_tipo = get_or_create_folder(tipo_sel, id_ano)
                        id_trim = get_or_create_folder(t_sel, id_tipo)
                        
                        # Proceso de subida
                        with open(archivo.name, "wb") as f:
                            f.write(archivo.getbuffer())
                        
                        media = MediaFileUpload(archivo.name, resumable=True)
                        service.files().create(body={'name': archivo.name, 'parents': [id_trim]}, media_body=media).execute()
                        os.remove(archivo.name)
                        
                        st.success("✅ ¡Factura recibida correctamente! Gracias.")
                        st.balloons()
                    else:
                        st.error(f"No se encontró la carpeta '{nombre_act}' en Drive. Contacta con soporte.")
                except Exception as e:
                    st.error(f"Hubo un problema técnico al subir el archivo: {e}")

        # --- PESTAÑA 2: DESCARGA DE IMPUESTOS ---
        with tab2:
            st.subheader("📥 Mis Impuestos y Modelos Presentados")
            a_bus = st.selectbox("Selecciona el año de consulta:", ["2026", "2025"], key="a_bus")
            
            try:
                # 1. Buscar carpeta cliente
                q_cli = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                res_cli = service.files().list(q=q_cli).execute().get('files', [])
                
                if res_cli:
                    id_folder_cli = res_cli[0]['id']
                    # 2. Buscar carpeta Año
                    q_ano = f"name = '{a_bus}' and '{id_folder_cli}' in parents and trashed = false"
                    res_ano = service.files().list(q=q_ano).execute().get('files', [])
                    
                    if res_ano:
                        id_folder_ano = res_ano[0]['id']
                        # 3. Buscar "IMPUESTOS PRESENTADOS"
                        q_imp = f"name = 'IMPUESTOS PRESENTADOS' and '{id_folder_ano}' in parents and trashed = false"
                        res_imp = service.files().list(q=q_imp).execute().get('files', [])
                        
                        if res_imp:
                            id_folder_imp = res_imp[0]['id']
                            # 4. Listar archivos
                            lista_docs = service.files().list(q=f"'{id_folder_imp}' in parents and trashed = false").execute().get('files', [])
                            
                            if lista_docs:
                                for doc in lista_docs:
                                    col1, col2 = st.columns([3,1])
                                    col1.write(f"📄 **{doc['name']}**")
                                    # Descargar el archivo
                                    request = service.files().get_media(fileId=doc['id'])
                                    fh = io.BytesIO()
                                    downloader = MediaIoBaseDownload(fh, request)
                                    done = False
                                    while not done:
                                        _, done = downloader.next_chunk()
                                    col2.download_button("Descargar", fh.getvalue(), file_name=doc['name'], key=doc['id'])
                            else:
                                st.info("Todavía no hay documentos cargados en esta carpeta.")
                        else:
                            st.info("La carpeta 'IMPUESTOS PRESENTADOS' aún no ha sido creada para este año.")
                    else:
                        st.info(f"No hay registros disponibles para el año {a_bus}.")
            except Exception as e:
                st.error(f"Error al conectar con la base de impuestos: {e}")

