import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
    .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px; text-align: center; font-size: 0.9rem; }
    
    /* Estilos para Avisos y Estados */
    .estado-box { background-color: #fff9c4; padding: 10px; border-radius: 10px; color: #827717; font-weight: bold; margin-bottom: 15px; text-align: center; border: 1px solid #fbc02d; }
    .aviso-urgente { padding: 15px; border-radius: 10px; background-color: #ffebee; border-left: 6px solid #f44336; color: #b71c1c; margin: 10px 0; }
    .aviso-info { padding: 15px; border-radius: 10px; background-color: #e3f2fd; border-left: 6px solid #2196f3; color: #0d47a1; margin: 10px 0; }
    
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<h2 style="text-align:center;">Acceso Privado</h2>', unsafe_allow_html=True)
        password_input = st.text_input("Contraseña del Portal:", type="password")
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
    AVISOS_FILE = "avisos_db.json" # Nuevo archivo para avisos personalizados

    # Funciones de Datos
    def cargar_datos(archivo, inicial):
        if os.path.exists(archivo):
            try:
                with open(archivo, "r", encoding="utf-8") as f: return json.load(f)
            except: return inicial
        return inicial

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
        c_logout1.markdown(f'<div class="user-info">Sesión de: {nombre_act}</div>', unsafe_allow_html=True)
        if c_logout2.button("🔒 SALIR"):
            del st.session_state["user_email"]
            st.rerun()

        # --- SECCIÓN DE ESTADO Y AVISOS ---
        info_cliente = DB_AVISOS.get(email_act, {"estado": "Pendiente de recibir facturas", "aviso": "Recuerda subir tus facturas antes del día 5.", "tipo": "info"})
        
        st.markdown(f'<div class="estado-box">📊 ESTADO ACTUAL: {info_cliente["estado"]}</div>', unsafe_allow_html=True)
        clase_aviso = "aviso-urgente" if info_cliente["tipo"] == "urgente" else "aviso-info"
        st.markdown(f'<div class="{clase_aviso}">📢 <b>AVISO PARA {nombre_act.split()[0].upper()}:</b> {info_cliente["aviso"]}</div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR DOCUMENTOS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)

        with tab1:
            c1, c2 = st.columns(2)
            a_sel = c1.selectbox("Año", ["2026", "2025"])
            t_sel = c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Tipo de documento:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Selecciona archivo (PDF o Imagen)", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if arc and st.button("🚀 ENVIAR AHORA"):
                try:
                    # Renombrado Automático Profesional
                    ahora = datetime.datetime.now()
                    ext = os.path.splitext(arc.name)[1]
                    tipo_corto = "EMITIDA" if "EMITIDAS" in tipo_sel else "GASTO"
                    nombre_profesional = f"{ahora.strftime('%Y-%m-%d')}_{tipo_corto}_{nombre_act.replace(' ', '_')}{ext}"
                    
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
                        
                        # Subida optimizada sin guardar en disco local permanentemente
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream', resumable=True)
                        service.files().create(body={'name': nombre_profesional, 'parents': [id_final]}, media_body=media).execute()
                        
                        id_just = f"REF-{ahora.strftime('%y%m%d%H%M')}"
                        st.markdown(f'<div class="justificante"><b>✅ RECIBIDO</b><br>Archivo: {nombre_profesional}<br>Ref: {id_just}</div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            # (Tu lógica de descarga de impuestos se mantiene igual, es perfecta)
            st.subheader("📥 Mis Impuestos Presentados")
            # ... (resto del código de tab2)

        with tab3:
            st.subheader("⚙️ Panel de Control de Asesoría")
            ad_pass = st.text_input("Clave Maestra:", type="password", key="adm_key")
            if ad_pass == PASSWORD_ADMIN:
                
                # --- NUEVO: GESTIÓN DE AVISOS Y ESTADOS ---
                st.write("---")
                st.write("### 📢 Actualizar Estado y Avisos")
                cli_sel = st.selectbox("Seleccionar Cliente:", list(DICCIONARIO_CLIENTES.keys()))
                nuevo_estado = st.text_input("Estado (ej: Presentado, Revisando...):")
                nuevo_aviso = st.text_area("Mensaje de aviso:")
                tipo_aviso = st.radio("Gravedad:", ["info", "urgente"], horizontal=True)
                
                if st.button("ACTUALIZAR PORTAL DEL CLIENTE"):
                    DB_AVISOS[cli_sel] = {"estado": nuevo_estado, "aviso": nuevo_aviso, "tipo": tipo_aviso}
                    guardar_datos(AVISOS_FILE, DB_AVISOS)
                    st.success("✅ Portal del cliente actualizado")

                st.write("---")
                # (Tu lógica de registrar/eliminar clientes se mantiene igual)
