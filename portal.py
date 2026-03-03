import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN VISUAL Y ESTILOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; color: white; }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; text-align: center; margin-bottom: 10px; }
    
    /* Colores del Semáforo */
    .st-rojo { background-color: #ffebee; color: #b71c1c; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #f44336; }
    .st-amarillo { background-color: #fff9c4; color: #827717; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #fbc02d; }
    .st-verde { background-color: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #4caf50; }
    
    .aviso-caja { padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 6px solid #2196f3; background-color: #f0f7ff; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNCIONES DE BASE DE DATOS ---
DB_F, AV_F = "clientes_db.json", "avisos_db.json"

def load_j(f, d):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as f1: return json.load(f1)
        except: return d
    return d

def save_j(f, d):
    with open(f, "w", encoding="utf-8") as f1: json.dump(d, f1, indent=4, ensure_ascii=False)

# --- 3. SEGURIDAD Y ACCESO ---
def check_password():
    if "pw_ok" not in st.session_state: st.session_state["pw_ok"] = False
    if st.session_state["pw_ok"]: return True
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Acceso Privado</p></div>', unsafe_allow_html=True)
    pw = st.text_input("Contraseña General:", type="password")
    if st.button("ENTRAR") and pw == "clara2026":
        st.session_state["pw_ok"] = True
        st.rerun()
    return False

if check_password():
    ID_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PW_ADM = "GEST_LA_2025"
    D_CLI = load_j(DB_F, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    D_AVI = load_j(AV_F, {})

    if "u_mail" not in st.session_state:
        st.write("### 👋 Bienvenida al Portal")
        em = st.text_input("Introduce tu email registrado:")
        if st.button("ACCEDER") and em.lower().strip() in D_CLI:
            st.session_state["u_mail"] = em.lower().strip()
            st.rerun()
    else:
        mail = st.session_state["u_mail"]
        nom = D_CLI[mail]
        
        # Obtener avisos con protección contra errores (KeyError)
        inf = D_AVI.get(mail, {})
        txt_aviso = inf.get("texto", "Bienvenido/a. Ya puedes subir tus documentos.")
        est_aviso = inf.get("estado", "Pte de documentación")

        # Lógica de colores para el estado
        clase_color = "st-rojo"
        if "revisión" in est_aviso.lower(): clase_color = "st-amarillo"
        elif "presentado" in est_aviso.lower(): clase_color = "st-verde"

        st.markdown(f'<div class="user-info">Sesión iniciada: {nom}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{clase_color}">📊 ESTADO ACTUAL: {est_aviso.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="aviso-caja">📢 <b>AVISO:</b> {txt_aviso}</div>', unsafe_allow_html=True)

        if st.button("🔒 CERRAR SESIÓN"):
            del st.session_state["u_mail"]
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])
        
        # Conexión con Google Drive
        with open('token.pickle', 'rb') as tk: 
            srv = build('drive', 'v3', credentials=pickle.load(tk))

        with tab1:
            st.subheader("Subir Documentación")
            c1, c2 = st.columns(2)
            a_v = c1.selectbox("Año", ["2026", "2025"])
            t_v = c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_v = st.radio("Tipo de documento", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Arrastra aquí tu archivo")
            
            if arc and st.button("🚀 ENVIAR A LA ASESORÍA"):
                try:
                    ahora = datetime.datetime.now()
                    ref = f"REF-{ahora.strftime('%H%M%S')}"
                    
                    # Buscar carpeta del cliente
                    res = srv.files().list(q=f"name='{nom}' and '{ID_RAIZ}' in parents").execute().get('files', [])
                    if res:
                        id_c = res[0]['id']
                        def get_f(n, p):
                            q = f"name='{n}' and '{p}' in parents and trashed=false"
                            r = srv.files().list(q=q).execute().get('files', [])
                            if r: return r[0]['id']
                            return srv.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        
                        id_dest = get_f(t_v, get_f(tipo_v, get_f(a_v, id_c)))
                        srv.files().create(body={'name': arc.name, 'parents': [id_dest]}, media_body=MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream')).execute()
                        
                        # Registro en archivo de texto (Log)
                        linea = f"{ahora.strftime('%d/%m/%y %H:%M')} | {arc.name} | {ref}\n"
                        q_txt = f"name contains 'REGISTRO' and '{id_c}' in parents"
                        r_txt = srv.files().list(q=q_txt).execute().get('files', [])
                        if r_txt:
                            f_id = r_txt[0]['id']
                            prev = srv.files().get_media(fileId=f_id).execute().decode('utf-8')
                            srv.files().update(fileId=f_id, media_body=MediaIoBaseUpload(io.BytesIO((prev + linea).encode('utf-8')), mimetype='text/plain')).execute()
                        else:
                            srv.files().create(body={'name':f'REGISTRO_ENVIOS_{nom}.txt', 'parents':[id_c]}, media_body=MediaIoBaseUpload(io.BytesIO(linea.encode('utf-8')), mimetype='text/plain')).execute()
                        
                        st.markdown(f'<div class="justificante">✅ <b>RECIBIDO</b><br>Referencia de envío: {ref}</div>', unsafe_allow_html=True)
                        st.balloons()
                except Exception as e: st.error(f"Error al subir: {e}")

        with tab2:
            st.subheader("Consultar Impuestos")
            a_b = st.selectbox("Selecciona el año:", ["2026", "2025"])
            r_c = srv.files().list(q=f"name='{nom}' and '{ID_RAIZ}' in parents").execute().get('files', [])
            if r_c:
                id_cl = r_c[0]['id']
                r_a = srv.files().list(q=f"name='{a_b}' and '{id_cl}' in parents").execute().get('files', [])
                if r_a:
                    fls = srv.files().list(q=f"'{r_a[0]['id']}' in parents").execute().get('files', [])
                    # Búsqueda flexible de la carpeta de impuestos
                    id_imp = next((x['id'] for x in fls if "IMPUESTO" in x['name'].upper()), None)
                    if id_imp:
                        docs = srv.files().list(q=f"'{id_imp}' in parents and trashed=false").execute().get('files', [])
                        if not docs: st.info("Todavía no hay documentos en esta carpeta.")
                        for d in docs:
                            buf = io.BytesIO()
                            downloader = MediaIoBaseDownload(buf, srv.files().get_media(fileId=d['id']))
                            done = False
                            while not done: _, done = downloader.next_chunk()
                            st.download_button(f"📥 Descargar {d['name']}", buf.getvalue(), file_name=d['name'], key=d['id'])
                    else: st.warning("No se ha encontrado la carpeta 'IMPUESTOS PRESENTADOS'.")

        with tab3:
            st.subheader("⚙️ Panel de Control (Admin)")
            if st.text_input("Clave de Administración:", type="password") == PW_ADM:
                c_sel = st.selectbox("Seleccionar Cliente:", list(D_CLI.keys()))
                m_txt = st.text_area("Nuevo Aviso para el cliente:")
                e_est = st.selectbox("Cambiar Estado:", ["Pte de documentación", "En revisión", "Presentado"])
                
                if st.button("ACTUALIZAR PORTAL DEL CLIENTE"):
                    D_AVI[c_sel] = {"texto": m_txt, "estado": e_est}
                    save_j(AV_F, D_AVI)
                    st.success("¡Información actualizada correctamente!")
                
                st.write("---")
                st.write("### Lista de Usuarios")
                for em, n in list(D_CLI.items()):
                    col_i, col_d = st.columns([4,1])
                    col_i.write(f"👤 {n} ({em})")
                    if col_d.button("Borrar", key=em):
                        del D_CLI[em]
                        save_j(DB_F, D_CLI)
                        st.rerun()
                
                st.write("### Registrar Nuevo Cliente")
                n_em = st.text_input("Nuevo Email:")
                n_no = st.text_input("Nombre exacto en Drive:")
                if st.button("DAR DE ALTA"):
                    if n_em
