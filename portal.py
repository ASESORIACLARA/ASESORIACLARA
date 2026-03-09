import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS MÓVILES ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if "user_email" not in st.session_state: st.session_state["user_email"] = None

AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"
SMTP_USER = "asesoriaclara0@gmail.com" 
SMTP_PASS = "aucmoslkpgcsbglv" 
URL_PORTAL = "https://asesoriaclara.streamlit.app"
ID_CARPETA_PROG = "1usBtuwX3xwZmIjojwP2ScUEBWx9vcjmt"

# DISEÑO ESPECIAL PARA MÓVILES
st.markdown("""
    <style>
    /* Ajustes generales para móvil */
    @media (max-width: 640px) {
        .header-box h1 { font-size: 1.6rem !important; }
        .header-box p { font-size: 0.8rem !important; }
        .stButton button { width: 100% !important; height: 3.5rem !important; font-size: 1.1rem !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.85rem !important; padding: 10px 5px !important; }
        .stTextInput input { font-size: 1rem !important; }
    }
    
    /* Estilos visuales */
    .header-box { 
        background-color: #1e3a8a; 
        padding: 1.5rem 1rem; 
        border-radius: 20px; 
        text-align: center; 
        color: white; 
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-box h1 { margin: 0; font-weight: 800; letter-spacing: -0.5px; }
    .header-box p { font-style: italic; opacity: 0.8; margin-top: 5px; }
    
    .globo-aviso { 
        border-radius: 15px; 
        padding: 18px; 
        margin: 15px 0; 
        border-left: 10px solid #3b82f6; 
        background: #f0f7ff; 
        color: #1e40af;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* Separadores limpios */
    hr { margin: 2rem 0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNCIONES MOTOR ---
def enviar_email(destinatario, nombre_cliente, mensaje_texto):
    try:
        cuerpo = f"Hola {nombre_cliente},\n\nTienes un nuevo aviso en tu portal:\n\n'{mensaje_texto}'\n\nAccede aquí: {URL_PORTAL}\n\nASESORIACLARA."
        msg = MIMEText(cuerpo)
        msg['Subject'] = "📢 AVISO IMPORTANTE - ASESORIACLARA"
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        server.quit()
    except: pass

def cargar_json(archivo, inicial):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f: return json.load(f)
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f: json.dump(datos, f, indent=4, ensure_ascii=False)

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
                    p = l.split(',')
                    dicc[p[0].strip().lower()] = p[1].strip().upper()
            return dicc
    except: pass
    return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

def b_id(service_drive, nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service_drive.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service_drive.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')

# --- 3. CONEXIÓN DRIVE ---
try:
    with open('token.pickle', 'rb') as t: creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)
    DICCIONARIO_CLIENTES = sincronizar_clientes_drive(service)
    DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": ""}})
    HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
except:
    st.error("Error conectando con la base de datos.")
    st.stop()

# --- 4. FLUJO DE INICIO ---
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    pw = st.text_input("Contraseña Maestra:", type="password")
    if pw == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

if st.session_state["user_email"] is None:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Acceso Clientes</p></div>', unsafe_allow_html=True)
    em_in = st.text_input("Email registrado:").lower().strip()
    if st.button("ENTRAR AL PORTAL"):
        if em_in in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_in
            st.rerun()
        else:
            st.error("Email no autorizado.")
    st.stop()

# --- 5. PORTAL ACTIVO ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES.get(email_act, "CLIENTE")

st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

# Sección Avisos
config_p = DATA_AVISOS.get(email_act, {"mensaje": ""})
if DATA_AVISOS["GLOBAL"].get("mensaje"):
    st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    st.markdown(f'<div class="globo-aviso"><b>MENSAJE PERSONAL:</b><br>{config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("✅ MARCAR COMO LEÍDO"):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""
        DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS)
        st.rerun()

# --- 6. PESTAÑAS ---
t1, t4 = st.tabs(["📤 SUBIR", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Documentos")
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    arc = st.file_uploader("Toca para elegir archivo:")
    if arc and st.button("🚀 ENVIAR DOCUMENTO"):
        n_nom = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_{arc.name}"
        id_cli = b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
        id_f = b_id(service, "2026", b_id(service, cat, id_cli))
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        st.success("¡Enviado!"); st.balloons()

with t4:
    st.subheader("Administración")
    if st.text_input("Clave Admin:", type="password", key="adm") == "GEST_LA_2025":
        m_opt = st.radio("Menú:", ["Avisos", "Historial", "Clientes"], horizontal=True)
        
        if m_opt == "Avisos":
            dest = st.selectbox("Enviar a:", ["GLOBAL"] + list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES.get(x, x))
            m_txt = st.text_area("Mensaje:")
            if st.button("📤 NOTIFICAR AHORA"):
                if dest == "GLOBAL":
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_txt}
                    for e, n in DICCIONARIO_CLIENTES.items(): enviar_email(e, n, m_txt)
                else:
                    DATA_AVISOS[dest] = {"mensaje": m_txt}
                    enviar_email(dest, DICCIONARIO_CLIENTES[dest], m_txt)
                guardar_json(AVISOS_FILE, DATA_AVISOS)
                st.success("Aviso y email enviados.")

        elif m_opt == "Historial":
            for l in reversed(HISTORIAL_LOG):
                st.info(f"✔️ {l['cliente']} leyó el aviso ({l['fecha']})")

if st.button("CERRAR SESIÓN"):
    st.session_state["user_email"] = None
    st.rerun()
