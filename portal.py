import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS (Mejora de Interfaz) ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-weight: bold; }
    .header-box p { color: #d1d5db; margin-top: 10px; }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .st-rojo { background-color: #ffebee; color: #b71c1c; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #f44336; }
    .st-amarillo { background-color: #fff9c4; color: #827717; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #fbc02d; }
    .st-verde { background-color: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #4caf50; }
    .aviso-caja { padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 6px solid #2196f3; background-color: #f0f7ff; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE BASES DE DATOS LOCALES ---
DB_F, AV_F = "clientes_db.json", "avisos_db.json"
def load_j(f, d):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as f1: return json.load(f1)
        except: return d
    return d
def save_j(f, d):
    with open(f, "w", encoding="utf-8") as f1: json.dump(d, f1, indent=4, ensure_ascii=False)

# --- 3. ACCESO AL PORTAL (Inicio Original Recuperado) ---
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True

    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña de acceso:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña incorrecta")
    return False

if check_password():
    ID_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PW_ADM = "GEST_LA_2025"
    D_CLI = load_j(DB_F, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    D_AVI = load_j(AV_F, {})

    if "user_email" not in st.session_state:
        st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
        st.write("### 👋 Bienvenida al Portal")
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            em_log = st.text_input("Introduce tu correo electrónico:")
            if st.button("ACCEDER", use_container_width=True):
                if em_log.lower().strip() in D_CLI:
                    st.session_state["user_email"] = em_log.lower().strip()
                    st.rerun()
                else: st.error("Correo no registrado.")
    else:
        # --- PORTAL DEL CLIENTE ---
        mail = st.session_state["user_email"]
        nom = D_CLI[mail]
        inf = D_AVI.get(mail, {})
        txt_av = inf.get("texto", "Bienvenido/a al portal.")
        est_av = inf.get("estado", "Pendiente documentación")

        cl_c = "st-rojo"
        if "revisión" in est_av.lower(): cl_c = "st-amarillo"
        elif "presentado" in est_av.lower(): cl_c = "st-verde"

        st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
        
        c_out1, c_out2 = st.columns([4,1])
        c_out1.markdown(f'<div class="user-info">Sesión: {nom}</div>', unsafe_allow_html=True)
        if c_out2.button("🔒 SALIR"):
            del st.session_state["user_email"]; st.rerun()

        st.markdown(f'<div class="{cl_c}">📊 ESTADO: {est_av.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="aviso-caja">📢 <b>AVISO:</b> {txt_av}</div>', unsafe_allow_html=True)

        t1, t2, t3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])
        
        # Conexión a Drive (Mejora: Manejo de token)
        try:
            with open('token.pickle', 'rb') as tk: srv = build('drive', 'v3', credentials=pickle.load(tk))
        except Exception:
            st.error("Error de conexión con Google Drive. Contacta con soporte.")
            st.stop()

        with t1:
            st.subheader("Subir Documentación")
            c1, c2 = st.columns(2)
            a_v, t_v = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_v = st.radio("Carpeta:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Arrastra aquí tu archivo o haz clic para subir")
            
            if arc and st.button("🚀 ENVIAR DOCUMENTO"):
                try:
                    res = srv.files().list(q=f"name='{nom}' and '{ID_RAIZ}' in parents").execute().get('files', [])
                    if res:
                        id_c = res[0]['id']
                        def get_f(n, p):
                            q = f"name='{n}' and '{p}' in parents and trashed=false"
                            r = srv.files().list(q=q).execute().get('files', [])
                            if r: return r[0]['id']
                            return srv.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        id_dest = get_f(t_v, get_f(tipo_v, get_f(a_v, id_c)))
                        srv.files().create(body={'name': arc.name, 'parents': [id_dest]}, media_body=MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream')).execute()
                        st.success(f"✅ {arc.name} se ha subido correctamente.")
                        st.rerun()
                except Exception as e: st.error(f"Error al subir: {e}")

            # Mejora: Visualización de archivos ya subidos
            st.write("---")
            st.subheader(f"📂 Archivos en {tipo_v} ({t_v})")
            try:
                res_v = srv.files().list(q=f"name='{nom}' and '{ID_RAIZ}' in parents").execute().get('files', [])
                if res_v:
                    id_cli = res_v[0]['id']
                    q_v = f"name='{a_v}' and '{id_cli}' in parents"
                    r_a = srv.files().list(q=q_v).execute().get('files', [])
                    if r_a:
                        q_tp = f"name='{tipo_v}' and '{r_a[0]['id']}' in parents"
                        r_tp = srv.files().list(q=q_tp).execute().get('files', [])
                        if r_tp:
                            q_tri = f"name='{t_v}' and '{r_tp[0]['id']}' in parents"
                            r_tri = srv.files().list(q=q_tri).execute().get('files', [])
                            if r_tri:
                                docs = srv.files().list(q=f"'{r_tri[0]['id']}' in parents and trashed=false").execute().get('files', [])
                                if docs:
                                    for d in docs: st.write(f"📄 {d['name']}")
                                else: st.info("No se han encontrado archivos en este trimestre.")
            except: st.warning("No se pudo cargar la lista de archivos.")

        with t2:
            st.subheader("Descargar Mis Impuestos")
            a_b = st.selectbox("Año consulta:", ["2026", "2025"])
            r_c = srv.files().list(q=f"name='{nom}' and '{ID_RAIZ}' in parents").execute().get('files', [])
            if r_c:
                id_cl = r_c[0]['id']
                r_a = srv.files().list(q=f"name='{a_b}' and '{id_cl}' in parents").execute().get('files', [])
                if r_a:
                    fls = srv.files().list(q=f"'{r_a[0]['id']}' in parents").execute().get('files', [])
                    id_imp = next((x['id'] for x in fls if "IMPUESTO" in x['name'].upper()), None)
                    if id_imp:
                        docs_i = srv.files().list(q=f"'{id_imp}' in parents and trashed=false").execute().get('files', [])
                        for d_i in docs_i:
                            buf = io.BytesIO()
                            downloader = MediaIoBaseDownload(buf, srv.files().get_media(fileId=d_i['id']))
                            done = False
                            while not done: _, done = downloader.next_chunk()
                            st.download_button(f"📥 Descargar {d_i['name']}", buf.getvalue(), file_name=d_i['name'], key=d_i['id'])

        with t3:
            # Mejora: Panel de Gestión Simplificado
            if st.text_input("Acceso Admin:", type="password") == PW_ADM:
                st.write("### Panel de Control")
                c_sel = st.selectbox("Seleccionar Cliente:", list(D_CLI.keys()))
                m_txt = st.text_area("Nuevo Aviso:"); e_est = st.selectbox("Cambiar Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                if st.button("GUARDAR CAMBIOS"):
                    D_AVI[c_sel] = {"texto": m_txt, "estado": e_est}; save_j(AV_F, D_AVI); st.success("Datos actualizados.")
