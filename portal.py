import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS (TU DISEÑO ORIGINAL) ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
    .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 15px; text-align: center; font-size: 0.9rem; }
    .st-rojo { background-color: #ffebee; color: #b71c1c; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #f44336; }
    .st-amarillo { background-color: #fff9c4; color: #827717; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #fbc02d; }
    .st-verde { background-color: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #4caf50; }
    .aviso-caja { padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 6px solid #2196f3; background-color: #f0f7ff; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNCIONES DE ACCESO ---
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True

    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña incorrecta")
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE, AV_FILE = "clientes_db.json", "avisos_db.json"

    def cargar_datos(f, defecto):
        if os.path.exists(f):
            try:
                with open(f, "r", encoding="utf-8") as file: return json.load(file)
            except: return defecto
        return defecto

    def guardar_datos(f, datos):
        with open(f, "w", encoding="utf-8") as file: json.dump(datos, file, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_datos(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    DICCIONARIO_AVISOS = cargar_datos(AV_FILE, {})

    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenida al Portal")
        c_mail1, c_mail2, c_mail3 = st.columns([1,2,1])
        with c_mail2:
            em_log = st.text_input("Correo electrónico:")
            if st.button("ACCEDER", use_container_width=True):
                if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = em_log.lower().strip()
                    st.rerun()
                else: st.error("Correo no registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]
        
        # --- MEJORA: GESTIÓN DE AVISOS Y COLORES ---
        info_aviso = DICCIONARIO_AVISOS.get(email_act, {})
        texto_aviso = info_aviso.get("texto", "Bienvenido/a al portal.")
        estado_aviso = info_aviso.get("estado", "Pendiente documentación")

        clase_color = "st-rojo"
        if "revisión" in estado_aviso.lower(): clase_color = "st-amarillo"
        elif "presentado" in estado_aviso.lower(): clase_color = "st-verde"

        c_logout1, c_logout2 = st.columns([4,1])
        c_logout1.markdown(f'<div class="user-info">Sesión de: {nombre_act}</div>', unsafe_allow_html=True)
        if c_logout2.button("🔒 SALIR"):
            del st.session_state["user_email"]; st.rerun()

        st.markdown(f'<div class="{clase_color}">📊 ESTADO: {estado_aviso.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="aviso-caja">📢 <b>AVISO:</b> {texto_aviso}</div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR DOCUMENTOS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

        with open('token.pickle', 'rb') as t: creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)

        with tab1:
            st.subheader("Subir Facturas")
            c1, c2 = st.columns(2)
            a_sel, t_sel = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Selecciona archivo")
            
            if arc and st.button("🚀 ENVIAR AHORA"):
                try:
                    q = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                    res = service.files().list(q=q).execute().get('files', [])
                    if res:
                        id_cli = res[0]['id']
                        def get_f(n, p):
                            q_f = f"name='{n}' and '{p}' in parents and trashed=false"
                            rf = service.files().list(q=q_f).execute().get('files', [])
                            if rf: return rf[0]['id']
                            return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        
                        id_final = get_f(t_sel, get_f(tipo_sel, get_f(a_sel, id_cli)))
                        service.files().create(body={'name':arc.name, 'parents':[id_final]}, media_body=MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream')).execute()
                        st.markdown(f'<div class="justificante">✅ Recibido correctamente.</div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            st.subheader("Descargar Mis Impuestos")
            a_bus = st.selectbox("Año consulta:", ["2026", "2025"])
            q_cli_imp = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
            res_cli_imp = service.files().list(q=q_cli_imp).execute().get('files', [])
            if res_cli_imp:
                id_cli_imp = res_cli_imp[0]['id']
                q_ano = f"name = '{a_bus}' and '{id_cli_imp}' in parents and trashed = false"
                res_ano = service.files().list(q=q_ano).execute().get('files', [])
                if res_ano:
                    id_ano = res_ano[0]['id']
                    todas = service.files().list(q=f"'{id_ano}' in parents and trashed = false").execute().get('files', [])
                    # MEJORA: Búsqueda flexible por nombre
                    id_imp = next((f['id'] for f in todas if "IMPUESTOS" in f['name'].upper()), None)
                    if id_imp:
                        docs = service.files().list(q=f"'{id_imp}' in parents and trashed=false").execute().get('files', [])
                        for d in docs:
                            buf = io.BytesIO()
                            downloader = MediaIoBaseDownload(buf, service.files().get_media(fileId=d['id']))
                            done = False
                            while not done: _, done = downloader.next_chunk()
                            st.download_button(f"📥 {d['name']}", buf.getvalue(), file_name=d['name'], key=d['id'])
                    else: st.warning("Carpeta de impuestos no encontrada.")

        with tab3:
            st.subheader("⚙️ Gestión")
            if st.text_input("Clave Maestra:", type="password") == PASSWORD_ADMIN:
                c_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()))
                m_txt = st.text_area("Aviso:")
                e_est = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                if st.button("ACTUALIZAR"):
                    DICCIONARIO_AVISOS[c_sel] = {"texto": m_txt, "estado": e_est}
                    guardar_datos(AV_FILE, DICCIONARIO_AVISOS); st.success("¡Portal actualizado!")
                
                st.write("---")
                for email, nombre in list(DICCIONARIO_CLIENTES.items()):
                    c_i, c_d = st.columns([3, 1])
                    c_i.write(f"**{nombre}**")
                    if c_d.button("X", key=f"del_{email}"):
                        del DICCIONARIO_CLIENTES[email]; guardar_datos(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()
                
                ne, nn = st.text_input("Nuevo Email:"), st.text_input("Nuevo Nombre Drive:")
                if st.button("REGISTRAR") and ne and nn:
                    DICCIONARIO_CLIENTES[ne.lower().strip()] = nn; guardar_datos(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()
