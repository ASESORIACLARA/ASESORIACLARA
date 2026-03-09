import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered", initial_sidebar_state="collapsed")

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if "user_email" not in st.session_state: st.session_state["user_email"] = None

# Archivos locales de respaldo para avisos y configuración
AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"

SMTP_USER = "asesoriaclara0@gmail.com" 
SMTP_PASS = "aucmoslkpgcsbglv" 
URL_PORTAL = "https://asesoriaclara.streamlit.app" 
ID_CARPETA_PROG = "1usBtuwX3xwZmIjojwP2ScUEBWx9vcjmt"

# --- FUNCIONES DE APOYO ---
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
                    if em != "email": dicc[em] = nom
            return dicc
    except: pass
    return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

def b_id(service_drive, nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service_drive.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service_drive.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')

# --- 2. ESTILOS CSS (MÓVIL FRIENDLY) ---
st.markdown("""
    <style>
    @media (max-width: 640px) {
        .header-box h1 { font-size: 1.5rem !important; }
        .stButton button { width: 100% !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8rem !important; padding: 10px 5px !important; }
    }
    .header-box { background-color: #1e3a8a; padding: 1.5rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1rem; }
    .status-panel { background: #f8fafc; padding: 12px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 8px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN INICIAL ---
try:
    with open('token.pickle', 'rb') as t: creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)
    DICCIONARIO_CLIENTES = sincronizar_clientes_drive(service)
    DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": ""}})
    HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
    CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})
except Exception as e:
    st.error("Error de conexión con Google Drive.")
    st.stop()

# --- 4. LOGIN MAESTRO ---
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Contraseña Maestra</p></div>', unsafe_allow_html=True)
    if st.text_input("Introduce la clave:", type="password") == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 5. LOGIN CLIENTE ---
if st.session_state["user_email"] is None:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Bienvenido al Portal</p></div>', unsafe_allow_html=True)
    em_in = st.text_input("Email registrado:").lower().strip()
    if st.button("ACCEDER AL PORTAL", use_container_width=True):
        if em_in in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_in
            st.rerun()
        else: st.error("Email no reconocido.")
    st.stop()

# --- 6. PORTAL ACTIVO ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES.get(email_act, "CLIENTE")
st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

# Avisos Globales e Individuales
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})
if DATA_AVISOS["GLOBAL"].get("mensaje"):
    st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    clase = "aviso-urgente" if config_p.get("prioridad") == "Urgente" else "aviso-info"
    st.markdown(f'<div class="globo-aviso {clase}"><b>{config_p.get("prioridad","").upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("MARCAR COMO LEÍDO ✓"):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""; DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS); st.rerun()

b_col = "bg-presentado" if config_p['estado'] == "Presentado" else "bg-revision" if config_p['estado'] == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p["estado"]}</span></div>', unsafe_allow_html=True)

# --- 7. PESTAÑAS ---
t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Documentación")
    a_s = st.selectbox("Año", ["2026", "2025"])
    t_s = st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    id_cli = b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_final = b_id(service, t_s, b_id(service, cat, b_id(service, a_s, id_cli)))
    
    # Ver archivos ya subidos
    docs_list = service.files().list(q=f"'{id_final}' in parents and trashed=false").execute().get('files', [])
    with st.expander(f"📂 Ver archivos en {t_s} ({len(docs_list)})"):
        for d in docs_list: st.write(f"✅ {d['name']}")
    
    arc = st.file_uploader("Selecciona archivo:")
    if arc and st.button("🚀 ENVIAR A ASESORÍA"):
        n_nom = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{arc.name}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_final]}, media_body=media).execute()
        st.success("¡Enviado con éxito!"); st.balloons()

with t2:
    st.subheader("Impuestos Presentados")
    a_b = st.selectbox("Año:", ["2026", "2025"], key="t2_y")
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
    else: st.info("No hay documentos aún.")

with t3:
    st.subheader("Área Personal")
    id_ap = b_id(service, "AREA PERSONAL", b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"))
    ap_docs = service.files().list(q=f"'{id_ap}' in parents and trashed=false").execute().get('files', [])
    for f in ap_docs:
        st.write(f"📁 {f['name']}")

with t4:
    st.subheader("Panel Administrativo")
    if st.text_input("Clave Admin:", type="password", key="adm_k") == "GEST_LA_2025":
        m_opt = st.radio("Menú:", ["Clientes", "Avisos", "Lecturas"], horizontal=True)
        
        if m_opt == "Clientes":
            st.write("### Lista de Clientes")
            for e, n in DICCIONARIO_CLIENTES.items():
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"**{n}** ({e})")
                if c2.button("🗑️", key=f"del_{e}"):
                    del DICCIONARIO_CLIENTES[e]
                    csv_t = "\n".join([f"{em},{no}" for em, no in DICCIONARIO_CLIENTES.items()])
                    media = MediaIoBaseUpload(io.BytesIO(csv_t.encode('utf-8')), mimetype='text/csv')
                    res = service.files().list(q=f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents").execute().get('files', [])
                    service.files().update(fileId=res[0]['id'], media_body=media).execute()
                    st.rerun()
            
            st.divider()
            st.write("### Nuevo Cliente")
            nn, ne = st.text_input("Nombre:"), st.text_input("Email:")
            if st.button("🚀 GUARDAR EN DRIVE"):
                DICCIONARIO_CLIENTES[ne.lower().strip()] = nn.upper()
                csv_t = "\n".join([f"{em},{no}" for em, no in DICCIONARIO_CLIENTES.items()])
                media = MediaIoBaseUpload(io.BytesIO(csv_t.encode('utf-8')), mimetype='text/csv')
                res = service.files().list(q=f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents").execute().get('files', [])
                service.files().update(fileId=res[0]['id'], media_body=media).execute()
                st.success("Guardado"); st.rerun()

        elif m_opt == "Avisos":
            dest = st.selectbox("Destino:", ["GLOBAL", "INDIVIDUAL"])
            m_txt = st.text_area("Mensaje:")
            if dest == "INDIVIDUAL":
                c_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                est_n = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                prio_n = st.selectbox("Prioridad:", ["Información", "Urgente"])
                if st.button("ENVIAR AVISO"):
                    DATA_AVISOS[c_sel] = {"mensaje": m_txt, "estado": est_n, "prioridad": prio_n}
                    guardar_json(AVISOS_FILE, DATA_AVISOS)
                    enviar_email(c_sel, DICCIONARIO_CLIENTES[c_sel], "personal")
                    st.success("Enviado"); st.rerun()
            elif st.button("PUBLICAR GLOBAL"):
                DATA_AVISOS["GLOBAL"] = {"mensaje": m_txt}
                guardar_json(AVISOS_FILE, DATA_AVISOS)
                st.success("Publicado"); st.rerun()

        elif m_opt == "Lecturas":
            for log in reversed(HISTORIAL_LOG):
                st.info(f"✔️ {log['cliente']} leyó: {log['msg']} ({log['fecha']})")

if st.button("SALIR / CERRAR SESIÓN"):
    st.session_state["user_email"] = None
    st.rerun()

