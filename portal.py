import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. BASES DE DATOS Y CONFIGURACIÓN ---
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

# --- 2. ESTILOS CSS (ADAPTACIÓN MÓVIL TOTAL) ---
st.markdown("""
    <style>
    @media (max-width: 640px) {
        .stButton button { width: 100% !important; height: 3.8rem !important; font-size: 1.2rem !important; border-radius: 12px !important; }
        .header-box h1 { font-size: 1.8rem !important; }
    }
    .header-box { background-color: #1e3a8a; padding: 2rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1.5rem; }
    .header-box p { color: #d1d5db; margin-top: 5px; font-size: 1.1rem; }
    .status-panel { background: #f8fafc; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; }
    .badge { padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 18px; margin: 12px 0; border-left: 8px solid; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    .aviso-finalizado { background: #f0fdf4; border-left-color: #22c55e; color: #166534; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ACCESO (LOGIN) ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([0.05, 0.9, 0.05])
    with col_l2:
        pass_in = st.text_input("Contraseña Maestra:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if pass_in == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña incorrecta")
    st.stop()

# --- 4. ÁREA DE CLIENTE ---
st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)

if "user_email" not in st.session_state:
    st.markdown("<h4 style='text-align:center;'>Acceso Clientes</h4>", unsafe_allow_html=True)
    em_log = st.text_input("Introduce tu email registrado:")
    if st.button("ACCEDER AL PORTAL", use_container_width=True):
        if em_log.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_log.lower().strip()
            st.rerun()
        else: st.error("El email no está registrado.")
    st.stop()

email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})

# Cabecera Usuario
c_u1, c_u2 = st.columns([0.7, 0.3])
c_u1.markdown(f"👤 **{nombre_act}**")
if c_u2.button("SALIR", use_container_width=True):
    del st.session_state["user_email"]; st.rerun()

# Avisos (Global y Personal con Botón de Lectura)
if DATA_AVISOS.get("GLOBAL", {}).get("mensaje"):
    st.warning(f"📢 **AVISO:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    clase = "aviso-urgente" if prio == "Urgente" else "aviso-finalizado" if "finalizado" in prio else "aviso-info"
    st.markdown(f'<div class="globo-aviso {clase}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("MARCAR COMO LEÍDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

# Estado Visual
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

tab1, tab2, tab3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

with tab1:
    st.subheader("Subir Facturación")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Categoría:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    try:
        id_cli = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
        id_f = b_id(t_s, b_id(cat, b_id(a_s, id_cli)))
        docs = service.files().list(q=f"'{id_f}' in parents and trashed=false").execute().get('files', [])
        if docs:
            with st.expander(f"📂 Ver {len(docs)} documentos ya enviados"):
                for d in docs: st.write(f"✅ {d['name']}")
    except: pass

    st.markdown("---")
    arc = st.file_uploader("Elige tu factura (PDF o Imagen)", type=['pdf', 'jpg', 'png', 'jpeg'])
    
    if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
        barra = st.progress(0)
        txt_barra = st.empty()
        try:
            txt_barra.text("Iniciando subida...")
            barra.progress(30)
            
            ahora = datetime.datetime.now()
            ref = ahora.strftime('%Y%m%d%H%M%S')
            pref = "EMITIDA" if "EMITIDAS" in cat else "GASTO"
            n_nom = f"{ahora.strftime('%Y-%m-%d')}_{pref}_REF-{ref}{os.path.splitext(arc.name)[1]}"
            
            barra.progress(60)
            txt_barra.text(f"Guardando: {n_nom}")
            
            media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
            service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
            
            barra.progress(100)
            txt_barra.empty()
            st.success(f"¡Hecho! Referencia: {ref}")
            st.balloons() # <--- GLOBOS DE ÉXITO
            st.toast("¡Archivo subido correctamente!", icon='🎉')
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.subheader("Mis Impuestos")
    a_b = st.selectbox("Año de búsqueda:", ["2026", "2025"])
    try:
        id_c = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
        id_a = b_id(a_b, id_c)
        res_folder = service.files().list(q=f"name='IMPUESTOS PRESENTADOS' and '{id_a}' in parents and trashed=false").execute().get('files', [])
        if res_folder:
            imps = service.files().list(q=f"'{res_folder[0]['id']}' in parents and trashed=false").execute().get('files', [])
            for im in imps:
                c_n, c_d = st.columns([0.6, 0.4])
                c_n.write(f"📄 {im['name']}")
                req = service.files().get_media(fileId=im['id'])
                fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req)
                done = False
                while not done: _, done = downloader.next_chunk()
                c_d.download_button("Descargar", fh.getvalue(), file_name=im['name'], key=im['id'])
        else: st.info("No hay archivos en 'IMPUESTOS PRESENTADOS'.")
    except: st.error("Error al acceder a los impuestos.")

with tab3:
    st.subheader("Panel Administrativo")
    if st.text_input("Clave Maestra:", type="password", key="adm_master") == "GEST_LA_2025":
        # 1. TRIMESTRE
        st.write("#### 🗓️ Periodo Activo")
        n_t = st.text_input("Editar trimestre:", value=CONFIG_APP['trimestre_activo'])
        if st.button("ACTUALIZAR TRIMESTRE"):
            CONFIG_APP['trimestre_activo'] = n_t
            guardar_json(CONFIG_FILE, CONFIG_APP); st.rerun()

        st.write("---")
        op = st.radio("Herramienta:", ["Avisos y Estados", "Lecturas", "Clientes Registrados"], horizontal=True)
        
        if op == "Avisos y Estados":
            dest = st.selectbox("Enviar a:", ["TODOS", "CLIENTE INDIVIDUAL"])
            if dest == "TODOS":
                m_g = st.text_area("Aviso Global:", value=DATA_AVISOS["GLOBAL"]["mensaje"])
                if st.button("Enviar a todos"):
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_g}; guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()
            else:
                c_s = st.selectbox("Seleccionar:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                est_n = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                prio_n = st.selectbox("Urgencia:", ["Información", "Urgente", "Trámite finalizado"])
                msg_n = st.text_area("Mensaje privado:")
                if st.button("Actualizar Cliente"):
                    DATA_AVISOS[c_s] = {"estado": est_n, "mensaje": msg_n, "prioridad": prio_n}
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()
        
        elif op == "Lecturas":
            st.write("#### ✅ Confirmaciones de lectura")
            for l in reversed(HISTORIAL_LOG):
                st.write(f"📌 **{l['cliente']}** - {l['fecha']}: {l['msg']}")
        
        elif op == "Clientes Registrados":
            st.write("#### 👥 Clientes en el sistema")
            for em, nom in DICCIONARIO_CLIENTES.items():
                st.write(f"• **{nom}** | `{em}`")
            
            st.write("---")
            st.write("#### ➕ Alta Nueva")
            n_n, n_e = st.text_input("Nombre:"), st.text_input("Email:")
            if st.button("REGISTRAR CLIENTE"):
                if n_n and n_e:
                    DICCIONARIO_CLIENTES[n_e.lower().strip()] = n_n.upper()
                    guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()
            
            st.write("---")
            st.write("#### 🗑️ Eliminar Acceso")
            c_b = st.selectbox("Borrar a:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
            if st.button("ELIMINAR DEFINITIVAMENTE"):
                del DICCIONARIO_CLIENTES[c_b]; guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()
