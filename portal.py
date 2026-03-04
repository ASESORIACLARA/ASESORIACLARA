import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS (SEGURIDAD CONTRA ERRORES) ---
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
                # Auto-reparación de estructura si falta GLOBAL
                if archivo == AVISOS_FILE and "GLOBAL" not in datos:
                    datos["GLOBAL"] = {"mensaje": "", "fecha": ""}
                return datos
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# Inicialización de datos
DICCIONARIO_CLIENTES = cargar_json(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": "", "fecha": ""}})
HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})

# --- 2. LOGIN CON ESTÉTICA ORIGINAL Y FRASE ---
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

# --- 3. DISEÑO INTERNO Y ESTILOS ---
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
    </style>
    <div class="header-box">
        <h1>ASESORIACLARA</h1>
        <p>Tu gestión, más fácil y transparente</p>
    </div>
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

# Datos del cliente actual
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información", "fecha": ""})

# Logout y Aviso Global
c_out1, c_out2 = st.columns([0.7, 0.3])
c_out1.markdown(f'<div style="background:#e8f0fe; padding:8px; border-radius:10px; color:#1e3a8a; font-weight:bold; text-align:center;">👤 {nombre_act}</div>', unsafe_allow_html=True)
if c_out2.button("SALIR", use_container_width=True):
    del st.session_state["user_email"]; st.rerun()

