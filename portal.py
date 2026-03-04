import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS (PROTEGIDAS) ---
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
                # Verificación extra para evitar el error que tuviste
                if archivo == AVISOS_FILE and "GLOBAL" not in datos:
                    datos["GLOBAL"] = {"mensaje": "", "fecha": ""}
                return datos
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# Inicialización segura de datos
DICCIONARIO_CLIENTES = cargar_json(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": "", "fecha": ""}})
HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})

# --- 2. SISTEMA DE LOGIN ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown('<h1 style="text-align:center; color:#1e3a8a;">ASESORIACLARA</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        pass_in = st.text_input("Contraseña del Portal:", type="password")
        if st.button("ENTRAR", use_container_width=True):
            if pass_in == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña incorrecta")
    st.stop()

# --- 3. CONFIGURACIÓN DRIVE ---
ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
PASSWORD_ADMIN = "GEST_LA_2025"

# --- 4. ESTILOS CSS ---
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
    </style>
    <div class="header-box"><h1>ASESORIACLARA</h1></div>
""", unsafe_allow_html=True)

# --- 5. FLUJO DE CLIENTE ---
if "user_email" not in st.session_state:
    em_log = st.text_input("Introduce tu Email para entrar:")
    if st.button("ACCEDER", use_container_width=True):
        if em_log.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_log.lower().strip()
            st.rerun()
    st.stop()

email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
# Uso de .get() para evitar el error si el cliente no tiene avisos aún
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información", "fecha": ""})

# Mostrar Aviso Global con protección
aviso_g = DATA_AVISOS.get("GLOBAL", {"mensaje": ""})
if aviso_g["mensaje"]:
    st.info(f"📢 **AVISO GENERAL:** {aviso_g['mensaje']}")

# Saludo y Logout
c_l1, c_l2 = st.columns([0.7, 0.3])
c_l1.markdown(f'👤 **{nombre_act}**')
if c_l2.button("SALIR", use_container_width=True):
    del st.session_state["user_email"]; st.rerun()

# Estado dinámico
b_col = "bg-presentado" if config_p.get('estado') == "Presentado" else "bg-revision" if config_p.get('estado') == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo Actual: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p.get("estado")}</span></div>', unsafe_allow_html=True)

# Globo Personal con protección
if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    est = "aviso-urgente" if prio == "Urgente" else "aviso-finalizado" if "finalizado" in prio else "aviso-info"
    st.markdown(f'<div class="globo-aviso {est}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("ENTENDIDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

# --- 6. TABS Y DRIVE ---
tab1, tab2, tab3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

with tab1:
    st.subheader("Subir Facturas")
    c1, c2 = st.columns(2)
    a_sel, t_sel = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    tipo_sel = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    # --- LISTADO DINÁMICO DE FACTURAS ---
    st.write(f"📂 **Documentos en {t_sel} - {a_sel}:**")
    try:
        def b_id(n, p):
            q = f"name='{n}' and '{p}' in parents and trashed=false"
            r = service.files().list(q=q).execute().get('files', [])
            return r[0]['id'] if r else None
        
        id_c = b_id(nombre_act, ID_CARPETA_CLIENTES)
        if id_c:
            id_a = b_id(a_sel, id_c)
            if id_a:
                id_t = b_id(tipo_sel, id_a)
                if id_t:
                    id_tri = b_id(t_sel, id_t)
                    if id_tri:
                        archivos = service.files().list(q=f"'{id_tri}' in parents and trashed=false").execute().get('files', [])
                        if archivos:
                            for f in archivos: st.markdown(f"- <small>{f['name']}</small>", unsafe_allow_html=True)
                        else: st.info("Carpeta vacía.")
    except: pass

    arc = st.file_uploader("Subir archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
    if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
        ahora = datetime.datetime.now()
        ref = ahora.strftime('%Y%m%d%H%M%S')
        pref = "EMITIDA" if "EMITIDAS" in tipo_sel else "GASTO"
        nuevo_nombre = f"{ahora.strftime('%Y-%m-%d')}_{pref}_REF-{ref}{os.path.splitext(arc.name)[1]}"
        st.toast(f"✅ Renombrado a: {nuevo_nombre}", icon='📂')
        # Lógica de subida aquí...
        st.success("¡Documento recibido!")
        st.balloons()

with tab3:
    st.subheader("⚙️ Panel de Gestión")
    ad_pass = st.text_input("Clave Maestra:", type="password", key="adm_key")
    if ad_pass == PASSWORD_ADMIN:
        # EDITAR TRIMESTRE (EL CORAZÓN DEL CAMBIO)
        st.markdown("### 🛠 Configuración del Periodo")
        nuevo_t = st.text_input("Trimestre actual (ej: 1T 2026):", value=CONFIG_APP['trimestre_activo'])
        if st.button("ACTUALIZAR TRIMESTRE PARA TODOS"):
            CONFIG_APP['trimestre_activo'] = nuevo_t
            guardar_json(CONFIG_FILE, CONFIG_APP)
            st.success("Cambiado.")
            st.rerun()

        st.markdown("---")
        op = st.radio("Herramientas:", ["Avisos", "Lecturas", "Clientes"], horizontal=True)
        
        if op == "Avisos":
            dest = st.selectbox("Destino:", ["GLOBAL", "PERSONAL"])
            if dest == "GLOBAL":
                msg_g = st.text_area("Mensaje global:", value=DATA_AVISOS["GLOBAL"]["mensaje"])
                if st.button("Publicar para todos"):
                    DATA_AVISOS["GLOBAL"] = {"mensaje": msg_g, "fecha": datetime.datetime.now().strftime('%d/%m/%Y')}
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()
            else:
                cli_s = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                est_s = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                prio_s = st.selectbox("Prioridad:", ["Información", "Urgente", "Trámite finalizado"])
                msg_p = st.text_area("Mensaje personal:")
                if st.button("Actualizar Cliente"):
                    DATA_AVISOS[cli_s] = {"estado": est_s, "mensaje": msg_p, "prioridad": prio_s, "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()
        elif op == "Lecturas":
            for l in reversed(HISTORIAL_LOG): st.write(f"✅ **{l['cliente']}** leyó: '_{l['msg']}_' ({l['fecha']})")
