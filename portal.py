import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered", initial_sidebar_state="collapsed")

DB_FILE = "clientes_db.json"
AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"

# --- CONFIGURACIÓN EMAIL (ESTO DEBE ESTAR CORRECTO PARA RECIBIR EMAILS) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "asesoriaclara0@gmail.com" # Su correo
SMTP_PASS = "xxxx xxxx xxxx xxxx"      # ¡IMPORTANTE! Su "Contraseña de Aplicación" de Google
URL_PORTAL = "https://tu-portal.streamlit.app" 

def enviar_email(destinatario, nombre_cliente, tipo_mensaje):
    try:
        asunto = f"📢 Aviso de ASESORIACLARA para {nombre_cliente}"
        cuerpo = f"""
        Hola {nombre_cliente},
        
        Tienes un nuevo mensaje {tipo_mensaje} en tu portal de cliente.
        
        Puedes acceder aquí: {URL_PORTAL}
        
        Un saludo,
        ASESORIACLARA.
        """
        msg = MIMEText(cuerpo)
        msg['Subject'] = asunto
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar email: {e}")
        return False

def cargar_json(archivo, inicial):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f: return json.load(f)
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

DICCIONARIO_CLIENTES = cargar_json(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": ""}})
HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    @media (max-width: 640px) { .stButton button { width: 100% !important; height: 3.5rem !important; } }
    .header-box { background-color: #1e3a8a; padding: 2rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1rem; }
    .status-panel { background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 10px; }
    .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 8px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1></div>', unsafe_allow_html=True)
    if st.text_input("Contraseña Maestra:", type="password") == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

if "user_email" not in st.session_state:
    em_log = st.text_input("Email registrado:")
    if st.button("ENTRAR"):
        if em_log.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_log.lower().strip()
            st.rerun()
    st.stop()

email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})

# --- 4. INTERFAZ ---
st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

if st.button("SALIR"): del st.session_state["user_email"]; st.rerun()

if DATA_AVISOS["GLOBAL"].get("mensaje"): st.warning(f"📢 **AVISO:** {DATA_AVISOS['GLOBAL']['mensaje']}")
if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    st.markdown(f'<div class="globo-aviso {"aviso-urgente" if prio=="Urgente" else "aviso-info"}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("MARCAR LEÍDO ✓"):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

b_col = "bg-presentado" if config_p['estado'] == "Presentado" else "bg-revision" if config_p['estado'] == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p["estado"]}</span></div>', unsafe_allow_html=True)

# --- 5. DRIVE ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

def b_id(nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')

t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 ÁREA PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Facturas")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Categoría:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    # --- FUNCIÓN RESTAURADA: VER DOCUMENTOS YA ENVIADOS ---
    try:
        id_cli = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
        id_f = b_id(t_s, b_id(cat, b_id(a_s, id_cli)))
        docs = service.files().list(q=f"'{id_f}' in parents and trashed=false").execute().get('files', [])
        if docs:
            with st.expander(f"📂 Ver archivos ya enviados en esta carpeta ({len(docs)})"):
                for d in docs: st.write(f"✅ {d['name']}")
    except: pass

    arc = st.file_uploader("Subir archivo")
    if arc and st.button("🚀 ENVIAR"):
        ahora = datetime.datetime.now()
        n_nom = f"{ahora.strftime('%Y-%m-%d')}_{cat[:4]}_REF-{ahora.strftime('%H%M%S')}{os.path.splitext(arc.name)[1]}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        st.success("¡Enviado!"); st.balloons()

with t2:
    st.subheader("Impuestos")
    # Lógica de descarga... (Misma que Código Maestro anterior)

with t3:
    st.subheader("📁 Área Personal")
    # Lógica de descarga Área Personal... (Misma que Código Maestro anterior)

with t4:
    st.subheader("Gestión")
    if st.text_input("Clave Admin:", type="password") == "GEST_LA_2025":
        opt = st.radio("Herramienta:", ["Avisos", "Clientes", "Lecturas"], horizontal=True)
        if opt == "Avisos":
            cli_dest = st.selectbox("Enviar a:", ["TODOS", "INDIVIDUAL"])
            m_txt = st.text_area("Mensaje:")
            if st.button("PUBLICAR Y NOTIFICAR POR EMAIL"):
                if cli_dest == "TODOS":
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_txt}
                    for e, n in DICCIONARIO_CLIENTES.items(): enviar_email(e, n, "global")
                else:
                    c_e = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                    DATA_AVISOS[c_e] = {"mensaje": m_txt, "estado": "En revisión", "prioridad": "Información"}
                    enviar_email(c_e, DICCIONARIO_CLIENTES[c_e], "personal")
                guardar_json(AVISOS_FILE, DATA_AVISOS); st.success("Aviso y emails enviados."); st.rerun()
