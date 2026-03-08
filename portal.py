import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered", initial_sidebar_state="collapsed")

# Inicializar estados de sesión para evitar saltos de pantalla
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if "user_email" not in st.session_state: st.session_state["user_email"] = None

DB_FILE = "clientes_db.json"
AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"

# --- CONFIGURACIÓN EMAIL ---
SMTP_USER = "asesoriaclara0@gmail.com" 
SMTP_PASS = "xxxx xxxx xxxx xxxx" # Tu clave de aplicación de 16 letras
URL_PORTAL = "https://tu-portal.streamlit.app" 

def enviar_email(destinatario, nombre_cliente, tipo_mensaje):
    try:
        asunto = f"📢 Aviso de ASESORIACLARA para {nombre_cliente}"
        cuerpo = f"Hola {nombre_cliente},\n\nTienes un nuevo mensaje {tipo_mensaje} en tu portal.\n\n{URL_PORTAL}"
        msg = MIMEText(cuerpo)
        msg['Subject'] = asunto
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        server.quit()
        return True
    except: return False

def cargar_json(archivo, inicial):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f: return json.load(f)
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f: json.dump(datos, f, indent=4, ensure_ascii=False)

DICCIONARIO_CLIENTES = cargar_json(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": ""}})
HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    .header-box { background-color: #1e3a8a; padding: 1.5rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1rem; }
    .status-panel { background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 10px; }
    .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; color: white; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 8px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ESTABLE ---
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1></div>', unsafe_allow_html=True)
    pw = st.text_input("Contraseña Maestra:", type="password")
    if st.button("ENTRAR"):
        if pw == "clara2026": 
            st.session_state["password_correct"] = True
            st.rerun()
    st.stop()

if st.session_state["user_email"] is None:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Acceso Clientes</p></div>', unsafe_allow_html=True)
    em = st.text_input("Introduce tu email registrado:")
    if st.button("CONECTAR"):
        if em.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em.lower().strip()
            st.rerun()
        else: st.error("Email no reconocido")
    st.stop()

# --- 4. PORTAL ACTIVO ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})

st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Bienvenida, {nombre_act}</p></div>', unsafe_allow_html=True)

# --- 5. DRIVE ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

def b_id(nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')

# --- TABS ---
t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 ÁREA PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Facturas")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Categoría:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    id_cli = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_f = b_id(t_s, b_id(cat, b_id(a_s, id_cli)))
    
    docs = service.files().list(q=f"'{id_f}' in parents and trashed=false").execute().get('files', [])
    if docs:
        with st.expander(f"📂 Ver archivos enviados ({len(docs)})"):
            for d in docs: st.write(f"✅ {d['name']}")

    arc = st.file_uploader("Subir factura")
    if arc and st.button("🚀 ENVIAR"):
        n_nom = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_{cat[:4]}_REF-{datetime.datetime.now().strftime('%H%M%S')}{os.path.splitext(arc.name)[1]}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        st.success("¡Enviado!"); st.balloons()

with t3:
    st.subheader("📁 Mi Área Personal")
    st.write("Documentos compartidos por tu asesora.")
    
    # BUSQUEDA REFORZADA DE CARPETA
    id_cli_root = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    q_ap = f"name='AREA PERSONAL' and '{id_cli_root}' in parents and trashed=false"
    res_ap = service.files().list(q=q_ap).execute().get('files', [])
    
    if res_ap:
        folder_id = res_ap[0]['id']
        archivos = service.files().list(q=f"'{folder_id}' in parents and trashed=false").execute().get('files', [])
        if archivos:
            for a in archivos:
                col1, col2 = st.columns([0.7, 0.3])
                col1.write(f"📄 {a['name']}")
                # Descarga
                req = service.files().get_media(fileId=a['id'])
                fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req)
                done = False
                while not done: _, done = downloader.next_chunk()
                col2.download_button("Bajar", fh.getvalue(), file_name=a['name'], key=a['id'])
        else:
            st.info("La carpeta 'AREA PERSONAL' está vacía.")
    else:
        st.warning("Aún no tienes creada la carpeta 'AREA PERSONAL' en Drive.")

with t4:
    # (Aquí iría todo el Panel de Gestión, avisos, lecturas y alta de clientes igual que antes)
    if st.button("CERRAR SESIÓN"):
        st.session_state["user_email"] = None
        st.rerun()
