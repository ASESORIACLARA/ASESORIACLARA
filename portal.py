import streamlit as st
import os, pickle, json, io, datetime, pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

# ID de tus archivos y carpetas
ID_ARCHIVO_CLIENTES = "1itfmAyRcHoS32bLf_bJFfoYJ3yW4pbED" 
ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
PASSWORD_ADMIN = "GEST_LA_2025"

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
    with open('token.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('drive', 'v3', credentials=creds)

    def cargar_clientes_drive():
        try:
            request = service.files().get_media(fileId=ID_ARCHIVO_CLIENTES)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done: _, done = downloader.next_chunk()
            fh.seek(0)
            df = pd.read_csv(fh)
            # Limpiamos espacios y pasamos a minúsculas para evitar errores
            df.columns = df.columns.str.strip().str.lower()
            return dict(zip(df['email'].str.strip().str.lower(), df['nombre'].str.strip()))
        except Exception as e:
            st.error(f"Error cargando base de datos: {e}")
            return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def guardar_clientes_drive(dicc):
        df = pd.DataFrame(list(dicc.items()), columns=['email', 'nombre'])
        csv_data = df.to_csv(index=False)
        media = MediaIoBaseUpload(io.BytesIO(csv_data.encode('utf-8')), mimetype='text/csv')
        service.files().update(fileId=ID_ARCHIVO_CLIENTES, media_body=media).execute()

    DICCIONARIO_CLIENTES = cargar_clientes_drive()

    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
        .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: clamp(1.5rem, 7vw, 2.5rem); font-weight: bold; }
        .header-box p { color: #d1d5db; margin-top: 5px; font-size: clamp(0.8rem, 4vw, 1rem); }
        .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 15px; text-align: center; font-size: 0.9rem; }
        .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
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
                email_limpio = em_log.lower().strip()
                if email_limpio in DICCIONARIO_CLIENTES:
                    st.session_state["user_email"] = email_limpio
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

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR DOCUMENTOS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])

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
                        media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype=arc.type)
                        service.files().create(body={'name':arc.name, 'parents':[id_final]}, media_body=media).execute()
                        st.markdown(f'<div class="justificante"><b>✅ RECIBIDO CORRECTAMENTE</b></div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error al subir: {e}")

        with tab2:
            st.subheader("📥 Mis Impuestos")
            st.info("Aquí aparecerán tus impuestos cuando los subas a la carpeta 'IMPUESTOS PRESENTADOS' de Drive.")

        with tab3:
            st.subheader("⚙️ Gestión de Clientes")
            ad_pass = st.text_input("Clave Maestra:", type="password")
            if ad_pass == PASSWORD_ADMIN:
                col_a, col_b = st.columns(2)
                n_em = col_a.text_input("Nuevo Email:")
                n_no = col_b.text_input("Nombre en Drive:")
                if st.button("REGISTRAR CLIENTE"):
                    if n_em and n_no:
                        DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                        guardar_clientes_drive(DICCIONARIO_CLIENTES)
                        st.success(f"¡{n_no} guardado en el Excel de Drive!")
                        st.rerun()
                
                st.write("---")
                st.write("📋 **Clientes registrados en Drive:**")
                for email, nombre in DICCIONARIO_CLIENTES.items():
                    st.text(f"• {nombre} ({email})")
