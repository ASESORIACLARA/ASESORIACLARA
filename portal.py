import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered", initial_sidebar_state="collapsed")

DB_FILE = "clientes_db.json"
AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"

def cargar_json(archivo, inicial):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if archivo == AVISOS_FILE and "GLOBAL" not in datos: datos["GLOBAL"] = {"mensaje": "", "fecha": ""}
                return datos
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

DICCIONARIO_CLIENTES = cargar_json(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": "", "fecha": ""}})
HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})

# --- 2. ESTILOS CSS (OPTIMIZADO PARA MÓVIL) ---
st.markdown("""
    <style>
    /* Ajustes para móviles */
    @media (max-width: 640px) {
        .stButton button { width: 100%; height: 3rem; font-size: 1.1rem !important; margin-bottom: 10px; }
        .header-box h1 { font-size: 1.8rem !important; }
        .header-box p { font-size: 1rem !important; }
    }
    .header-box { background-color: #1e3a8a; padding: 2rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1.5rem; }
    .status-panel { background: #f8fafc; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; font-size: 1.1rem; }
    .badge { padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 18px; margin: 12px 0; border-left: 8px solid; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    .aviso-finalizado { background: #f0fdf4; border-left-color: #22c55e; color: #166534; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
    with col2:
        pass_in = st.text_input("Contraseña Maestra:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if pass_in == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Incorrecta")
    st.stop()

# --- 4. PORTAL INTERNO ---
st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)

if "user_email" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>Bienvenida</h3>", unsafe_allow_html=True)
    em_log = st.text_input("Introduce tu email para acceder:")
    if st.button("ACCEDER", use_container_width=True):
        if em_log.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_log.lower().strip()
            st.rerun()
        else: st.error("Email no registrado.")
    st.stop()

email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})

# Info Usuario y Avisos
c_u1, c_u2 = st.columns([0.7, 0.3])
c_u1.info(f"👤 **{nombre_act}**")
if c_u2.button("SALIR", use_container_width=True):
    del st.session_state["user_email"]; st.rerun()

if DATA_AVISOS.get("GLOBAL", {}).get("mensaje"):
    st.warning(f"📢 **AVISO:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    clase = "aviso-urgente" if prio == "Urgente" else "aviso-finalizado" if "finalizado" in prio else "aviso-info"
    st.markdown(f'<div class="globo-aviso {clase}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("ENTENDIDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

# Estado
b_color = "bg-presentado" if config_p.get('estado') == "Presentado" else "bg-revision" if config_p.get('estado') == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_color}">{config_p.get("estado")}</span></div>', unsafe_allow_html=True)

# --- 5. DRIVE Y TABS ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

def b_id(nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    meta = {'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}
    return service.files().create(body=meta, fields='id').execute().get('id')

t1, t2, t3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Facturas")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Categoría:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    try:
        id_cli = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
        id_f = b_id(t_s, b_id(cat, b_id(a_s, id_cli)))
        docs = service.files().list(q=f"'{id_f}' in parents and trashed=false").execute().get('files', [])
        if docs:
            with st.expander(f"Ver archivos enviados ({len(docs)})"):
                for d in docs: st.write(f"✅ {d['name']}")
    except: pass

    arc = st.file_uploader("Elegir archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
    if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
        ahora = datetime.datetime.now()
        ref = ahora.strftime('%Y%m%d%H%M%S')
        n_nom = f"{ahora.strftime('%Y-%m-%d')}_{cat[:4]}_REF-{ref}{os.path.splitext(arc.name)[1]}"
        m_meta = {'name': n_nom, 'parents': [id_f]}
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body=m_meta, media_body=media).execute()
        st.success(f"¡Enviado! Ref: {ref}")
        st.balloons()

with t2:
    st.subheader("Mis Impuestos")
    a_b = st.selectbox("Año:", ["2026", "2025"], key="busq_imp")
    try:
        id_c = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
        id_a = b_id(a_b, id_c)
        res_f = service.files().list(q=f"name='IMPUESTOS PRESENTADOS' and '{id_a}' in parents and trashed=false").execute().get('files', [])
        if res_f:
            imps = service.files().list(q=f"'{res_f[0]['id']}' in parents and trashed=false").execute().get('files', [])
            for im in imps:
                c_n, c_d = st.columns([0.7, 0.3])
                c_n.write(f"📄 {im['name']}")
                req = service.files().get_media(fileId=im['id'])
                fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req)
                done = False
                while not done: _, done = downloader.next_chunk()
                c_d.download_button("Bajar", fh.getvalue(), file_name=im['name'], key=im['id'])
        else: st.info("No hay impuestos todavía.")
    except: pass

with t3:
    st.subheader("Panel de Gestión")
    ad_p = st.text_input("Clave Maestra:", type="password", key="adm_final")
    if ad_p == "GEST_LA_2025":
        # 1. TRIMESTRE
        st.write("### 🛠 Configuración")
        n_t = st.text_input("Trimestre visible:", value=CONFIG_APP['trimestre_activo'])
        if st.button("GUARDAR TRIMESTRE"):
            CONFIG_APP['trimestre_activo'] = n_t
            guardar_json(CONFIG_FILE, CONFIG_APP); st.rerun()

        # 2. HERRAMIENTAS
        st.write("---")
        op = st.radio("Herramienta:", ["Avisos", "Lecturas", "Clientes"], horizontal=True)
        
        if op == "Avisos":
            dest = st.selectbox("Enviar a:", ["TODOS", "UN CLIENTE"])
            if dest == "TODOS":
                m_g = st.text_area("Mensaje global:", value=DATA_AVISOS["GLOBAL"]["mensaje"])
                if st.button("Publicar Global"):
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_g}; guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()
            else:
                c_s = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                est_n = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                prio_n = st.selectbox("Prioridad Globo:", ["Información", "Urgente", "Trámite finalizado"])
                msg_n = st.text_area("Mensaje:")
                if st.button("Actualizar Cliente"):
                    DATA_AVISOS[c_s] = {"estado": est_n, "mensaje": msg_n, "prioridad": prio_n}
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()
        
        elif op == "Lecturas":
            for l in reversed(HISTORIAL_LOG): st.write(f"✅ **{l['cliente']}** ({l['fecha']}): {l['msg']}")
        
        elif op == "Clientes":
            st.write("### 👥 Alta de nuevo cliente")
            n_nom = st.text_input("Nombre y Apellidos:")
            n_ema = st.text_input("Email del cliente:")
            if st.button("REGISTRAR CLIENTE"):
                if n_nom and n_ema:
                    DICCIONARIO_CLIENTES[n_ema.lower().strip()] = n_nom.upper()
                    guardar_json(DB_FILE, DICCIONARIO_CLIENTES)
                    st.success(f"Cliente {n_nom} dado de alta correctamente.")
                    st.rerun()
                else: st.warning("Rellena nombre y email.")
            
            st.write("---")
            with st.expander("Eliminar Cliente"):
                c_d = st.selectbox("Borrar a:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                if st.button("BORRAR DEFINITIVAMENTE"):
                    del DICCIONARIO_CLIENTES[c_d]; guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()

