import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: clamp(1.5rem, 8vw, 2.5rem);">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px; font-size: clamp(0.8rem, 4vw, 1.1rem);">Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
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

    # --- ESTILOS (MANTENIENDO EL MAESTRO + GLOBOS Y ESTADOS) ---
    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
        .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
        .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
        .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px; text-align: center; font-size: 0.9rem; }
        .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
        
        /* MEJORA: GLOBOS DE AVISO */
        .globo-aviso { border-radius: 10px; padding: 12px; margin: 8px 0; border-left: 5px solid; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .aviso-urgente { background: #fdf2f2; border-left-color: #e74c3c; color: #c0392b; }
        .aviso-finalizado { background: #f0fff4; border-left-color: #2ecc71; color: #22543d; }
        
        /* MEJORA: ESTADO TRIMESTRE */
        .status-panel { background: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #dee2e6; text-align: center; margin-bottom: 15px; }
        .badge { padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
        .bg-pendiente { background-color: #f1c40f; } .bg-presentado { background-color: #2ecc71; }
        
        [data-testid="stSidebar"] { display: none; }
        </style>
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
            <p>Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenida al Portal")
        st.info("Introduce tu correo registrado para acceder.")
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
        c_logout1.markdown(f'<div class="user-info">Sesión de: {nombre_act}</div>', unsafe_allow_html=True)
        
        # --- MEJORA: ESTADO DEL TRIMESTRE (Debajo de Sesión) ---
        tri_demo = "1T 2026"
        est_demo = "Pendiente documentación" # Esto lo controlarás desde el JSON/Admin
        badge_col = "bg-pendiente" if "Pendiente" in est_demo else "bg-presentado"
        st.markdown(f'<div class="status-panel">Trimestre Activo: <b>{tri_demo}</b> | <span class="badge {badge_col}">{est_demo}</span></div>', unsafe_allow_html=True)

        # --- MEJORA: SISTEMA DE AVISOS (GLOBOS) ---
        st.markdown(f'<div class="globo-aviso aviso-urgente">⚠️ <b>Urgente:</b> Faltan facturas de gastos de febrero. <br><small>2026-03-03</small></div>', unsafe_allow_html=True)
        if st.button("ENTENDIDO ✓"):
             st.toast("Confirmado")

        if c_logout2.button("🔒 SALIR"):
            del st.session_state["user_email"]
            st.rerun()

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
                        
                        # --- MEJORA: RENOMBRADO AUTOMÁTICO PROFESIONAL ---
                        ahora = datetime.datetime.now()
                        id_just = f"REF-{ahora.strftime('%Y%m%d%H%M%S')}"
                        ext = os.path.splitext(arc.name)[1]
                        tipo_nom = "EMITIDA" if "EMITIDAS" in tipo_sel else "GASTO"
                        nuevo_nombre_archivo = f"{ahora.strftime('%Y-%m-%d')}_{tipo_nom}_{id_just}{ext}"
                        
                        # Subida con nuevo nombre
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype=arc.type)
                        service.files().create(body={'name': nuevo_nombre_archivo, 'parents':[id_final]}, media_body=media).execute()
                        
                        # Registro de envíos (Mantenido el sistema original)
                        linea = f"{ahora.strftime('%d/%m/%Y %H:%M')}|{nuevo_nombre_archivo}|{id_just}\n"
                        q_reg = f"name = 'REGISTRO_ENVIOS_{nombre_act}.txt' and '{id_cli}' in parents and trashed = false"
                        res_reg = service.files().list(q=q_reg).execute().get('files', [])
                        
                        if res_reg:
                            f_id = res_reg[0]['id']
                            old_c = service.files().get_media(fileId=f_id).execute().decode('utf-8')
                            new_c = old_c + linea
                            service.files().update(fileId=f_id, media_body=MediaIoBaseUpload(io.BytesIO(new_c.encode('utf-8')), mimetype='text/plain')).execute()
                        else:
                            meta = {'name': f'REGISTRO_ENVIOS_{nombre_act}.txt', 'parents': [id_cli]}
                            service.files().create(body=meta, media_body=MediaIoBaseUpload(io.BytesIO(linea.encode('utf-8')), mimetype='text/plain')).execute()

                        st.markdown(f'<div class="justificante"><b>✅ RECIBIDO CORRECTAMENTE</b><br>Ref: {id_just}</div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error al subir: {e}")

            st.write("---")
            st.subheader("📋 Tus últimos envíos")
            try:
                q_cli_tab = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                res_cli_tab = service.files().list(q=q_cli_tab).execute().get('files', [])
                if res_cli_tab:
                    id_cli_tab = res
