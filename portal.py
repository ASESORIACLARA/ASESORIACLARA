import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS (Mejora 1: Estilos de Avisos) ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
    .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px; text-align: center; font-size: 0.9rem; }
    /* Mejora 3: Estado del Trimestre */
    .estado-box { background-color: #fff9c4; padding: 10px; border-radius: 10px; color: #827717; font-weight: bold; margin-bottom: 15px; text-align: center; border: 1px solid #fbc02d; }
    /* Mejora 1: Cuadros de Avisos */
    .aviso-urgente { padding: 15px; border-radius: 10px; background-color: #ffebee; border-left: 6px solid #f44336; margin-bottom: 10px; color: #b71c1c; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
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

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes(diccionario):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

    DICCIONARIO_CLIENTES = cargar_clientes()

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

        # --- SECCIÓN SUPERIOR ACTUALIZADA ---
        c_logout1, c_logout2 = st.columns([4,1])
        c_logout1.markdown(f'<div class="user-info">Sesión: {nombre_act}</div>', unsafe_allow_html=True)
        if c_logout2.button("🔒 SALIR"):
            del st.session_state["user_email"]
            st.rerun()

        # Mejora 3: Estado del Trimestre (Visible debajo de Sesión)
        st.markdown('<div class="estado-box">📊 ESTADO 1T 2026: 🟡 En revisión</div>', unsafe_allow_html=True)

        # Mejora 1 y 2: Sistema de Avisos y Botón "Entendido"
        col_av, col_btn_av = st.columns([3,1])
        with col_av:
            st.markdown('<div class="aviso-urgente"><strong>📢 ACCIÓN REQUERIDA:</strong> Pendiente subir facturas de gastos de Febrero.</div>', unsafe_allow_html=True)
        with col_btn_av:
            if st.button("✔️ LEÍDO"):
                st.balloons()
                # El registro se guarda en un archivo de texto por cliente (Mejora 2)
                with open(f"REGISTRO_AVISOS_{nombre_act}.txt", "a") as f_log:
                    f_log.write(f"{datetime.datetime.now()}: Cliente confirmó lectura del aviso.\n")
                st.success("Confirmado")

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
                    # Mejora 4: Renombrado Automático Profesional
                    ahora = datetime.datetime.now()
                    id_just = f"REF-{ahora.strftime('%Y%m%d%H%M%S')}"
                    ext = os.path.splitext(arc.name)[1]
                    tipo_corto = "EMITIDA" if "EMITIDAS" in tipo_sel else "GASTO"
                    nombre_profesional = f"{ahora.strftime('%Y-%m-%d')}_{tipo_corto}_{id_just}{ext}"
                    
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
                        
                        # Subida con el NUEVO NOMBRE (Mejora 4)
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream', resumable=True)
                        service.files().create(body={'name': nombre_profesional, 'parents': [id_final]}, media_body=media).execute()
                        
                        # Registro de envíos (Tu lógica original con el nuevo nombre)
                        linea = f"{ahora.strftime('%d/%m/%Y %H:%M')}|{nombre_profesional}|{id_just}\n"
                        q_reg = f"name = 'REGISTRO_ENVIOS_{nombre_act}.txt' and '{id_cli}' in parents and trashed = false"
                        res_reg = service.files().list(q=q_reg).execute().get('files', [])
                        
                        if res_reg:
                            f_id = res_reg[0]['id']
                            old_c = service.files().get_media(fileId=f_id).execute().decode('utf-8')
                            service.files().update(fileId=f_id, media_body=MediaIoBaseUpload(io.BytesIO((old_c + linea).encode('utf-8')), mimetype='text/plain')).execute()
                        else:
                            service.files().create(body={'name': f'REGISTRO_ENVIOS_{nombre_act}.txt', 'parents': [id_cli]}, media_body=MediaIoBaseUpload(io.BytesIO(linea.encode('utf-8')), mimetype='text/plain')).execute()

                        st.markdown(f'<div class="justificante"><b>✅ RECIBIDO CORRECTAMENTE</b><br>Nuevo nombre: {nombre_profesional}<br>Ref: {id_just}</div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error al subir: {e}")

            # ... (Resto de tu lógica de tabla de últimos envíos se mantiene igual)

        with tab2:
            st.subheader("📥 Mis Impuestos")
            # ... (Toda tu lógica de descarga se mantiene igual)

        with tab3:
            st.subheader("⚙️ Gestión")
            ad_pass = st.text_input("Clave Maestra:", type="password", key="adm_key")
            if ad_pass == PASSWORD_ADMIN:
                # Aquí puedes gestionar los clientes (Tu lógica original)
                # Y en el futuro añadiremos aquí el editor de avisos
                col_a, col_b = st.columns(2)
                n_em = col_a.text_input("Email:")
                n_no = col_b.text_input("Nombre en Drive:")
                if st.button("REGISTRAR CLIENTE"):
                    if n_em and n_no:
                        DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                        guardar_clientes(DICCIONARIO_CLIENTES)
                        st.success("¡Registrado!")
                        st.rerun()