if DATA_AVISOS.get("GLOBAL", {}).get("mensaje"):
    st.info(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

# Globo Personal con Historial de Lectura
if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    est_clase = "aviso-urgente" if prio == "Urgente" else "aviso-finalizado" if "finalizado" in prio else "aviso-info"
    st.markdown(f'<div class="globo-aviso {est_clase}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("ENTENDIDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

# Estado dinámico
b_col = "bg-presentado" if config_p.get('estado') == "Presentado" else "bg-revision" if config_p.get('estado') == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo Actual: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p.get("estado")}</span></div>', unsafe_allow_html=True)

# --- 4. FUNCIONES DE DRIVE ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

def buscar_o_crear_id(nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    else:
        meta = {'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}
        return service.files().create(body=meta, fields='id').execute().get('id')

# --- 5. TABS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

with tab1:
    st.subheader("Subir Documentación")
    c1, c2 = st.columns(2)
    a_sel, t_sel = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    tipo_sel = st.radio("Tipo de factura:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    # Listar lo que ya hay en Drive
    try:
        id_cli = buscar_o_crear_id(nombre_act, ID_CARPETA_CLIENTES)
        id_final = buscar_o_crear_id(t_sel, buscar_o_crear_id(tipo_sel, buscar_o_crear_id(a_sel, id_cli)))
        st.write(f"📂 **Documentos enviados en {t_sel}:**")
        archivos_en_drive = service.files().list(q=f"'{id_final}' in parents and trashed=false").execute().get('files', [])
        if archivos_en_drive:
            for d in archivos_en_drive: st.write(f"- <small>{d['name']}</small>", unsafe_allow_html=True)
        else: st.info("No hay archivos subidos todavía.")
    except: st.error("Error al conectar con las carpetas.")

    st.markdown("---")
    arc = st.file_uploader("Elegir archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
    if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
        ahora = datetime.datetime.now()
        ref = ahora.strftime('%Y%m%d%H%M%S')
        prefijo = "EMITIDA" if "EMITIDAS" in tipo_sel else "GASTO"
        nuevo_nombre = f"{ahora.strftime('%Y-%m-%d')}_{prefijo}_REF-{ref}{os.path.splitext(arc.name)[1]}"
        
        m_meta = {'name': nuevo_nombre, 'parents': [id_final]}
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body=m_meta, media_body=media).execute()
        
        st.toast(f"✅ Recibido: {nuevo_nombre}", icon='📂')
        st.success(f"¡Documento enviado con éxito! Referencia: {ref}")
        st.balloons()

with tab2:
    st.subheader("📥 Mis Impuestos Presentados")
    a_bus = st.selectbox("Seleccionar el Año:", ["2026", "2025"])
    try:
        id_c = buscar_o_crear_id(nombre_act, ID_CARPETA_CLIENTES)
        id_a = buscar_o_crear_id(a_bus, id_c)
        q_imp = f"name = 'IMPUESTOS PRESENTADOS' and '{id_a}' in parents and trashed = false"
        res_folder = service.files().list(q=q_imp).execute().get('files', [])
        if res_folder:
            id_f_imp = res_folder[0]['id']
            imptos = service.files().list(q=f"'{id_f_imp}' in parents and trashed = false").execute().get('files', [])
            if imptos:
                for imp in imptos:
                    col_a, col_b = st.columns([0.7, 0.3])
                    col_a.write(f"📄 {imp['name']}")
                    req_m = service.files().get_media(fileId=imp['id'])
                    fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req_m)
                    done = False
                    while not done: _, done = downloader.next_chunk()
                    col_b.download_button("Bajar", fh.getvalue(), file_name=imp['name'], key=imp['id'], use_container_width=True)
            else: st.info("Todavía no hay modelos subidos en esta carpeta.")
        else: st.warning("Carpeta 'IMPUESTOS PRESENTADOS' no encontrada.")
    except: st.error("No se pudo acceder a la sección de impuestos.")

with tab3:
    st.subheader("⚙️ Panel de Gestión")
    ad_pass = st.text_input("Clave Administrativa:", type="password", key="p_adm_final")
    if ad_pass == PASSWORD_ADMIN:
        
        # 1. Trimestre
        st.markdown("#### 🛠️ Configuración General")
        t_edit = st.text_input("Trimestre visible para todos:", value=CONFIG_APP['trimestre_activo'])
        if st.button("GUARDAR NUEVO TRIMESTRE"):
            CONFIG_APP['trimestre_activo'] = t_edit
            guardar_json(CONFIG_FILE, CONFIG_APP); st.success("Cambiado."); st.rerun()

        st.markdown("---")
        herramienta = st.radio("Seleccionar Herramienta:", ["Avisos y Estados", "Historial Lecturas", "Alta Clientes"], horizontal=True)

        if herramienta == "Avisos y Estados":
            d_dest = st.selectbox("Destino:", ["GLOBAL", "PERSONAL"])
            if d_dest == "GLOBAL":
                m_g = st.text_area("Mensaje global:", value=DATA_AVISOS["GLOBAL"]["mensaje"])
                if st.button("Actualizar para todos"):
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_g, "fecha": datetime.datetime.now().strftime('%d/%m/%Y')}
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()
            else:
                c_s = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                col_1, col_2 = st.columns(2)
                e_n = col_1.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                p_n = col_2.selectbox("Prioridad:", ["Información", "Urgente", "Trámite finalizado"])
                m_p = st.text_area("Mensaje personal:")
                if st.button("Actualizar este cliente"):
                    DATA_AVISOS[c_s] = {"estado": e_n, "mensaje": m_p, "prioridad": p_n, "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

        elif herramienta == "Historial Lecturas":
            st.write("### ✅ Registro de 'Entendido'")
            for h in reversed(HISTORIAL_LOG):
                st.write(f"📌 **{h['cliente']}** - {h['fecha']}: {h['msg']}")

        elif herramienta == "Alta Clientes":
            st.write("### 👥 Gestionar Base de Datos")
            with st.expander("Añadir Nuevo"):
                n_n = st.text_input("Nombre Completo:")
                n_e = st.text_input("Email:")
                if st.button("Registrar"):
                    DICCIONARIO_CLIENTES[n_e.lower().strip()] = n_n.upper()
                    guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()
            with st.expander("Eliminar"):
                c_d = st.selectbox("Borrar a:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                if st.button("CONFIRMAR BORRADO"):
                    del DICCIONARIO_CLIENTES[c_d]; guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()

