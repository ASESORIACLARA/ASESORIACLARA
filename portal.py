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

    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
        .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
        .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
        .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 10px; text-align: center; font-size: 0.9rem; }
        .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
        
        /* ESTILOS MEJORAS PDF */
        .status-panel { background: #f1f3f9; padding: 10px; border-radius: 12px; border: 1px solid #d1d5db; text-align: center; margin-bottom: 15px; }
        .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }
        .bg-rojo { background-color: #e74c3c; } .bg-amarillo { background-color: #f1c40f; } .bg-verde { background-color: #2ecc71; }
        .globo-aviso { border-radius: 10px; padding: 12px; margin: 10px 0; border-left: 6px solid; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .aviso-urgente { background: #fdf2f2; border-left-color: #e74c3c; }
        
        [data-testid="stSidebar"] { display: none; }
        </style>
        <div class="header-box">
            <h1>ASESORIACLARA</h1>
            <p>Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)

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

        # --- CABECERA SESIÓN ---
        c_logout1, c_logout2 = st.columns([4,1])
        c_logout1.markdown(f'<div class="user-info">Sesión de: {nombre_act}</div>', unsafe_allow_html=True)
        if c_logout2.button("🔒 SALIR"):
            del st.session_state["user_email"]
            st.rerun()

        # --- MEJORA: ESTADO TRIMESTRE (Página 3 PDF) ---
        st.markdown(f"""
            <div class="status-panel">
                <span style="color:#1e3a8a">Trimestre: <b>1T 2026</b></span> | 
                <span class="badge bg-amarillo">Pendiente documentación</span>
            </div>
        """, unsafe_allow_html=True)

        # --- MEJORA: SISTEMA DE AVISOS (Página 1 PDF) ---
        st.markdown(f"""
            <div class="globo-aviso aviso-urgente">
                <small>📅 03/03/2026</small><br>
                <strong>⚠️ URGENTE:</strong> Faltan facturas de gastos de febrero.
            </div>
        """, unsafe_allow_html=True)
        if st.button("ENTENDIDO ✓"): st.toast("Aviso marcado")

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
                        
                        # --- MEJORA: RENOMBRADO AUTOMÁTICO (Página 4 PDF) ---
                        ahora = datetime.datetime.now()
                        ref_id = ahora.strftime('%Y%m%d%H%M%S')
                        ext = os.path.splitext(arc.name)[1]
                        prefijo = "GASTO" if "GASTOS" in tipo_sel else "EMITIDA"
                        nuevo_nombre = f"{ahora.strftime('%Y-%m-%d')}_{prefijo}_REF-{ref_
