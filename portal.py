import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. BASES DE DATOS Y CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered", initial_sidebar_state="collapsed")

DB_FILE = "clientes_db.json"
AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"

# --- CONFIGURACIÓN ENVÍO DE EMAIL (IMPORTANTE RELLENAR) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "tu_correo@gmail.com" # Cambia por tu email
SMTP_PASS = "tu_clave_aplicacion" # Cambia por tu clave de aplicación de Google
URL_PORTAL = "https://tu-portal.streamlit.app" # Tu enlace real

def enviar_notificacion_email(destinatario, nombre_cliente, tipo="personal"):
    """Función para enviar el aviso por correo"""
    try:
        asunto = "📢 Aviso importante en ASESORIACLARA"
        contenido = f"""
        Hola {nombre_cliente},
        
        Te informamos que tienes un nuevo mensaje {tipo} disponible en tu Portal de Cliente.
        
        Puedes acceder para leerlo y descargar tus documentos en el siguiente enlace:
        {URL_PORTAL}
        
        Atentamente,
        ASESORIACLARA
        """
        msg = MIMEText(contenido)
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
        print(f"Error enviando email: {e}")
        return False

def cargar_json(archivo, inicial):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# Carga inicial
DICCIONARIO_CLIENTES = cargar_json(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": "", "fecha": ""}})
HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})

# --- 2. DISEÑO Y ESTILOS (MÓVIL) ---
st.markdown("""
    <style>
    @media (max-width: 640px) {
        .stButton button { width: 100% !important; height: 3.5rem !important; font-size: 1.1rem !important; }
    }
    .header-box { background-color: #1e3a8a; padding: 2rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1.5rem; }
    .status-panel { background: #f8fafc; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; }
    .badge { padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 18px; margin: 12px 0; border-left: 8px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SISTEMA DE LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    pass_in = st.text_input("Contraseña Maestra:", type="password")
    if st.button("ENTRAR AL PORTAL", use_container_width=True):
        if pass_in == "clara2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Contraseña incorrecta")
    st.stop()

if "user_email" not in st.session_state:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    em_log = st.text_input("Introduce tu email registrado para acceder:")
    if st.button("ACCEDER", use_container_width=True):
        if em_log.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_log.lower().strip()
            st.rerun()
        else: st.error("Email no encontrado.")
    st.stop()

# --- 4. PORTAL DE CLIENTE ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})

st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

if st.button("SALIR DEL PORTAL"):
    del st.session_state["user_email"]
    st.rerun()

# Lógica de Avisos y Botón Leído
if DATA_AVISOS["GLOBAL"]["mensaje"]:
    st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    clase = "aviso-urgente" if config_p["prioridad"] == "Urgente" else "aviso-info"
    st.markdown(f'<div class="globo-aviso {clase}"><b>{config_p["prioridad"].upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("MARCAR COMO LEÍDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""
        DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS)
        st.rerun()

# Estado del Cliente
b_col = "bg-presentado" if config_p['estado'] == "Presentado" else "bg-revision" if config_p['estado'] == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p["estado"]}</span></div>', unsafe_allow_html=True)

# --- 5. GOOGLE DRIVE ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)

def b_id(nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')

# --- TABS PRINCIPALES ---
t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 ÁREA PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir documentación")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    
    id_cli = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_f = b_id(t_s, b_id(cat, b_id(a_s, id_cli)))
    
    arc = st.file_uploader("Selecciona archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
    if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
        barra = st.progress(0)
        ahora = datetime.datetime.now()
        ref = ahora.strftime('%Y%m%d%H%M%S')
        n_nom = f"{ahora.strftime('%Y-%m-%d')}_{cat[:4]}_REF-{ref}{os.path.splitext(arc.name)[1]}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        barra.progress(100)
        st.success(f"¡Enviado! Ref: {ref}")
        st.balloons()

with t2:
    st.subheader("Modelos Presentados")
    # Lógica igual que el código anterior para descarga de la carpeta 'IMPUESTOS PRESENTADOS'
    a_busq = st.selectbox("Selecciona Año:", ["2026", "2025"])
    id_a = b_id(a_busq, b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH"))
    res_f = service.files().list(q=f"name='IMPUESTOS PRESENTADOS' and '{id_a}' in parents and trashed=false").execute().get('files', [])
    if res_f:
        docs = service.files().list(q=f"'{res_f[0]['id']}' in parents and trashed=false").execute().get('files', [])
        for d in docs:
            c1, c2 = st.columns([0.7, 0.3])
            c1.write(f"📄 {d['name']}")
            req = service.files().get_media(fileId=d['id'])
            fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req); done = False
            while not done: _, done = downloader.next_chunk()
            c2.download_button("Bajar", fh.getvalue(), file_name=d['name'], key=d['id'])
    else: st.info("No hay impuestos subidos aún.")

with t3:
    st.subheader("📁 Tu Área Personal")
    st.info("Documentos privados compartidos por tu asesora.")
    id_cli_ap = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    res_ap = service.files().list(q=f"name='AREA PERSONAL' and '{id_cli_ap}' in parents and trashed=false").execute().get('files', [])
    if res_ap:
        docs_ap = service.files().list(q=f"'{res_ap[0]['id']}' in parents and trashed=false").execute().get('files', [])
        if docs_ap:
            for d in docs_ap:
                c1, c2 = st.columns([0.7, 0.3])
                c1.write(f"📄 {d['name']}")
                req = service.files().get_media(fileId=d['id'])
                fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req); done = False
                while not done: _, done = downloader.next_chunk()
                c2.download_button("Descargar", fh.getvalue(), file_name=d['name'], key="ap_"+d['id'])
        else: st.write("Carpeta vacía.")
    else: st.write("Aún no se ha habilitado tu Área Personal.")

with t4:
    st.subheader("Gestión")
    if st.text_input("Clave Admin:", type="password") == "GEST_LA_2025":
        herr = st.radio("Herramienta:", ["Avisos y Emails", "Clientes", "Lecturas"], horizontal=True)
        
        if herr == "Avisos y Emails":
            dest = st.selectbox("Destino:", ["GLOBAL", "INDIVIDUAL"])
            msg = st.text_area("Mensaje:")
            prio_n = st.selectbox("Prioridad:", ["Información", "Urgente"])
            if st.button("PUBLICAR Y NOTIFICAR POR EMAIL"):
                if dest == "GLOBAL":
                    DATA_AVISOS["GLOBAL"] = {"mensaje": msg}
                    for e in DICCIONARIO_CLIENTES.keys(): enviar_notificacion_email(e, DICCIONARIO_CLIENTES[e], "general")
                else:
                    c_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                    DATA_AVISOS[c_sel] = {"mensaje": msg, "estado": "En revisión", "prioridad": prio_n}
                    enviar_notificacion_email(c_sel, DICCIONARIO_CLIENTES[c_sel], "personal")
                guardar_json(AVISOS_FILE, DATA_AVISOS); st.success("¡Hecho!"); st.rerun()

        elif herr == "Clientes":
            # (Aquí va tu sección de añadir y eliminar clientes ya conocida)
            for em, nom in DICCIONARIO_CLIENTES.items(): st.write(f"• {nom} ({em})")
            n_n = st.text_input("Nuevo Nombre:"); n_e = st.text_input("Nuevo Email:")
            if st.button("Añadir"):
                DICCIONARIO_CLIENTES[n_e.lower().strip()] = n_n.upper()
                guardar_json(DB_FILE, DICCIONARIO_CLIENTES); st.rerun()
