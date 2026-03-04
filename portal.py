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

# --- 2. LOGIN ESTÉTICO ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: 2.5rem;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Acceso exclusivo para clientes</p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        pass_in = st.text_input("Introduce la Contraseña Maestra:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if pass_in == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña incorrecta")
    st.stop()

# --- 3. INTERFAZ Y DRIVE ---
ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
PASSWORD_ADMIN = "GEST_LA_2025"

st.markdown(f"""
    <style>
    .header-box {{ background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; color: white; }}
    .status-panel {{ background: #f1f3f9; padding: 12px; border-radius: 12px; border: 1px solid #d1d5db; text-align: center; margin-bottom: 15px; }}
    .badge {{ padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }}
    .bg-pendiente {{ background-color: #f1c40f; }} .bg-revision {{ background-color: #3498db; }} .bg-presentado {{ background-color: #2ecc71; }}
    .globo-aviso {{ border-radius: 10px; padding: 15px; margin: 10px 0; border-left: 6px solid; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
    .aviso-urgente {{ background: #fdf2f2; border-left-color: #e74c3c; color: #c0392b; }}
    .aviso-info {{ background: #ebf8ff; border-left-color: #3498db; color: #2c5282; }}
    .aviso-finalizado {{ background: #f0fff4; border-left-color: #2ecc71; color: #22543d; }}
    [data-testid="stSidebar"] {{ display: none; }}
    </style>
    <div class="header-box"><h1>ASESORIACLARA</h1></div>
""", unsafe_allow_html=True)

if "user_email" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>👋 Bienvenida</h3>", unsafe_allow_html=True)
    em_log = st.text_input("Introduce tu email registrado para acceder:")
    if st.button("ACCEDER", use_container_width=True):
        if em_log.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_log.lower().strip()
            st.rerun()
        else: st.error("Email no encontrado.")
    st.stop()

# --- DATOS SESIÓN ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información", "fecha": ""})

# Logout y Avisos
c_logout1, c_logout2 = st.columns([0.7, 0.3])
c_logout1.markdown(f'<div style="background:#e8f0fe; padding:8px; border-radius:10px; color:#1e3a8a; font-weight:bold; text-align:center;">👤 {nombre_act}</div>', unsafe_allow_html=True)
if c_logout2.button("SALIR", use_container_width=True):
    del st.session_state["user_email"]; st.rerun()

# Avisos Globales y Personales
if DATA_AVISOS.get("GLOBAL", {}).get("mensaje"):
    st.info(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    est = "aviso-urgente" if prio == "Urgente" else "aviso-finalizado" if "finalizado" in prio else "aviso-info"
    st.markdown(f'<div class="globo-aviso {est}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("MARCAR COMO LEÍDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

# Estado
b_col = "bg-presentado" if config_p.get('estado') == "Presentado" else "bg-revision" if config_p.get('estado') == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo Actual: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p.get("estado")}</span></div>', unsafe_allow_html=True)

# --- CONEXIÓN DRIVE ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

tab1, tab2, tab3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

with tab1:
    st.subheader("Subir Facturas")
    c1, c2 = st.columns(2)
    a_sel, t_sel = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    tipo_sel = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    # Listar enviados
    try:
        def b_id(n, p):
            q = f"name='{n}' and '{p}' in parents and trashed=false"
            r = service.files().list(q=q).execute().get('files', [])
            return r[0]['id'] if r else None
        id_cli = b_id(nombre_act, ID_CARPETA_CLIENTES)
        if id_cli:
            id_final = b_id(t_sel, b_id(tipo_sel, b_id(a_sel, id_cli)))
            if id_final:
                st.write(f"📂 **Enviados en {t_sel}:**")
                docs = service.files().list(q=f"'{id_final}' in parents and trashed=false").execute().get('files', [])
                for d in docs: st.write(f"- <small>{d['name']}</small>", unsafe_allow_html=True)
    except: pass

    arc = st.file_uploader("Elegir archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
    if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
        # (Lógica de renombrado y subida...)
        st.success("¡Documento enviado!")

with tab2:
    st.subheader("📥 Mis Impuestos Presentados")
    a_bus = st.selectbox("Selecciona Año:", ["2026", "2025"])
    try:
        id_c = b_id(nombre_act, ID_CARPETA_CLIENTES)
        id_a = b_id(a_bus, id_c)
        if id_a:
            # Buscar carpeta de Impuestos
            q_imp = f"name = 'IMPUESTOS PRESENTADOS' and '{id_a}' in parents and trashed = false"
            res_imp = service.files().list(q=q_imp).execute().get('files', [])
            if res_imp:
                id_f_imp = res_imp[0]['id']
                impuestos = service.files().list(q=f"'{id_f_imp}' in parents and trashed = false").execute().get('files', [])
                if impuestos:
                    for imp in impuestos:
                        col_n, col_d = st.columns([0.7, 0.3])
                        col_n.write(f"📄 {imp['name']}")
                        # Lógica de descarga
                        req = service.files().get_media(fileId=imp['id'])
                        fh = io.BytesIO()
                        downloader = MediaIoBaseDownload(fh, req)
                        done = False
                        while not done: _, done = downloader.next_chunk()
                        col_d.download_button("Bajar", fh.getvalue(), file_name=imp['name'], key=imp['id'], use_container_width=True)
                else: st.info("No hay modelos subidos todavía.")
            else: st.warning("Carpeta 'IMPUESTOS PRESENTADOS' no encontrada en Drive.")
    except Exception as e: st.error("Error al conectar con Drive.")

with tab3:
    st.subheader("⚙️ Panel de Gestión")
    ad_p = st.text_input("Clave Maestra:", type="password", key="adm_p")
    if ad_p == PASSWORD_ADMIN:
        st.write("### 🛠 Configuración del Periodo")
        nuevo_t = st.text_input("Trimestre visible (ej: 1T 2026):", value=CONFIG_APP['trimestre_activo'])
        if st.button("ACTUALIZAR TRIMESTRE"):
            CONFIG_APP['trimestre_activo'] = nuevo_t
            guardar_json(CONFIG_FILE, CONFIG_APP); st.success("Cambiado."); st.rerun()
        
        st.write("---")
        # Avisos y Estados (Lógica completa...)
