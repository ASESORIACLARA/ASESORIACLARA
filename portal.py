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

# --- CONFIGURACIÓN EMAIL ---
SMTP_USER = "asesoriaclara0@gmail.com" 
SMTP_PASS = "xxxx xxxx xxxx xxxx" # Tu clave de aplicación
URL_PORTAL = "https://tu-portal.streamlit.app" 

def enviar_email(destinatario, nombre_cliente, tipo_mensaje):
    try:
        asunto = f"📢 Aviso de ASESORIACLARA para {nombre_cliente}"
        cuerpo = f"Hola {nombre_cliente},\n\nTienes un nuevo mensaje {tipo_mensaje} en tu portal.\n\nAccede aquí: {URL_PORTAL}"
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

# --- 2. ESTILOS CSS REFORZADOS (FORMATO MÓVIL) ---
st.markdown("""
    <style>
    @media (max-width: 640px) {
        .stButton button { width: 100% !important; height: 3.8rem !important; font-size: 1.1rem !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8rem !important; padding: 10px 5px !important; }
    }
    .header-box { background-color: #1e3a8a; padding: 1.5rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1.2rem; }
    .header-box p { font-style: italic; opacity: 0.9; margin-top: 5px; font-size: 0.9rem; }
    .status-panel { background: #f8fafc; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; }
    .badge { padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 18px; margin: 12px 0; border-left: 8px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGINS ---
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    if st.text_input("Contraseña Maestra:", type="password") == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

if st.session_state["user_email"] is None:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    em = st.text_input("Email registrado:")
    if st.button("ACCEDER", use_container_width=True):
        if em.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em.lower().strip()
            st.rerun()
    st.stop()

# --- 4. PORTAL ACTIVO ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})

st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

if DATA_AVISOS["GLOBAL"].get("mensaje"): st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")
if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    st.markdown(f'<div class="globo-aviso {"aviso-urgente" if prio=="Urgente" else "aviso-info"}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("MARCAR LEÍDO ✓", use_container_width=True):
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

# --- 6. TABS ---
t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 ÁREA PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir documentación")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    id_cli = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_f = b_id(t_s, b_id(cat, b_id(a_s, id_cli)))
    
    docs = service.files().list(q=f"'{id_f}' in parents and trashed=false").execute().get('files', [])
    if docs:
        with st.expander(f"📂 Archivos en esta carpeta ({len(docs)})"):
            for d in docs: st.write(f"✅ {d['name']}")
    
    arc = st.file_uploader("Subir archivo")
    if arc and st.button("🚀 ENVIAR"):
        n_nom = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_{cat[:4]}_REF-{datetime.datetime.now().strftime('%H%M%S')}{os.path.splitext(arc.name)[1]}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        st.success("¡Enviado!"); st.balloons()

with t2:
    st.subheader("Mis Impuestos")
    # Lógica de descarga igual...
    
with t3:
    st.subheader("📁 Área Personal")
    id_root = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    res_ap = service.files().list(q=f"name='AREA PERSONAL' and '{id_root}' in parents and trashed=false").execute().get('files', [])
    if res_ap:
        files = service.files().list(q=f"'{res_ap[0]['id']}' in parents and trashed=false").execute().get('files', [])
        for f in files:
            c1, c2 = st.columns([0.7, 0.3])
            c1.write(f"📄 {f['name']}")
            req = service.files().get_media(fileId=f['id'])
            fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req); done = False
            while not done: _, done = downloader.next_chunk()
            c2.download_button("Bajar", fh.getvalue(), file_name=f['name'], key="ap_"+f['id'])
    else: st.info("Sin archivos personales aún.")

with t4:
    st.subheader("Panel Administrativo")
    if st.text_input("Clave Admin:", type="password", key="adm_key") == "GEST_LA_2025":
        opt = st.radio("Menú:", ["Avisos/Estados", "Clientes", "Lecturas Confirmadas"], horizontal=True)
        
        if opt == "Avisos/Estados":
            dest = st.selectbox("Destino:", ["GLOBAL", "INDIVIDUAL"])
            m_txt = st.text_area("Mensaje:")
            if dest == "INDIVIDUAL":
                c_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                est_n = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                prio_n = st.selectbox("Urgencia:", ["Información", "Urgente"])
                if st.button("ENVIAR Y NOTIFICAR"):
                    DATA_AVISOS[c_sel] = {"mensaje": m_txt, "estado": est_n, "prioridad": prio_n}
                    guardar_json(AVISOS_FILE, DATA_AVISOS)
                    enviar_email(c_sel, DICCIONARIO_CLIENTES[c_sel], "personal")
                    st.success("Actualizado."); st.rerun()
            else:
                if st.button("PUBLICAR GLOBAL"):
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_txt}
                    guardar_json(AVISOS_FILE, DATA_AVISOS)
                    for e, n in DICCIONARIO_CLIENTES.items(): enviar_email(e, n, "global")
                    st.success("Aviso global enviado."); st.rerun()

        elif opt == "Clientes":
            for e, n in DICCIONARIO_CLIENTES.items(): st.write(f"• **{n}** ({e})")
            n_n = st.text_input("Nombre:"); n_e = st.text_input("Email:")
            if st.button("DAR DE ALTA"):
                DICCIONARIO_CLIENTES[n_e.lower().strip()] = n_n.upper()
                guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()
            c_borrar = st.selectbox("Borrar a:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
            if st.button("BORRAR"):
                del DICCIONARIO_CLIENTES[c_borrar]; guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()

        elif opt == "Lecturas Confirmadas":
            for log in reversed(HISTORIAL_LOG):
                st.write(f"✔️ **{log['cliente']}** - {log['fecha']}")
                st.caption(f"Mensaje: {log['msg']}")

if st.button("CERRAR SESIÓN TOTAL"):
    st.session_state["user_email"] = None
    st.rerun()
