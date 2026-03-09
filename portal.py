import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS ---
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

st.markdown("""
    <style>
    @media (max-width: 640px) {
        .header-box h1 { font-size: 1.6rem !important; }
        .stButton button { width: 100% !important; height: 3.2rem !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8rem !important; padding: 10px 4px !important; }
    }
    .header-box { background-color: #1e3a8a; padding: 1.5rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1rem; }
    .globo-aviso { border-radius: 15px; padding: 15px; margin: 10px 0; border-left: 8px solid #3b82f6; background: #f0f7ff; color: #1e40af; }
    .status-panel { background: #f8fafc; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 10px; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNCIONES ---
def enviar_email(destinatario, nombre_cliente, mensaje_texto):
    try:
        cuerpo = f"Hola {nombre_cliente},\n\nTienes un nuevo aviso en tu portal:\n\n'{mensaje_texto}'\n\nAccede aquí: {URL_PORTAL}\n\nUn saludo,\nASESORIACLARA."
        msg = MIMEText(cuerpo)
        msg['Subject'] = "📢 AVISO ASESORIACLARA"
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
            dicc = {}
            for l in cont.strip().split('\n'):
                if ',' in l:
                    p = l.split(',')
                    if p[0].strip().lower() != "email": dicc[p[0].strip().lower()] = p[1].strip().upper()
            return dicc
    except: pass
    return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

def b_id(service_drive, nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service_drive.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service_drive.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')

# --- 3. CONEXIÓN ---
try:
    with open('token.pickle', 'rb') as t: creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)
    DICCIONARIO_CLIENTES = sincronizar_clientes_drive(service)
    DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": ""}})
    HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
    CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})
except:
    st.error("Error de conexión.")
    st.stop()

# --- 4. ACCESO ---
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    if st.text_input("Contraseña Maestra:", type="password") == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

if st.session_state["user_email"] is None:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Acceso Clientes</p></div>', unsafe_allow_html=True)
    em_in = st.text_input("Email:").lower().strip()
    if st.button("ENTRAR AL PORTAL"):
        if em_in in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_in
            st.rerun()
        else: st.error("Email no autorizado.")
    st.stop()

# --- 5. PORTAL ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES.get(email_act, "CLIENTE")
st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

# Avisos
config_p = DATA_AVISOS.get(email_act, {"mensaje": "", "estado": "Pendiente"})
if DATA_AVISOS["GLOBAL"].get("mensaje"):
    st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")
if config_p.get("mensaje"):
    st.markdown(f'<div class="globo-aviso"><b>MENSAJE PERSONAL:</b><br>{config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("✅ LEÍDO"):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | Estado: <b>{config_p.get("estado", "Pendiente")}</b></div>', unsafe_allow_html=True)

# --- 6. PESTAÑAS ---
t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Facturas")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    id_cli = b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_f = b_id(service, t_s, b_id(service, cat, b_id(service, a_s, id_cli)))
    
    docs = service.files().list(q=f"'{id_f}' in parents and trashed=false").execute().get('files', [])
    with st.expander(f"📂 Archivos en esta carpeta ({len(docs)})"):
        for d in docs: st.write(f"✅ {d['name']}")
    
    arc = st.file_uploader("Seleccionar archivo:")
    if arc and st.button("🚀 ENVIAR"):
        n_nom = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_{arc.name}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        st.success("¡Enviado!"); st.balloons()

with t2:
    st.subheader("Impuestos")
    a_b = st.selectbox("Año:", ["2026", "2025"], key="t2y")
    id_año = b_id(service, a_b, b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"))
    res_f = service.files().list(q=f"name='IMPUESTOS PRESENTADOS' and '{id_año}' in parents and trashed=false").execute().get('files', [])
    if res_f:
        imp_docs = service.files().list(q=f"'{res_f[0]['id']}' in parents and trashed=false").execute().get('files', [])
        for d in imp_docs:
            st.write(f"📄 {d['name']}")
            req = service.files().get_media(fileId=d['id'])
            fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req); done = False
            while not done: _, done = downloader.next_chunk()
            st.download_button("Descargar", fh.getvalue(), file_name=d['name'], key=d['id'])
    else: st.info("Sin documentos.")

with t3:
    st.subheader("Área Personal")
    id_ap = b_id(service, "AREA PERSONAL", b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"))
    ap_docs = service.files().list(q=f"'{id_ap}' in parents and trashed=false").execute().get('files', [])
    for f in ap_docs:
        st.write(f"📁 {f['name']}")

with t4:
    st.subheader("Administración")
    if st.text_input("Clave Admin:", type="password", key="ad") == "GEST_LA_2025":
        m = st.radio("Menú:", ["Avisos", "Clientes", "Lecturas"], horizontal=True)
        if m == "Avisos":
            dest = st.selectbox("Enviar a:", ["GLOBAL"] + list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES.get(x, x))
            m_txt = st.text_area("Mensaje:")
            est = st.selectbox("Estado del cliente:", ["Pendiente", "En revisión", "Presentado"])
            if st.button("📤 NOTIFICAR"):
                if dest == "GLOBAL":
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_txt}
                    for e, n in DICCIONARIO_CLIENTES.items(): enviar_email(e, n, m_txt)
                else:
                    DATA_AVISOS[dest] = {"mensaje": m_txt, "estado": est}
                    enviar_email(dest, DICCIONARIO_CLIENTES[dest], m_txt)
                guardar_json(AVISOS_FILE, DATA_AVISOS); st.success("Enviado")
        elif m == "Clientes":
            st.write("### Gestión")
            for e, n in DICCIONARIO_CLIENTES.items():
                col1, col2 = st.columns([0.8, 0.2])
                col1.write(f"{n} ({e})")
                if col2.button("🗑️", key=e):
                    del DICCIONARIO_CLIENTES[e]
                    csv_t = "\n".join([f"{em},{no}" for em, no in DICCIONARIO_CLIENTES.items()])
                    res = service.files().list(q=f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents").execute().get('files', [])
                    service.files().update(fileId=res[0]['id'], media_body=MediaIoBaseUpload(io.BytesIO(csv_t.encode('utf-8')), mimetype='text/csv')).execute()
                    st.rerun()
            st.divider()
            nn, ne = st.text_input("Nombre:"), st.text_input("Email:")
            if st.button("➕ AÑADIR"):
                DICCIONARIO_CLIENTES[ne.lower().strip()] = nn.upper()
                csv_t = "\n".join([f"{em},{no}" for em, no in DICCIONARIO_CLIENTES.items()])
                res = service.files().list(q=f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents").execute().get('files', [])
                service.files().update(fileId=res[0]['id'], media_body=MediaIoBaseUpload(io.BytesIO(csv_t.encode('utf-8')), mimetype='text/csv')).execute()
                st.rerun()
        elif m == "Lecturas":
            for l in reversed(HISTORIAL_LOG): st.info(f"✔️ {l['cliente']} leyó ({l['fecha']})")

if st.button("SALIR"):
    st.session_state["user_email"] = None
    st.rerun()

