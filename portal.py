import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="ASESORIACLARA", 
    page_icon="⚖️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

DB_FILE = "clientes_db.json"
AVISOS_FILE = "avisos_db.json"

def cargar_json(archivo, inicial):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f: return json.load(f)
        except: return inicial
    return inicial

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

DICCIONARIO_CLIENTES = cargar_json(DB_FILE, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
DATA_AVISOS = cargar_json(AVISOS_FILE, {})

# --- 2. LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: clamp(1.5rem, 8vw, 2.5rem);">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px;">Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        pass_in = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if pass_in == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Incorrecta")
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"

    # --- 3. ESTILOS RESPONSIVE ---
    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
        .header-box h1 { color: white !important; margin: 0; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
        .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 10px; text-align: center; }
        .status-panel { background: #f1f3f9; padding: 12px; border-radius: 12px; border: 1px solid #d1d5db; text-align: center; margin-bottom: 15px; }
        .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }
        .bg-pendiente { background-color: #f1c40f; } .bg-revision { background-color: #3498db; } .bg-presentado { background-color: #2ecc71; }
        .globo-aviso { border-radius: 10px; padding: 12px; margin: 10px 0; border-left: 6px solid; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .aviso-urgente { background: #fdf2f2; border-left-color: #e74c3c; color: #c0392b; }
        .aviso-info { background: #ebf8ff; border-left-color: #3498db; color: #2c5282; }
        .aviso-finalizado { background: #f0fff4; border-left-color: #2ecc71; color: #22543d; }
        [data-testid="stSidebar"] { display: none; }
        </style>
        <div class="header-box"><h1>ASESORIACLARA</h1></div>
    """, unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenida")
        em_log = st.text_input("Correo electrónico:")
        if st.button("ACCEDER", use_container_width=True):
            if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                st.session_state["user_email"] = em_log.lower().strip()
                st.rerun()
            else: st.error("No registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]
        
        # Carga segura de avisos (Evita el KeyError)
        config_cliente = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información", "fecha": ""})

        # Cabecera Usuario
        c_logout1, c_logout2 = st.columns([0.7, 0.3])
        c_logout1.markdown(f'<div class="user-info">Sesión: {nombre_act}</div>', unsafe_allow_html=True)
        if c_logout2.button("🔒 SALIR", use_container_width=True):
            del st.session_state["user_email"]
            st.rerun()

        # Estado del Trimestre
        b_col = "bg-presentado" if config_cliente.get('estado') == "Presentado" else "bg-revision" if config_cliente.get('estado') == "En revisión" else "bg-pendiente"
        st.markdown(f"""
            <div class="status-panel">
                <span style="color:#1e3a8a">Trimestre: <b>1T 2026</b></span> | 
                <span class="badge {b_col}">{config_cliente.get('estado')}</span>
            </div>
        """, unsafe_allow_html=True)

        # Globos de Aviso
        msg_aviso = config_cliente.get('mensaje', "")
        if msg_aviso:
            prio = config_cliente.get('prioridad', "Información")
            estilo = "aviso-urgente" if "Urgente" in prio else "aviso-finalizado" if "finalizado" in prio else "aviso-info"
            st.markdown(f"""
                <div class="globo-aviso {estilo}">
                    <small>📅 {config_cliente.get('fecha','')}</small><br>
                    <strong>{prio.upper()}:</strong> {msg_aviso}
                </div>
            """, unsafe_allow_html=True)
            if st.button("ENTENDIDO ✓", use_container_width=True):
                config_cliente['mensaje'] = ""
                DATA_AVISOS[email_act] = config_cliente
                guardar_json(AVISOS_FILE, DATA_AVISOS)
                st.rerun()

        # --- TABS PRINCIPALES ---
        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR DOCUMENTOS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

        # Credenciales Drive
        with open('token.pickle', 'rb') as t: creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)

        with tab1:
            c1, c2 = st.columns(2)
            a_sel, t_sel = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Selecciona archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if arc and st.button("🚀 ENVIAR AHORA", use_container_width=True):
                try:
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
                        
                        ahora = datetime.datetime.now()
                        ref_id = ahora.strftime('%Y%m%d%H%M%S')
                        ext = os.path.splitext(arc.name)[1]
                        nuevo_nombre = f"{ahora.strftime('%Y-%m-%d')}_{tipo_sel.split()[-1]}_REF-{ref_id}{ext}"
                        
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype=arc.type)
                        service.files().create(body={'name': nuevo_nombre, 'parents':[id_final]}, media_body=media).execute()
                        
                        # Registro TXT de seguridad
                        linea = f"{ahora.strftime('%d/%m/%Y %H:%M')}|{nuevo_nombre}|REF-{ref_id}\n"
                        q_reg = f"name = 'REGISTRO_ENVIOS_{nombre_act}.txt' and '{id_cli}' in parents and trashed = false"
                        res_reg = service.files().list(q=q_reg).execute().get('files', [])
                        if res_reg:
                            f_id = res_reg[0]['id']
                            old_c = service.files().get_media(fileId=f_id).execute().decode('utf-8')
                            service.files().update(fileId=f_id, media_body=MediaIoBaseUpload(io.BytesIO((old_c + linea).encode('utf-8')), mimetype='text/plain')).execute()
                        else:
                            service.files().create(body={'name': f'REGISTRO_ENVIOS_{nombre_act}.txt', 'parents': [id_cli]}, media_body=MediaIoBaseUpload(io.BytesIO(linea.encode('utf-8')), mimetype='text/plain')).execute()

                        st.success(f"✅ Recibido: REF-{ref_id}")
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            st.subheader("📥 Mis Impuestos")
            a_bus = st.selectbox("Año consulta:", ["2026", "2025"], key="bus_a")
            q_cli_imp = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
            res_cli_imp = service.files().list(q=q_cli_imp).execute().get('files', [])
            if res_cli_imp:
                id_cli_imp = res_cli_imp[0]['id']
                q_ano = f"name = '{a_bus}' and '{id_cli_imp}' in parents and trashed = false"
                res_ano = service.files().list(q=q_ano).execute().get('files', [])
                if res_ano:
                    id_ano = res_ano[0]['id']
                    todas = service.files().list(q=f"'{id_ano}' in parents and trashed = false").execute().get('files', [])
                    id_imp = next((f['id'] for f in todas if f['name'].strip().upper() == "IMPUESTOS PRESENTADOS"), None)
                    if id_imp:
                        docs = service.files().list(q=f"'{id_imp}' in parents and trashed = false").execute().get('files', [])
                        for d in docs:
                            ca, cb = st.columns([0.7, 0.3])
                            ca.write(f"📄 {d['name']}")
                            req = service.files().get_media(fileId=d['id'])
                            fh = io.BytesIO()
                            downloader = MediaIoBaseDownload(fh, req)
                            done = False
                            while not done: _, done = downloader.next_chunk()
                            cb.download_button("Bajar", fh.getvalue(), file_name=d['name'], key=d['id'], use_container_width=True)
                    else: st.info("No hay carpeta de 'IMPUESTOS PRESENTADOS' aún.")

        with tab3:
            st.subheader("⚙️ Panel de Gestión")
            ad_pass = st.text_input("Clave Maestra:", type="password", key="adm_key")
            if ad_pass == PASSWORD_ADMIN:
                st.markdown("### 📢 Control de Avisos y Estados")
                with st.expander("Modificar Portal de Cliente", expanded=True):
                    email_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                    c_ad1, c_ad2 = st.columns(2)
                    est_nuevo = c_ad1.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                    prio_nueva = c_ad2.selectbox("Prioridad:", ["Información", "Acción requerida", "Urgente", "Trámite finalizado"])
                    msg_nuevo = st.text_area("Mensaje:")
                    
                    if st.button("💾 ACTUALIZAR PORTAL", use_container_width=True):
                        DATA_AVISOS[email_sel] = {
                            "estado": est_nuevo, "mensaje": msg_nuevo, 
                            "prioridad": prio_nueva, "fecha": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                        }
                        guardar_json(AVISOS_FILE, DATA_AVISOS)
                        st.success("Guardado.")
                        st.rerun()

                st.markdown("---")
                st.markdown("### 👥 Registro de Clientes")
                col_a, col_b = st.columns(2)
                n_em, n_no = col_a.text_input("Email:"), col_b.text_input("Nombre Drive:")
                if st.button("REGISTRAR CLIENTE", use_container_width=True):
                    if n_em and n_no:
                        DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                        guardar_json(DB_FILE, DICCIONARIO_CLIENTES)
                        st.rerun()
                
                for em, nom in list(DICCIONARIO_CLIENTES.items()):
                    ci, cd = st.columns([0.7, 0.3])
                    ci.write(f"**{nom}** ({em})")
                    if cd.button("Borrar", key=f"del_{em}", use_container_width=True):
                        del DICCIONARIO_CLIENTES[em]
                        guardar_json(DB_FILE, DICCIONARIO_CLIENTES)
                        st.rerun()

