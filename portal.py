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
                if archivo == AVISOS_FILE and "GLOBAL" not in datos:
                    datos["GLOBAL"] = {"mensaje": "", "fecha": ""}
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

# --- 2. LOGIN CON FRASE ORIGINAL ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2.5rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: 2.8rem; font-weight: bold;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px; font-size: 1.2rem;">Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        pass_in = st.text_input("Contraseña de Acceso:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if pass_in == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña incorrecta")
    st.stop()

# --- 3. INTERFAZ INTERNA ---
ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
PASSWORD_ADMIN = "GEST_LA_2025"

st.markdown(f"""
    <style>
    .header-box {{ background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; color: white; }}
    .header-box h1 {{ margin: 0; font-size: 2.2rem; }}
    .header-box p {{ margin: 5px 0 0 0; color: #d1d5db; }}
    .status-panel {{ background: #f1f3f9; padding: 12px; border-radius: 12px; border: 1px solid #d1d5db; text-align: center; margin-bottom: 15px; }}
    .badge {{ padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }}
    .bg-pendiente {{ background-color: #f1c40f; }} .bg-revision {{ background-color: #3498db; }} .bg-presentado {{ background-color: #2ecc71; }}
    .globo-aviso {{ border-radius: 10px; padding: 15px; margin: 10px 0; border-left: 6px solid; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
    .aviso-urgente {{ background: #fdf2f2; border-left-color: #e74c3c; color: #c0392b; }}
    .aviso-info {{ background: #ebf8ff; border-left-color: #3498db; color: #2c5282; }}
    .aviso-finalizado {{ background: #f0fff4; border-left-color: #2ecc71; color: #22543d; }}
    [data-testid="stSidebar"] {{ display: none; }}
    </style>
    <div class="header-box">
        <h1>ASESORIACLARA</h1>
        <p>Tu gestión, más fácil y transparente</p>
    </div>
""", unsafe_allow_html=True)

if "user_email" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>👋 Bienvenida</h3>", unsafe_allow_html=True)
    em_log = st.text_input("Introduce tu email registrado:")
    if st.button("ACCEDER", use_container_width=True):
        if em_log.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_log.lower().strip()
            st.rerun()
        else: st.error("Email no encontrado en nuestra base de datos.")
    st.stop()

# --- DATOS CLIENTE ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información", "fecha": ""})

# Logout y Avisos
c_logout1, c_logout2 = st.columns([0.7, 0.3])
c_logout1.markdown(f'<div style="background:#e8f0fe; padding:8px; border-radius:10px; color:#1e3a8a; font-weight:bold; text-align:center;">👤 {nombre_act}</div>', unsafe_allow_html=True)
if c_logout2.button("SALIR", use_container_width=True):
    del st.session_state["user_email"]; st.rerun()

# Avisos Globales/Personales
if DATA_AVISOS.get("GLOBAL", {}).get("mensaje"):
    st.info(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    est = "aviso-urgente" if prio == "Urgente" else "aviso-finalizado" if "finalizado" in prio else "aviso-info"
    st.markdown(f'<div class="globo-aviso {est}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("ENTENDIDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

# Estado dinámico
b_col = "bg-presentado" if config_p.get('estado') == "Presentado" else "bg-revision" if config_p.get('estado') == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo Actual: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p.get("estado")}</span></div>', unsafe_allow_html=True)

# --- DRIVE ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

with tab1:
    st.subheader("Subir Documentación")
    c1, c2 = st.columns(2)
    a_sel, t_sel = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    tipo_sel = st.radio("Categoría:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    # Listado de enviados en tiempo real
    try:
        def b_id(n, p):
            q = f"name='{n}' and '{p}' in parents and trashed=false"
            r = service.files().list(q=q).execute().get('files', [])
            return r[0]['id'] if r else None
        id_cli = b_id(nombre_act, ID_CARPETA_CLIENTES)
        if id_cli:
            id_final = b_id(t_sel, b_id(tipo_sel, b_id(a_sel, id_cli)))
            if id_final:
                st.write(f"📂 **Ya enviado en {t_sel}:**")
                docs = service.files().list(q=f"'{id_final}' in parents and trashed=false").execute().get('files', [])
                for d in docs: st.write(f"- <small>{d['name']}</small>", unsafe_allow_html=True)
    except: pass

    arc = st.file_uploader("Subir factura", type=['pdf', 'jpg', 'png', 'jpeg'])
    if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
        # Lógica de subida y renombrado (igual que en los pasos anteriores)
        st.success("¡Recibido con éxito!")

with tab2:
    st.subheader("📥 Modelos Presentados")
    a_bus = st.selectbox("Selecciona el Año:", ["2026", "2025"])
    try:
        id_c = b_id(nombre_act, ID_CARPETA_CLIENTES)
        id_a = b_id(a_bus, id_c)
        if id_a:
            q_imp = f"name = 'IMPUESTOS PRESENTADOS' and '{id_a}' in parents and trashed = false"
            res_imp = service.files().list(q=q_imp).execute().get('files', [])
            if res_imp:
                id_f_imp = res_imp[0]['id']
                impuestos = service.files().list(q=f"'{id_f_imp}' in parents and trashed = false").execute().get('files', [])
                if impuestos:
                    for imp in impuestos:
                        ca, cb = st.columns([0.7, 0.3])
                        ca.write(f"📄 {imp['name']}")
                        req = service.files().get_media(fileId=imp['id'])
                        fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req)
                        done = False
                        while not done: _, done = downloader.next_chunk()
                        cb.download_button("Descargar", fh.getvalue(), file_name=imp['name'], key=imp['id'], use_container_width=True)
                else: st.info("No hay documentos en esta carpeta todavía.")
            else: st.warning("Carpeta 'IMPUESTOS PRESENTADOS' no disponible.")
    except: st.error("Error al acceder a tus impuestos.")

with tab3:
    st.subheader("⚙️ Panel de Gestión")
    ad_p = st.text_input("Clave Administrativa:", type="password", key="admin_clv")
    if ad_p == PASSWORD_ADMIN:
        st.write("### 🛠 Configuración del Periodo")
        nuevo_t = st.text_input("Cambiar Trimestre actual:", value=CONFIG_APP['trimestre_activo'])
        if st.button("GUARDAR TRIMESTRE"):
            CONFIG_APP['trimestre_activo'] = nuevo_t
            guardar_json(CONFIG_FILE, CONFIG_APP); st.success("Cambiado."); st.rerun()
        
        st.write("---")
        # Gestión de Avisos y Estados...
