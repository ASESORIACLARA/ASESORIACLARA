import streamlit as st
import os, pickle, json, io, datetime, pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

ID_ARCHIVO_CLIENTES = "1itfmAyRcHoS32bLf_bJFfoYJ3yW4pbED" 
ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
PASSWORD_ADMIN = "GEST_LA_2025"

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style="background-color: #1e3a8a; padding: 1.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="color: white !important; margin: 0; font-size: clamp(1.8rem, 8vw, 2.5rem); line-height: 1.2;">ASESORIACLARA</h1>
            <p style="color: #d1d5db; margin-top: 10px; font-size: clamp(0.9rem, 4vw, 1.1rem);">Tu gestión, más fácil y transparente</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password_input = st.text_input("Contraseña del portal:", type="password")
        if st.button("ENTRAR AL PORTAL", use_container_width=True):
            if password_input == "clara2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

if check_password():
    try:
        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        service = build('drive', 'v3', credentials=creds)
    except Exception:
        st.error("Error de conexión con Drive.")
        st.stop()

    # --- FUNCIÓN CRÍTICA: ENCONTRAR O CREAR CARPETAS ---
    def get_f(n, p):
        q_f = f"name='{n}' and '{p}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        rf = service.files().list(q=q_f).execute().get('files', [])
        if rf: return rf[0]['id']
        return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']

    def listar_archivos_carpeta(folder_id):
        query = f"'{folder_id}' in parents and trashed = false"
        return service.files().list(q=query, fields="files(id, name, webContentLink)").execute().get('files', [])

    def cargar_clientes_drive():
        clis = {"asesoriaclara0@gmail.com": "LORENA ALONSO"}
        try:
            req = service.files().get_media(fileId=ID_ARCHIVO_CLIENTES)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, req)
            done = False
            while not done: _, done = downloader.next_chunk()
            fh.seek(0)
            df = pd.read_csv(fh)
            df.columns = df.columns.str.strip().str.lower()
            for _, r in df.iterrows():
                e = str(r['email']).strip().lower()
                n = str(r['nombre']).strip()
                if e and n: clis[e] = n
        except: pass
        return clis

    def guardar_clientes_drive(dicc):
        df = pd.DataFrame(list(dicc.items()), columns=['email', 'nombre'])
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')
        service.files().update(fileId=ID_ARCHIVO_CLIENTES, media_body=media).execute()

    if 'dicc' not in st.session_state:
        st.session_state['dicc'] = cargar_clientes_drive()
    DICCIONARIO_CLIENTES = st.session_state['dicc']

    st.markdown("""
        <style>
        .header-box { background-color: #223a8e; padding: 1.2rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
        .header-box h1 { color: white !important; margin: 0; font-size: clamp(1.5rem, 7vw, 2rem); font-weight: bold; }
        .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; margin-bottom: 15px; text-align: center; font-size: 0.9rem; }
        </style>
        <div class="header-box"><h1>ASESORIACLARA</h1></div>
    """, unsafe_allow_html=True)

    if "user_email" not in st.session_state:
        st.write("### 👋 Bienvenido/a")
        em_log = st.text_input("Correo electrónico:")
        if st.button("ACCEDER"):
            email_limpio = em_log.lower().strip()
            if email_limpio in DICCIONARIO_CLIENTES:
                st.session_state["user_email"] = email_limpio
                st.rerun()
            else: st.error("No registrado.")
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES.get(email_act, "USUARIO")
        st.markdown(f'<div class="user-info">Sesión: {nombre_act}</div>', unsafe_allow_html=True)
        
        if st.button("🔒 SALIR"):
            del st.session_state["user_email"]
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR / VER", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

        with tab1:
            st.subheader("📁 Tus Documentos")
            c_a, c_b = st.columns(2)
            a_sel = c_a.selectbox("Año", ["2026", "2025"])
            t_sel = c_b.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_sel = st.radio("Tipo:", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            
            # BUSCAR CARPETA PADRE DEL CLIENTE
            q_c = f"name = '{nombre_act}' and '{ID_CARPETA_CLIENTES}' in parents and trashed = false"
            res_c = service.files().list(q=q_c).execute().get('files', [])
            
            if res_c:
                id_cli = res_c[0]['id']
                # Crear/Obtener la ruta: Año -> Tipo -> Trimestre
                id_final = get_f(t_sel, get_f(tipo_sel, get_f(a_sel, id_cli)))
                
                arc = st.file_uploader("Subir factura", type=['pdf', 'jpg', 'png', 'jpeg'])
                if arc and st.button("🚀 SUBIR"):
                    media = MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype=arc.type)
                    service.files().create(body={'name': arc.name, 'parents': [id_final]}, media_body=media).execute()
                    st.success(f"¡Enviado a tu carpeta {nombre_act}!")
                    st.balloons()
                    st.rerun()
                
                st.write("---")
                st.write("📂 **Lo que has enviado en esta sección:**")
                lista = listar_archivos_carpeta(id_final)
                if lista:
                    for f in lista: st.markdown(f"📄 [{f['name']}]({f['webContentLink']})")
                else: st.info("Todavía no has subido archivos en esta carpeta.")
            else:
                st.error(f"⚠️ Error: No existe una carpeta en Drive llamada '{nombre_act}'. Créala para poder subir archivos.")

        with tab2:
            st.subheader("📥 Mis Impuestos")
            if res_c:
                id_imp = get_f("IMPUESTOS PRESENTADOS", res_c[0]['id'])
                lista_imp = listar_archivos_carpeta(id_imp)
                if lista_imp:
                    for f in lista_imp: st.markdown(f"📑 [{f['name']}]({f['webContentLink']})")
                else: st.info("No hay impuestos subidos aún por la asesoría.")

        with tab3:
            st.subheader("⚙️ Gestión")
            ad_pass = st.text_input("Clave Maestra:", type="password")
            if ad_pass == PASSWORD_ADMIN:
                n_em = st.text_input("Nuevo Email:")
                n_no = st.text_input("Nombre en Drive (exacto):")
                if st.button("REGISTRAR CLIENTE"):
                    if n_em and n_no:
                        DICCIONARIO_CLIENTES[n_em.lower().strip()] = n_no
                        guardar_clientes_drive(DICCIONARIO_CLIENTES)
                        st.session_state['dicc'] = DICCIONARIO_CLIENTES
                        st.success("¡Cliente registrado y sincronizado!")
                        st.rerun()
                st.write("---")
                for m, n in DICCIONARIO_CLIENTES.items(): st.text(f"• {n} ({m})")

