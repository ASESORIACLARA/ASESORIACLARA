import streamlit as st
import os, pickle, json, io, datetime, smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if "user_email" not in st.session_state: st.session_state["user_email"] = None

# Base de datos local para avisos y configuración
AVISOS_FILE = "avisos_db.json"
LOG_AVISOS = "log_avisos.json"
CONFIG_FILE = "config_app.json"

SMTP_USER = "asesoriaclara0@gmail.com" 
SMTP_PASS = "aucmoslkpgcsbglv" 
URL_PORTAL = "https://asesoriaclara.streamlit.app"
ID_CARPETA_PROG = "1usBtuwX3xwZmIjojwP2ScUEBWx9vcjmt"

# --- FUNCIONES DE EMAIL Y DRIVE ---
def enviar_email(destinatario, nombre_cliente, tipo_mensaje, texto_aviso=""):
    try:
        asunto = f"📢 NUEVO AVISO DE ASESORIACLARA"
        cuerpo = f"Hola {nombre_cliente},\n\n{tipo_mensaje}:\n\"{texto_aviso}\"\n\nPuedes revisarlo y marcarlo como leído en tu portal: {URL_PORTAL}\n\nUn saludo,\nASESORIACLARA."
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

# --- 2. CONEXIÓN ---
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

# --- 3. LOGINS ---
if not st.session_state["password_correct"]:
    if st.text_input("Clave Maestra:", type="password") == "clara2026":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

if st.session_state["user_email"] is None:
    em_in = st.text_input("Email:").lower().strip()
    if st.button("ENTRAR"):
        if em_in in DICCIONARIO_CLIENTES:
            st.session_state["user_email"] = em_in
            st.rerun()
    st.stop()

# --- 4. INTERFAZ CLIENTE ---
email_act = st.session_state["user_email"]
nombre_act = DICCIONARIO_CLIENTES.get(email_act, "CLIENTE")

st.markdown(f"### 📑 Portal de {nombre_act}")

# AVISO GLOBAL
if DATA_AVISOS["GLOBAL"].get("mensaje"):
    st.warning(f"📢 **AVISO GENERAL:** {DATA_AVISOS['GLOBAL']['mensaje']}")

# AVISO PERSONAL Y BOTÓN "LEÍDO"
config_p = DATA_AVISOS.get(email_act, {"estado": "Pendiente", "mensaje": "", "prioridad": "Información"})
if config_p.get("mensaje"):
    st.info(f"✉️ **AVISO PARA TI:** {config_p['mensaje']}")
    if st.button("✅ HE LEÍDO EL MENSAJE"):
        # Registrar en el historial
        HISTORIAL_LOG.append({
            "cliente": nombre_act, 
            "msg": config_p["mensaje"], 
            "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        })
        guardar_json(LOG_AVISOS, HISTORIAL_LOG)
        # Borrar aviso para que no salga más
        config_p["mensaje"] = ""
        DATA_AVISOS[email_act] = config_p
        guardar_json(AVISOS_FILE, DATA_AVISOS)
        st.success("¡Gracias! Aviso registrado.")
        st.rerun()

# --- 5. PESTAÑAS ---
t1, t4 = st.tabs(["📤 SUBIR FACTURAS", "⚙️ ADMINISTRACIÓN"])

with t1:
    cat = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
    arc = st.file_uploader("Adjuntar archivo:")
    if arc and st.button("🚀 ENVIAR"):
        # Renombrar con fecha
        fecha_str = datetime.datetime.now().strftime('%Y-%m-%d')
        n_nom = f"{fecha_str}_{arc.name}"
        
        id_cli = b_id(service, nombre_act, "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH")
        id_final = b_id(service, "2026", b_id(service, cat, id_cli))
        
        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
        service.files().create(body={'name': n_nom, 'parents': [id_final]}, media_body=media).execute()
        st.success(f"Archivo '{n_nom}' guardado en Drive.")

with t4:
    if st.text_input("Clave Admin:", type="password") == "GEST_LA_2025":
        opt = st.radio("Sección:", ["Avisos", "Lecturas", "Clientes"])
        
        if opt == "Avisos":
            dest = st.selectbox("Enviar a:", ["GLOBAL", "INDIVIDUAL"])
            msg_enviar = st.text_area("Mensaje:")
            if st.button("📤 ENVIAR Y NOTIFICAR POR EMAIL"):
                if dest == "GLOBAL":
                    DATA_AVISOS["GLOBAL"] = {"mensaje": msg_enviar}
                    for e, n in DICCIONARIO_CLIENTES.items():
                        enviar_email(e, n, "Tienes un nuevo aviso general", msg_enviar)
                else:
                    c_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                    DATA_AVISOS[c_sel] = {"mensaje": msg_enviar, "estado": "En revisión", "prioridad": "Urgente"}
                    enviar_email(c_sel, DICCIONARIO_CLIENTES[c_sel], "Tienes un nuevo aviso personal", msg_enviar)
                
                guardar_json(AVISOS_FILE, DATA_AVISOS)
                st.success("Aviso publicado y correos enviados.")

        elif opt == "Lecturas":
            st.write("### 📖 Historial de confirmaciones")
            for log in reversed(HISTORIAL_LOG):
                st.write(f"✔️ **{log['cliente']}** leyó el aviso el {log['fecha']}")

if st.button("SALIR"):
    st.session_state["user_email"] = None
    st.rerun()
