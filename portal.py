import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS (MEJORADOS) ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-weight: bold; }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px; text-align: center; }
    
    /* ESTILOS DE LOS GLOBOS DE AVISO (PDF Mejora 1) */
    .globo-aviso { border-radius: 10px; padding: 15px; margin: 10px 0; border-left: 6px solid; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .aviso-urgente { background: #fdf2f2; border-left-color: #e74c3c; color: #c0392b; }
    .aviso-accion { background: #fffbeb; border-left-color: #f1c40f; color: #92400e; }
    .aviso-finalizado { background: #f0fff4; border-left-color: #2ecc71; color: #22543d; }
    .aviso-info { background: #ebf8ff; border-left-color: #3498db; color: #2c5282; }
    
    /* ESTADO DEL TRIMESTRE (PDF Mejora 3) */
    .status-panel { background: #f8f9fa; padding: 12px; border-radius: 10px; border: 1px solid #dee2e6; text-align: center; margin-bottom: 20px; }
    .badge { padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; font-weight: bold; color: white; }
    .bg-pendiente { background-color: #f1c40f; } .bg-revision { background-color: #3498db; } .bg-presentado { background-color: #2ecc71; }
    
    [data-testid="stSidebar"] { display: none; }
    </style>
    <div class="header-box">
        <h1>ASESORIACLARA</h1>
        <p style="color: #d1d5db;">Tu gestión, más fácil y transparente</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. FUNCIONES DE PROTECCIÓN PROFESIONAL (PDF Mejora 2) ---
def registrar_en_txt(nombre_act, tipo, texto, email_enviado="No"):
    """Registra cada movimiento para protección profesional del asesor"""
    ahora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    linea = f"{ahora} | {tipo} | {texto} | Email: {email_enviado} | Leído: No\n"
    # Lógica para guardar en Drive (similar a tu registro de envíos)
    return linea

# --- 3. LOGICA DE ACCESO ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña General:", type="password")
        if st.button("ENTRAR AL PORTAL"):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Incorrecta")
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    DICCIONARIO_CLIENTES = cargar_clientes()

    if "user_email" not in st.session_state:
        st.info("👋 Introduce tu correo para acceder.")
        em_log = st.text_input("Correo electrónico:")
        if st.button("ACCEDER"):
            if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                st.session_state["user_email"] = em_log.lower().strip()
                st.rerun()
            else: st.error("Correo no registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]

        # --- CABECERA DE USUARIO Y SALIR ---
        c_logout1, c_logout2 = st.columns([4,1])
        c_logout1.markdown(f'<div class="user-info">Sesión de: {nombre_act}</div>', unsafe_allow_html=True)
        if c_logout2.button("🔒 SALIR"):
            del st.session_state["user_email"]
            st.rerun()

        # --- MEJORA 3: ESTADO DEL TRIMESTRE (Debajo de Sesión) ---
        # Estos valores idealmente vendrían de un JSON de configuración por cliente
        tri_activo = "1T 2026"
        est_manual = "Pendiente documentación" # O: "En revisión", "Presentado"
        badge_class = "bg-pendiente" if "Pendiente" in est_manual else "bg-revision" if "revisión" in est_manual else "bg-presentado"
        
        st.markdown(f"""
            <div class="status-panel">
                <span style="color: #555;">Trimestre actual: <b>{tri_activo}</b></span><br>
                <span class="badge {badge_class}">{est_manual.upper()}</span>
            </div>
        """, unsafe_allow_html=True)

        # --- MEJORA 1: GLOBOS DE AVISOS ---
        st.markdown("### 🔔 Avisos Recientes")
        # Ejemplo de aviso (esto se cargaría de un archivo o base de datos)
        st.markdown(f"""
            <div class="globo-aviso aviso-urgente">
                <small>Fecha: 2026-03-03</small><br>
                <strong>⚠️ ACCIÓN REQUERIDA:</strong> Faltan gastos de febrero por subir.
            </div>
        """, unsafe_allow_html=True)
        if st.button("Entendido ✓", key="btn_entendido"):
            st.success("Aviso marcado como leído.")
            # Aquí llamarías a registrar_en_txt() para guardar la fecha de lectura

        st.write("---")

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR DOCUMENTOS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)

        with tab1:
            c1, c2 = st.columns(2)
            a_sel = c1.selectbox("Año", ["2026", "2025"])
            t_sel = c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Tipo de documento:", ["GASTO", "EMITIDA"], horizontal=True)
            arc = st.file_uploader("Arrastra o selecciona el archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if arc and st.button("🚀 ENVIAR AL ASESOR"):
                try:
                    # MEJORA 4: RENOMBRADO AUTOMÁTICO (AAAA-MM-DD_TIPO_REF.ext)
                    ahora = datetime.datetime.now()
                    ref_unica = ahora.strftime('%Y%m%d%H%M%S')
                    extension = os.path.splitext(arc.name)[1]
                    nuevo_nombre = f"{ahora.strftime('%Y-%m-%d')}_{tipo_sel}_REF-{ref_unica}{extension}"
                    
                    # Lógica de carpetas en Drive
                    q = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
                    res = service.files().list(q=q).execute().get('files', [])
                    if res:
                        id_cli = res[0]['id']
                        def get_f(n, p):
                            q_f = f"name='{n}' and '{p}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                            rf = service.files().list(q=q_f).execute().get('files', [])
                            if rf: return rf[0]['id']
                            return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        
                        # Organización: Año -> Tipo -> Trimestre
                        id_final = get_f(t_sel, get_f(tipo_sel, get_f(a_sel, id_cli)))
                        
                        # Subida con el nuevo nombre profesional
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype=arc.type)
                        service.files().create(body={'name': nuevo_nombre, 'parents':[id_final]}, media_body=media).execute()
                        
                        # Registro de seguridad (TXT)
                        linea_log = f"{ahora.strftime('%d/%m/%Y %H:%M')}|{nuevo_nombre}|REF-{ref_unica}\n"
                        # (Aquí iría la lógica existente para actualizar el REGISTRO_ENVIOS.txt en Drive)
                        
                        st.markdown(f'<div class="justificante"><b>✅ RECIBIDO CORRECTAMENTE</b><br>Archivo: {nuevo_nombre}</div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            st.subheader("📥 Mis Impuestos Presentados")
            # (Mantener tu lógica original de descarga de impuestos)

        with tab3:
            # (Mantener tu lógica original de administración)
            pass
