import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
    .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px; text-align: center; font-size: 0.9rem; }
    .estado-box { background-color: #fff9c4; padding: 10px; border-radius: 10px; color: #827717; font-weight: bold; margin-bottom: 15px; text-align: center; border: 1px solid #fbc02d; }
    .aviso-rojo { padding: 15px; border-radius: 10px; background-color: #ffebee; border-left: 6px solid #f44336; color: #b71c1c; margin: 10px 0; }
    .aviso-azul { padding: 15px; border-radius: 10px; background-color: #e3f2fd; border-left: 6px solid #2196f3; color: #0d47a1; margin: 10px 0; }
    .aviso-tarea { padding: 15px; border-radius: 10px; background-color: #fff3e0; border-left: 6px solid #ff9800; color: #e65100; margin: 10px 0; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True

    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña incorrecta")
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"
    AVISOS_FILE = "avisos_db.json"

    def cargar_datos(archivo, defecto):
        if os.path.exists(archivo):
            try:
                with open(archivo, "r", encoding="utf-8") as f: return json.load(f)
            except: return defecto
        return defecto

    def guardar_datos(archivo, datos):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_datos(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    DB_AVISOS = cargar_datos(AVISOS_FILE, {})

    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu gestión, más fácil y transparente</p></div>', unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenida al Portal")
        c_mail1, c_mail2, c_mail3 = st.columns([1,2,1])
        with c_mail2:
            em_log = st.text_input("Correo electrónico:")
            if st.button("ACCEDER", use_container_width=True):
                if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = em_log.lower().strip()
                    st.rerun()
                else: st.error("Correo no registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]

        c_logout1, c_logout2 = st.columns([4,1])
        c_logout1.markdown(f'<div class="user-info">Sesión: {nombre_act}</div>', unsafe_allow_html=True)
        if c_logout2.button("🔒 SALIR"):
            del st.session_state["user_email"]
            st.rerun()

        # Mostrar Estado y Aviso del cliente
        info_c = DB_AVISOS.get(email_act, {"texto": "Bienvenido/a a tu portal.", "tipo": "azul", "estado": "Pendiente documentación"})
        st.markdown(f'<div class="estado-box">📊 ESTADO 1T 2026: {info_c["estado"]}</div>', unsafe_allow_html=True)
        
        clase_css = "aviso-rojo" if info_c["tipo"] == "urgente" else "aviso-azul" if info_c["tipo"] == "informativo" else "aviso-tarea"
        tit_av = "⚠️ URGENTE" if info_c["tipo"] == "urgente" else "📢 INFORMATIVO" if info_c["tipo"] == "informativo" else f"📝 TAREA PENDIENTE - {nombre_act.split()[0]}"
        st.markdown(f'<div class="{clase_css}"><strong>{tit_av}:</strong> {info_c["texto"]}</div>', unsafe_allow_html=True)
        
        if st.button("✔️ HE LEÍDO EL AVISO"):
            st.balloons()
            with open(f"REGISTRO_AVISOS_{nombre_act}.txt", "a") as f:
                f.write(f"{datetime.datetime.now()}: Leído: {info_c['texto']}\n")

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR DOCUMENTOS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)

        with tab1:
            c1, c2 = st.columns(2)
            a_sel = c1.selectbox("Año", ["2026", "2025"])
            t_sel = c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Selecciona archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if arc and st.button("🚀 ENVIAR AHORA"):
                try:
                    ahora = datetime.datetime.now()
                    id_just = f"REF-{ahora.strftime('%Y%m%d%H%M%S')}"
                    ext = os.path.splitext(arc.name)[1]
                    tipo_corto = "EMITIDA" if "EMITIDAS" in tipo_sel else "GASTO"
                    n_prof = f"{ahora.strftime('%Y-%m-%d')}_{tipo_corto}_{id_just}{ext}"

                    q = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                    res = service.files().list(q=q).execute().get('files', [])
                    if res:
                        id_cli = res[0]['id']
                        def get_f(n, p):
                            q_f = f"name='{n}' and '{p}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                            rf = service.files().list(q=q_f).execute().get('files', [])
                            if rf: return rf[0]['id']
                            return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        
                        id_final = get_f(t_sel, get_f(tipo_sel, get_f(a_sel, id_cli)))
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream', resumable=True)
                        service.files().create(body={'name': n_prof, 'parents': [id_final]}, media_body=media).execute()
                        
                        linea = f"{ahora.strftime('%d/%m/%Y %H:%M')}|{n_prof}|{id_just}\n"
                        q_reg = f"name = 'REGISTRO_ENVIOS_{nombre_act}.txt' and '{id_cli}' in parents and trashed = false"
                        res_reg = service.files().list(q=q_reg).execute().get('files', [])
                        if res_reg:
                            f_id = res_reg[0]['id']
                            old_c = service.files().get_media(fileId=f_id).execute().decode('utf-8')
                            service.files().update(fileId=f_id, media_body=MediaIoBaseUpload(io.BytesIO((old_c + linea).encode('utf-8')), mimetype='text/plain')).execute()
                        else:
                            service.files().create(body={'name': f'REGISTRO_ENVIOS_{nombre_act}.txt', 'parents': [id_cli]}, media_body=MediaIoBaseUpload(io.BytesIO(linea.encode('utf-8')), mimetype='text/plain')).execute()
                        st.markdown(f'<div class="justificante"><b>✅ RECIBIDO</b><br>Ref: {id_just}</div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

            st.write("---")
            st.subheader("📋 Tus últimos envíos")
            try:
                q_cli_tab = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                res_cli_tab = service.files().list(q=q_cli_tab).execute().get('files', [])
                if res_cli_tab:
                    id_cli_tab = res_cli_tab[0]['id']
                    q_reg_tab = f"name = 'REGISTRO_ENVIOS_{nombre_act}.txt' and '{id_cli_tab}' in parents and trashed = false"
                    res_reg_tab = service.files().list(q=q_reg_tab).execute().get('files', [])
                    if res_reg_tab:
                        content = service.files().get_media(fileId=res_reg_tab[0]['id']).execute().decode('utf-8')
                        filas = [l.split('|') for l in content.split('\n') if l]
                        for f in filas[-5:]: st.text(f"📅 {f[0]} - 📄 {f[1]} (Ref: {f[2]})")
            except: pass

        with tab2: # --- AQUÍ ESTÁ LO DE DESCARGAR IMPUESTOS ---
            st.subheader("📥 Mis Impuestos")
            a_
