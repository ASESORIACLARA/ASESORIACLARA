import streamlit as st
import os, pickle, json, io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

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
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
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

    # LAS PESTAÑAS SE CREAN AQUÍ (SIEMPRE VISIBLES)
    tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN (ADMIN)"])

    with open('token.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    # --- PESTAÑA 3: GESTIÓN (ADMIN) ---
    with tab3:
        st.subheader("⚙️ Panel de Gestión")
        ad_pass = st.text_input("Clave Maestra:", type="password", key="adm_key")
        if ad_pass == PASSWORD_ADMIN:
            st.success("Acceso Administradora")
            col_a, col_b = st.columns(2)
            n_em = col_a.text_input("Email Gmail:")
            n_no = col_b.text_input("Nombre Carpeta:")
            if st.button("REGISTRAR CLIENTE"):
                if n_em and n_no:
                    DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.success("¡Registrado!")
                    st.rerun()
            
            st.write("### 👥 Clientes Actuales")
            for email, nombre in list(DICCIONARIO_CLIENTES.items()):
                c_i, c_d = st.columns([3, 1])
                c_i.write(f"**{nombre}** ({email})")
                if c_d.button("ELIMINAR", key=f"del_{email}"):
                    del DICCIONARIO_CLIENTES[email]
                    guardar_clientes(DICCIONARIO_CLIENTES)
                    st.rerun()

    # --- CONTENIDO PARA CLIENTES (TAB 1 Y TAB 2) ---
    if "user_email" not in st.session_state:
        with tab1:
            st.info("👋 Identifícate con tu correo para empezar.")
            em_log = st.text_input("Correo electrónico registrado:")
            if st.button("ACCEDER AL PORTAL"):
                if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = em_log.lower().strip()
                    st.rerun()
                else: st.error("No registrado.")
        with tab2:
            st.warning("Debes identificarte en la pestaña 'ENVIAR FACTURAS' primero.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]

        with tab1:
            st.markdown(f'<div class="user-info">Sesión de: {nombre_act}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            a_sel = c1.selectbox("Año", ["2026", "2025"])
            t_sel = c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Clasificación:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Sube factura (PDF o Imagen)", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if arc and st.button("🚀 SUBIR AHORA"):
                try:
                    q = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                    res = service.files().list(q=q).execute().get('files', [])
                    if res:
                        id_cli = res[0]['id']
                        def get_f(n, p):
                            q_f = f"name='{n}' and '{p}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                            rf = service.files().list(q=q_f).execute().get('files', [])
                            if rf: return rf[0]['id']
                            return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        
                        id_final = get_f(t_sel, get_f(tipo_sel, get_f(a_sel, id_cli)))
                        with open(arc.name, "wb") as f: f.write(arc.getbuffer())
                        media = MediaFileUpload(arc.name, resumable=True)
                        service.files().create(body={'name':arc.name, 'parents':[id_final]}, media_body=media).execute()
                        os.remove(arc.name)
                        st.success("✅ ¡Subido con éxito!")
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            st.subheader("📥 Mis Impuestos")
            st.markdown(f"Consultando documentos de: **{nombre_act}**")
            a_bus = st.selectbox("Año consulta:", ["2026", "2025"], key="bus_a")
            q_c = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
            res_c = service.files().list(q=q_c).execute().get('files', [])
            if res_c:
                q_path = f"name = '{a_bus}' and '{res_c[0]['id']}' in parents"
                res_a = service.files().list(q=q_path).execute().get('files', [])
                if res_a:
                    q_imp = f"name = 'IMPUESTOS PRESENTADOS' and '{res_a[0]['id']}' in parents"
                    res_i = service.files().list(q=q_imp).execute().get('files', [])
                    if res_i:
                        docs = service.files().list(q=f"'{res_i[0]['id']}' in parents").execute().get('files', [])
                        if docs:
                            for d in docs:
                                col_a, col_b = st.columns([3,1])
                                col_a.write(f"📄 {d['name']}")
                                req = service.files().get_media(fileId=d['id'])
                                fh = io.BytesIO()
                                downloader = MediaIoBaseDownload(fh, req)
                                done = False
                                while not done: _, done = downloader.next_chunk()
                                col_b.download_button("Bajar", fh.getvalue(), file_name=d['name'], key=d['id']+"_dl")
                        else: st.info("No hay archivos en la carpeta.")
                    else: st.info("No hay carpeta 'IMPUESTOS PRESENTADOS'.")
                else: st.info("Sin datos para este año.")

        if st.sidebar.button("🔒 CERRAR SESIÓN"):
            del st.session_state["user_email"]
            st.rerun()




