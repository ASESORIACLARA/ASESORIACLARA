import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y BASES DE DATOS LOCALES ---
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

# --- 2. SISTEMA DE LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    # Cabecera para móvil en Login
    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 1.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: clamp(1.5rem, 8vw, 2.2rem);">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 5px; font-size: 0.9rem;">Acceso Clientes</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        password_input = st.text_input("Contraseña del Portal:", type="password")
        if st.button("ENTRAR", use_container_width=True):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"

    # --- 3. ESTILOS CSS AVANZADOS (RESPONSIVE) ---
    st.markdown("""
        <style>
        /* Ajustes de contenedores */
        .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        
        /* Cabecera Adaptable */
        .header-box { background-color: #223a8e; padding: 1.2rem; border-radius: 15px; text-align: center; margin-bottom: 1rem; }
        .header-box h1 { color: white !important; margin: 0; font-size: clamp(1.3rem, 7vw, 2.2rem); font-weight: bold; letter-spacing: 1px; }
        
        /* Paneles de Usuario y Estado */
        .user-info { background-color: #f0f4ff; padding: 8px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 10px; text-align: center; font-size: 0.85rem; border: 1px solid #d1e0ff; }
        .status-panel { background: #ffffff; padding: 12px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .badge { padding: 5px 12px; border-radius: 15px; font-size: 0.7rem; font-weight: bold; color: white; text-transform: uppercase; display: inline-block; margin-top: 5px; }
        .bg-pendiente { background-color: #f59e0b; } .bg-revision { background-color: #3b82f6; } .bg-presentado { background-color: #10b981; }
        
        /* Globos de Aviso Estilo App */
        .globo-aviso { border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 5px solid; position: relative; font-size: 0.9rem; }
        .aviso-urgente { background: #fef2f2; border-left-color: #ef4444; color: #991b1b; }
        .aviso-info { background: #eff6ff; border-left-color: #3b82f6; color: #1e40af; }
        .aviso-finalizado { background: #f0fdf4; border-left-color: #10b981; color: #166534; }
        
        /* Ocultar elementos innecesarios */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stSidebar"] { display: none; }
        </style>
        <div class="header-box"><h1>ASESORIACLARA</h1></div>
    """, unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenida")
        em_log = st.text_input("Introduce tu email registrado:")
        if st.button("ACCEDER AL PORTAL", use_container_width=True):
            if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                st.session_state["user_email"] = em_log.lower().strip()
                st.rerun()
            else: st.error("Email no encontrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]
        config_cliente = DATA_AVISOS.get(email_act, {"estado": "Pendiente documentación", "mensaje": "", "prioridad": "Información", "fecha": ""})

        # Logout y Nombre
        c_out1, c_out2 = st.columns([0.7, 0.3])
        c_out1.markdown(f'<div class="user-info">👤 {nombre_act}</div>', unsafe_allow_html=True)
        if c_out2.button("SALIR", use_container_width=True):
            del st.session_state["user_email"]
            st.rerun()

        # Panel de Estado (Visible en Móvil)
        b_col = "bg-presentado" if config_cliente['estado'] == "Presentado" else "bg-revision" if config_cliente['estado'] == "En revisión" else "bg-pendiente"
        st.markdown(f"""
            <div class="status-panel">
                <div style="font-size: 0.8rem; color: #64748b;">ESTADO DEL TRIMESTRE (1T 2026)</div>
                <div class="badge {b_col}">{config_cliente['estado']}</div>
            </div>
        """, unsafe_allow_html=True)

        # Globos de Aviso dinámicos
        if config_cliente['mensaje']:
            est_g = "aviso-urgente" if "Urgente" in config_cliente['prioridad'] else "aviso-finalizado" if "finalizado" in config_cliente['prioridad'] else "aviso-info"
            st.markdown(f"""
                <div class="globo-aviso {est_g}">
                    <div style="font-size: 0.7rem; opacity: 0.8; margin-bottom: 4px;">📅 {config_cliente['fecha']}</div>
                    {config_cliente['mensaje']}
                </div>
            """, unsafe_allow_html=True)
            if st.button("MARCAR COMO LEÍDO ✓", use_container_width=True):
                config_cliente['mensaje'] = ""
                DATA_AVISOS[email_act] = config_cliente
                guardar_json(AVISOS_FILE, DATA_AVISOS)
                st.rerun()

        # TABS (Diseño nativo responsive)
        tab1, tab2, tab3 = st.tabs(["📤 SUBIR", "📥 MIS DOCS", "⚙️ GESTIÓN"])

        with open('token.pickle', 'rb') as t: creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)

        with tab1:
            st.write("### Enviar Documentación")
            c1, c2 = st.columns(2)
            a_sel = c1.selectbox("Año", ["2026", "2025"])
            t_sel = c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Tipo de factura:", ["EMITIDA", "GASTO"], horizontal=True)
            arc = st.file_uploader("Cargar archivo", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if arc and st.button("🚀 SUBIR AHORA", use_container_width=True):
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
                        ref = ahora.strftime('%Y%m%d%H%M%S')
                        ext = os.path.splitext(arc.name)[1]
                        nuevo_nombre = f"{ahora.strftime('%Y-%m-%d')}_{tipo_sel}_REF-{ref}{ext}"
                        
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype=arc.type)
                        service.files().create(body={'name': nuevo_nombre, 'parents':[id_final]}, media_body=media).execute()
                        st.success(f"Enviado: {nuevo_nombre}")
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            st.write("### Mis Impuestos")
            a_bus = st.selectbox("Selecciona Año:", ["2026", "2025"], key="b2")
            # Lógica de búsqueda simplificada para móvil
            st.info("Aquí aparecerán tus modelos presentados.")

        with tab3:
            st.write("### Área de Administración")
            ad_pass = st.text_input("Clave Maestra:", type="password", key="adm")
            if ad_pass == PASSWORD_ADMIN:
                st.markdown("---")
                # PANEL DE CONTROL AVISOS
                email_sel = st.selectbox("Cliente:", list(DICCIONARIO_CLIENTES.keys()), format_func=lambda x: DICCIONARIO_CLIENTES[x])
                
                est_nuevo = st.selectbox("Estado:", ["Pendiente documentación", "En revisión", "Presentado"])
                prio_nueva = st.selectbox("Prioridad Aviso:", ["Información", "Acción requerida", "Urgente", "Trámite finalizado"])
                msg_nuevo = st.text_area("Mensaje del Aviso:")
                
                if st.button("💾 ACTUALIZAR PORTAL", use_container_width=True):
                    f_ahora = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    DATA_AVISOS[email_sel] = {"estado": est_nuevo, "mensaje": msg_nuevo, "prioridad": prio_nueva, "fecha": f_ahora}
                    guardar_json(AVISOS_FILE, DATA_AVISOS)
                    st.success("Actualizado")
                    st.rerun()
                
                st.markdown("---")
                # GESTIÓN DE CLIENTES
                st.write("### Registrar Cliente")
                n_em = st.text_input("Nuevo Email:")
                n_no = st.text_input("Nombre Carpeta Drive:")
                if st.button("AÑADIR", use_container_width=True):
                    if n_em and n_no:
                        DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                        guardar_json(DB_FILE, DICCIONARIO_CLIENTES)
                        st.rerun()
