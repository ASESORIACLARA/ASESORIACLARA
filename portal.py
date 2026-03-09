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

# --- CONEXIÓN PERMANENTE CON TU CSV DE DRIVE ---
ID_CARPETA_PROG = "1usBtuwX3xwZmIjojwP2ScUEBWx9vcjmt"

def sincronizar_clientes_drive():
    try:
        q = f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents and trashed=false"
        res = service.files().list(q=q).execute().get('files', [])
        if res:
            f_id = res[0]['id']
            cont = service.files().get_media(fileId=f_id).execute().decode('utf-8')
            lineas = cont.strip().split('\n')
            dicc = {}
            for l in lineas:
                if ',' in l:
                    partes = l.split(',')
                    # Limpiamos espacios y forzamos minúsculas para que el login no falle
                    em = partes[0].strip().lower()
                    nom = partes[1].strip().upper()
                    if em != "email": # Ignora la fila de títulos si existe
                        dicc[em] = nom
            return dicc
    except Exception as e:
        st.error(f"Error al leer Drive: {e}")
    # Si falla o está vacío, Lorena siempre puede entrar
    return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}



# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    @media (max-width: 640px) {
        .header-box h1 { font-size: 1.6rem !important; letter-spacing: -1px; line-height: 1; }
        .stButton button { width: 100% !important; height: 3.5rem !important; font-size: 1rem !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.75rem !important; padding: 10px 4px !important; }
        .status-panel { font-size: 0.85rem !important; display: flex; flex-direction: column; gap: 8px; align-items: center; }
    }
    .header-box { background-color: #1e3a8a; padding: 1.5rem 1rem; border-radius: 20px; text-align: center; color: white; margin-bottom: 1rem; }
    .header-box p { font-style: italic; opacity: 0.9; margin-top: 5px; font-size: 0.85rem; }
    .status-panel { background: #f8fafc; padding: 12px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; display: inline-block; }
    .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
    .globo-aviso { border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 8px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
    .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
    </style>
""", unsafe_allow_html=True)
# --- 5. GOOGLE DRIVE (Movido aquí para que cargue antes del login) ---
try:
    with open('token.pickle', 'rb') as t: 
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    # AHORA SÍ, cargamos los datos porque el 'service' ya existe
    DICCIONARIO_CLIENTES = sincronizar_clientes_drive()
    DATA_AVISOS = cargar_json(AVISOS_FILE, {"GLOBAL": {"mensaje": ""}})
    HISTORIAL_LOG = cargar_json(LOG_AVISOS, [])
    CONFIG_APP = cargar_json(CONFIG_FILE, {"trimestre_activo": "1T 2026"})
except Exception as e:
    st.error(f"Error en la conexión inicial: {e}")

# --- 3. LOGINS ---
if not st.session_state["password_correct"]:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    if st.text_input("Contraseña Maestra:", type="password") == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()


# --- 4. PORTAL CLIENTE ACTIVO ---
email_act = st.session_state["user_email"]

if email_act not in DICCIONARIO_CLIENTES:
    st.error(f"⚠️ El email '{email_act}' no está autorizado.")
    if st.button("⬅️ VOLVER AL INICIO"):
        st.session_state["user_email"] = None
        st.rerun()
    st.stop()

nombre_act = DICCIONARIO_CLIENTES[email_act]
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información"})
st.markdown(f'<div class="header-box"><h1>ASESORIACLARA</h1><p>Hola, {nombre_act}</p></div>', unsafe_allow_html=True)

if DATA_AVISOS["GLOBAL"].get("mensaje"):
    st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

if config_p.get("mensaje"):
    prio = config_p.get("prioridad", "Información")
    clase = "aviso-urgente" if prio == "Urgente" else "aviso-info"
    st.markdown(f'<div class="globo-aviso {clase}"><b>{prio.upper()}:</b> {config_p["mensaje"]}</div>', unsafe_allow_html=True)
    if st.button("MARCAR COMO LEÍDO ✓", use_container_width=True):
        HISTORIAL_LOG.append({"cliente": nombre_act, "msg": config_p["mensaje"], "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')})
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        config_p["mensaje"] = ""
        DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS)
        st.rerun()

b_col = "bg-presentado" if config_p['estado'] == "Presentado" else "bg-revision" if config_p['estado'] == "En revisión" else "bg-pendiente"
st.markdown(f'<div class="status-panel">Periodo: <b>{CONFIG_APP["trimestre_activo"]}</b> | <span class="badge {b_col}">{config_p["estado"]}</span></div>', unsafe_allow_html=True)

# --- 5. GOOGLE DRIVE ---
with open('token.pickle', 'rb') as t: creds = pickle.load(t)
service = build('drive', 'v3', credentials=creds)
# --- CARGA DE DATOS (IMPORTANTE: Debe ir después de definir 'service') ---

def b_id(nombre, padre):
    q = f"name='{nombre}' and '{padre}' in parents and trashed=false"
    res = service.files().list(q=q).execute().get('files', [])
    if res: return res[0]['id']
    return service.files().create(body={'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [padre]}, fields='id').execute().get('id')
if st.session_state["user_email"] is None:
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    em = st.text_input("Email registrado:")
    if st.button("ACCEDER AL PORTAL", use_container_width=True):
        if em.lower().strip() in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em.lower().strip()
            st.rerun()
        else:
            st.error("Email no reconocido.")
    st.stop()
# --- 6. PESTAÑAS ---
t1, t2, t3, t4 = st.tabs(["📤 SUBIR", "📥 IMPUESTOS", "📁 PERSONAL", "⚙️ GESTIÓN"])

with t1:
    st.subheader("Subir Facturas")
    a_s, t_s = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    id_cli = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_f = b_id(t_s, b_id(cat, b_id(a_s, id_cli)))
    
    docs = service.files().list(q=f"'{id_f}' in parents and trashed=false").execute().get('files', [])
    if docs:
        with st.expander(f"📂 Archivos enviados ({len(docs)})"):
            for d in docs: st.write(f"✅ {d['name']}")
    
    arc = st.file_uploader("Subir archivo")
    if arc and st.button("🚀 ENVIAR DOCUMENTO", use_container_width=True):
        f_h, h_h = datetime.datetime.now().strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%H:%M')
        ref = f"REF-{datetime.datetime.now().strftime('%H%M%S')}"
        n_nom = f"{f_h}_{cat[:4]}_{ref}{os.path.splitext(arc.name)[1]}"
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_f]}, media_body=media).execute()
        
        n_log = f"REGISTRO_ENVIOS_{nombre_act.replace(' ', '_')}.txt"
        res_log = service.files().list(q=f"name='{n_log}' and '{id_cli}' in parents and trashed=false").execute().get('files', [])
        n_lin = f"{f_h} {h_h}|{arc.name}|{ref}\n"
        
        try:
            if res_log:
                f_id = res_log[0]['id']
                prev = service.files().get_media(fileId=f_id).execute().decode('utf-8')
                m_up = MediaIoBaseUpload(io.BytesIO((prev + n_lin).encode('utf-8')), mimetype='text/plain')
                service.files().update(fileId=f_id, media_body=m_up).execute()
            else:
                m_up = MediaIoBaseUpload(io.BytesIO(n_lin.encode('utf-8')), mimetype='text/plain')
                service.files().create(body={'name': n_log, 'parents': [id_cli]}, media_body=m_up).execute()
        except: pass
        st.success("¡Enviado y registrado!"); st.balloons()

with t2:
    st.subheader("Impuestos Presentados")
    a_b = st.selectbox("Año:", ["2026", "2025"], key="tab2_y")
    id_cli_root = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    id_año = b_id(a_b, id_cli_root)
    res_f = service.files().list(q=f"name='IMPUESTOS PRESENTADOS' and '{id_año}' in parents and trashed=false").execute().get('files', [])
    if res_f:
        docs_imp = service.files().list(q=f"'{res_f[0]['id']}' in parents and trashed=false").execute().get('files', [])
        for d in docs_imp:
            c1, c2 = st.columns([0.7, 0.3])
            c1.write(f"📄 {d['name']}")
            req = service.files().get_media(fileId=d['id'])
            fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req); done = False
            while not done: _, done = downloader.next_chunk()
            c2.download_button("Descargar", fh.getvalue(), file_name=d['name'], key="imp_"+d['id'])
    else: st.info("No hay carpeta de 'IMPUESTOS PRESENTADOS' para este año.")

with t3:
    st.subheader("📁 Área Personal")
    id_root_p = b_id(nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
    res_ap = service.files().list(q=f"name='AREA PERSONAL' and '{id_root_p}' in parents and trashed=false").execute().get('files', [])
    if res_ap:
        files_ap = service.files().list(q=f"'{res_ap[0]['id']}' in parents and trashed=false").execute().get('files', [])
        for f in files_ap:
            c1, c2 = st.columns([0.7, 0.3])
            c1.write(f"📄 {f['name']}")
            req = service.files().get_media(fileId=f['id'])
            fh = io.BytesIO(); downloader = MediaIoBaseDownload(fh, req); done = False
            while not done: _, done = downloader.next_chunk()
            c2.download_button("Bajar", fh.getvalue(), file_name=f['name'], key="ap_"+f['id'])

with t4:
        st.subheader("Panel Administrativo")
        pass_admin = st.text_input("Clave Admin:", type="password", key="adm_key")
        if pass_admin == "GEST_LA_2025":
            opt = st.radio("Sección:", ["Avisos", "Clientes", "Lecturas"], horizontal=True)
            
            if opt == "Avisos":
                dest = st.selectbox("Destino:", ["GLOBAL", "INDIVIDUAL"])
                m_txt = st.text_area("Mensaje del aviso:")
                if dest == "INDIVIDUAL":
                    c_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                    est_n = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                    prio_n = st.selectbox("Prioridad:", ["Información", "Urgente"])
                    if st.button("ACTUALIZAR"):
                        DATA_AVISOS[c_sel] = {"mensaje": m_txt, "estado": est_n, "prioridad": prio_n}
                        guardar_json(AVISOS_FILE, DATA_AVISOS)
                        enviar_email(c_sel, DICCIONARIO_CLIENTES[c_sel], "personal")
                        st.success("¡Enviado!"); st.rerun()
                elif st.button("PUBLICAR GLOBAL"):
                    DATA_AVISOS["GLOBAL"] = {"mensaje": m_txt}
                    guardar_json(AVISOS_FILE, DATA_AVISOS)
                    for e, n in DICCIONARIO_CLIENTES.items(): enviar_email(e, n, "global")
                    st.success("Global publicado"); st.rerun()

            elif opt == "Clientes":
                st.write("### Gestión de Clientes (Drive)")
                for e, n in DICCIONARIO_CLIENTES.items(): st.write(f"• {n} ({e})")
                st.divider()
                n_n = st.text_input("Nombre Nuevo:")
                n_e = st.text_input("Email Nuevo:")
                if st.button("🚀 GUARDAR ALTA EN DRIVE"):
                    if n_n and n_e:
                        DICCIONARIO_CLIENTES[n_e.lower().strip()] = n_n.upper()
                        nuevo_csv = "\n".join([f"{e},{n}" for e, n in DICCIONARIO_CLIENTES.items()])
                        media = MediaIoBaseUpload(io.BytesIO(nuevo_csv.encode('utf-8')), mimetype='text/csv')
                        q = f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents and trashed=false"
                        res = service.files().list(q=q).execute().get('files', [])
                        if res:
                            service.files().update(fileId=res[0]['id'], media_body=media).execute()
                        else:
                            service.files().create(body={'name': 'clientes.csv', 'parents': [ID_CARPETA_PROG]}, media_body=media).execute()
                        st.success("✅ Guardado en Drive"); st.rerun()
                
                st.divider()
                lista_emails = list(DICCIONARIO_CLIENTES.keys())
                if lista_emails:
                    c_del = st.selectbox("Seleccionar para eliminar:", lista_emails, format_func=lambda x: DICCIONARIO_CLIENTES[x])
                    if st.button("❌ ELIMINAR DE DRIVE"):
                        del DICCIONARIO_CLIENTES[c_del]
                        nuevo_csv = "\n".join([f"{e},{n}" for e, n in DICCIONARIO_CLIENTES.items()])
                        media = MediaIoBaseUpload(io.BytesIO(nuevo_csv.encode('utf-8')), mimetype='text/csv')
                        q = f"name='clientes.csv' and '{ID_CARPETA_PROG}' in parents and trashed=false"
                        res = service.files().list(q=q).execute().get('files', [])
                        if res:
                            service.files().update(fileId=res[0]['id'], media_body=media).execute()
                        st.warning("Eliminado de Drive"); st.rerun()

            elif opt == "Lecturas":
                st.write("### Historial de Lecturas")
                for log in reversed(HISTORIAL_LOG):
                    st.success(f"✔️ {log['cliente']} leyó el aviso")
                    st.caption(f"Fecha: {log['fecha']} | Msg: {log['msg']}")
                    st.divider()
        elif opt == "Lecturas":
            st.write("### Historial")
            for log in reversed(HISTORIAL_LOG):
                st.success(f"✔️ {log['cliente']} leyó el aviso")
                st.caption(f"Fecha: {log['fecha']} | Msg: {log['msg']}")
                st.divider()

# Este botón va fuera de las pestañas, al final de todo el archivo
if st.button("SALIR", use_container_width=True):
    st.session_state["user_email"] = None
    st.rerun()











