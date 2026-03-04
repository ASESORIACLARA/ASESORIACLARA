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

# --- 3. DISEÑO INTERNO ---
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
        else: st.error("Email no encontrado.")
    st.stop()

# --- SESIÓN ACTIVA ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información", "fecha": ""})

# Avisos
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

# Estado y Trimestre
b_col = "bg-presentado" if config_p.get('estado') == "Presentado" else "bg-revision" if config_p.get('estado') == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p.get("estado")}</span></div>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

with tab1:
    st.subheader("Subir Facturación")
    # (Lógica de subida y listado ya enviada anteriormente...)
    pass

with tab2:
    st.subheader("📥 Mis Impuestos")
    # (Lógica de descarga ya enviada anteriormente...)
    pass

with tab3:
    st.subheader("⚙️ Panel de Gestión")
    ad_p = st.text_input("Clave Administrativa:", type="password", key="panel_admin")
    if ad_p == PASSWORD_ADMIN:
        
        # 1. CONFIGURACIÓN GLOBAL
        st.markdown("#### 🛠️ Configuración General")
        trim_edit = st.text_input("Trimestre actual visible para todos:", value=CONFIG_APP['trimestre_activo'])
        if st.button("ACTUALIZAR PERIODO"):
            CONFIG_APP['trimestre_activo'] = trim_edit
            guardar_json(CONFIG_FILE, CONFIG_APP); st.success("Cambiado."); st.rerun()

        st.markdown("---")

        # 2. SECCIONES DE GESTIÓN
        op_gest = st.radio("Herramientas:", ["Avisos y Estados", "Registro de Lectura", "Base de Clientes"], horizontal=True)

        if op_gest == "Avisos y Estados":
            st.write("### 📢 Control de Avisos")
            dest = st.selectbox("Destinatario:", ["A TODOS (Global)", "UN CLIENTE (Personal)"])
            
            if dest == "A TODOS (Global)":
                msg_g = st.text_area("Mensaje para todos los clientes:", value=DATA_AVISOS["GLOBAL"]["mensaje"])
                if st.button("Publicar Global"):
                    DATA_AVISOS["GLOBAL"] = {"mensaje": msg_g, "fecha": datetime.datetime.now().strftime('%d/%m/%Y')}
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.success("Aviso global actualizado."); st.rerun()
            else:
                cli_sel = st.selectbox("Seleccionar Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                col_e, col_p = st.columns(2)
                nuevo_est = col_e.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                nueva_prio = col_p.selectbox("Prioridad Globo:", ["Información", "Urgente", "Trámite finalizado"])
                nuevo_msg = st.text_area("Mensaje personal para este cliente:")
                
                if st.button("Actualizar Cliente"):
                    DATA_AVISOS[cli_sel] = {
                        "estado": nuevo_est,
                        "mensaje": nuevo_msg,
                        "prioridad": nueva_prio,
                        "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                    guardar_json(AVISOS_FILE, DATA_AVISOS); st.success("Datos actualizados."); st.rerun()

        elif op_gest == "Registro de Lectura":
            st.write("### ✅ Confirmaciones de 'Entendido'")
            if HISTORIAL_LOG:
                for reg in reversed(HISTORIAL_LOG):
                    st.write(f"📌 **{reg['cliente']}** leyó su aviso el **{reg['fecha']}**")
                    st.caption(f"Mensaje leído: {reg['msg']}")
            else: st.info("No hay lecturas registradas.")

        elif op_gest == "Base de Clientes":
            st.write("### 👥 Gestión de Clientes")
            # Añadir Cliente
            with st.expander("Añadir nuevo cliente"):
                nuevo_n = st.text_input("Nombre Completo:")
                nuevo_e = st.text_input("Email:")
                if st.button("Registrar Cliente"):
                    DICCIONARIO_CLIENTES[nuevo_e.lower().strip()] = nuevo_n.upper()
                    guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.success("Añadido."); st.rerun()
            
            # Borrar Cliente
            with st.expander("Eliminar cliente"):
                cli_del = st.selectbox("Borrar a:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                if st.button("CONFIRMAR ELIMINACIÓN"):
                    del DICCIONARIO_CLIENTES[cli_del]
                    guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()

