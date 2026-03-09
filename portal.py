import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered", initial_sidebar_state="collapsed")

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if "user_email" not in st.session_state: st.session_state["user_email"] = None

DB_FILE = "clientes_db.json"
AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"

SMTP_USER = "asesoriaclara0@gmail.com" 
SMTP_PASS = "aucmoslkpgcsbglv" 
URL_PORTAL = "https://asesoriaclara.streamlit.app" 

# --- FUNCIONES ---
def enviar_email(destinatario, nombre_cliente, tipo_mensaje):
    try:
        asunto = f"📢 Aviso de ASESORIACLARA para {nombre_cliente}"
        cuerpo = f"Hola {nombre_cliente},\n\nTienes un nuevo mensaje {tipo_mensaje} en tu portal de cliente.\n\nAccede aquí: {URL_PORTAL}\n\nUn saludo,\nASESORIACLARA."
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

DICCIONARIO_CLIENTES = {}
ID_CARPETA_PROG = "1usBtuwX3xwZmIjojwP2ScUEBWx9vcjmt"

def sincronizar_clientes_drive(service_drive):
    try:
        q = f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents and trashed=false"
        res = service_drive.files().list(q=q).execute().get('files', [])
        if res:
            f_id = res[0]['id']
            cont = service_drive.files().get_media(fileId=f_id).execute().decode('utf-8')
            lineas = cont.strip().split('\n')
            dicc = {}
            for l in lineas:
                if ',' in l:
                    partes = l.split(',')
                    em = partes[0].strip().lower()
                    nom = partes[1].strip().upper()
                    if em != "email":
                        dicc[em] = nom
            return dicc
    except: pass
    return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

def b_id(service_drive, nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service_drive.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service_drive.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    .header-box { background-color: #1e3a8a; padding: 1.5rem 1rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1rem; }
    .status-panel { background: #f8fafc; padding: 12px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; display: inline-block; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN Y CARGA (Antes del login) ---
try:
    with open('token.pickle', 'rb') as t: 
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)
    DICCIONARIO_CLIENTES = sincronizar_clientes_drive(service)
    DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": ""}})
    HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
    CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})
except Exception as e:
    st.error("Error conectando con Google Drive. Revisa el token.")
    st.stop()

# --- 4. LOGIN MAESTRO ---
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    if st.text_input("Contraseña Maestra:", type="password") == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 5. LOGIN EMAIL CLIENTE ---
if st.session_state["user_email"] is None:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Bienvenido al Portal de Clientes</p></div>', unsafe_allow_html=True)
    em_input = st.text_input("Introduce tu email registrado:").lower().strip()
    if st.button("ACCEDER AL PORTAL", use_container_width=True):
        if em_input in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_input
            st.rerun()
        else:
            st.error(f"⚠️ El email '{em_input}' no está autorizado.")
    st.stop()

# --- 6. PORTAL ACTIVO ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES.get(email_act, "CLIENTE")

st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

# Avisos y Estado
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})
if DATA_AVISOS["GLOBAL"].get("mensaje"):
    st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

b_col = "bg-presentado" if config_p['estado'] == "Presentado" else "bg-revision" if config_p['estado'] == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p["estado"]}</span></div>', unsafe_allow_html=True)

# --- 7. PESTAÑAS ---
t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Facturas")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    id_cli = b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_f = b_id(service, t_s, b_id(service, cat, b_id(service, a_s, id_cli)))
    
    arc = st.file_uploader("Subir archivo")
    if arc and st.button("🚀 ENVIAR DOCUMENTO"):
        n_nom = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_{arc.name}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        st.success("¡Archivo enviado con éxito!")

with t2:
    st.subheader("Impuestos Presentados")
    a_b = st.selectbox("Año:", ["2026", "2025"], key="tab2_y")
    id_cli_root = b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_año = b_id(service, a_b, id_cli_root)
    res_f = service.files().list(q=f"name='IMPUESTOS PRESENTADOS' and '{id_año}' in parents and trashed=false").execute().get('files', [])
    if res_f:
        docs = service.files().list(q=f"'{res_f[0]['id']}' in parents and trashed=false").execute().get('files', [])
        for d in docs:
            st.write(f"📄 {d['name']}")

with t4:
    st.subheader("Panel Administrativo")
    if st.text_input("Clave Admin:", type="password") == "GEST_LA_2025":
        opt = st.radio("Sección:", ["Clientes", "Avisos", "Lecturas"], horizontal=True)
        if opt == "Clientes":
            st.write("### Alta de Cliente")
            n_n = st.text_input("Nombre:")
            n_e = st.text_input("Email:").lower().strip()
            if st.button("🚀 GUARDAR EN DRIVE"):
                DICCIONARIO_CLIENTES[n_e] = n_n.upper()
                csv_txt = "\n".join([f"{e},{n}" for e, n in DICCIONARIO_CLIENTES.items()])
                media = MediaIoBaseUpload(io.BytesIO(csv_txt.encode('utf-8')), mimetype='text/csv')
                q_csv = f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents"
                res_csv = service.files().list(q=q_csv).execute().get('files', [])
                if res_csv: service.files().update(fileId=res_csv[0]['id'], media_body=media).execute()
                else: service.files().create(body={'name': 'clientes.csv', 'parents': [ID_CARPETA_PROG]}, media_body=media).execute()
                st.success("Cliente guardado"); st.rerun()

if st.button("CERRAR SESIÓN"):
    st.session_state["user_email"] = None
    st.rerun()





