import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN DE COLORES Y ESTILOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; color: white; }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .estado-rojo { background-color: #ffebee; color: #b71c1c; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #f44336; }
    .estado-amarillo { background-color: #fff9c4; color: #827717; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #fbc02d; }
    .estado-verde { background-color: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #4caf50; }
    .aviso-caja { padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 6px solid; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

def check_password():
    if "pw_ok" not in st.session_state: st.session_state["pw_ok"] = False
    if st.session_state["pw_ok"]: return True
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Acceso Privado</p></div>', unsafe_allow_html=True)
    pw = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR") and pw == "clara2026":
        st.session_state["pw_ok"] = True
        st.rerun()
    return False

if check_password():
    ID_CARPETA_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PW_ADMIN = "GEST_LA_2025"
    DB_F, AV_F = "clientes_db.json", "avisos_db.json"

    def cargar_j(f, d):
        if os.path.exists(f):
            try:
                with open(f, "r", encoding="utf-8") as f1: return json.load(f1)
            except: return d
        return d

    def guardar_j(f, d):
        with open(f, "w", encoding="utf-8") as f1: json.dump(d, f1, indent=4, ensure_ascii=False)

    D_CLI = cargar_j(DB_F, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    D_AVI = cargar_j(AV_F, {})

    if "u_mail" not in st.session_state:
        st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1></div>', unsafe_allow_html=True)
        em = st.text_input("Introduce tu correo para acceder:")
        if st.button("ACCEDER") and em.lower().strip() in D_CLI:
            st.session_state["u_mail"] = em.lower().strip()
            st.rerun()
    else:
        mail = st.session_state["u_mail"]
        nom = D_CLI[mail]
        
        # --- MEJORA: Evitar KeyError si faltan datos ---
        inf = D_AVI.get(mail, {})
        texto_aviso = inf.get("texto", "Bienvenido/a al portal. Por favor, sube tus facturas.")
        tipo_aviso = inf.get("tipo", "informativo")
        estado_tri = inf.get("estado", "Pendiente documentación")

        # Colores de Estado
        clase_estado = "estado-rojo"
        if estado_tri == "En revisión": clase_estado = "estado-amarillo"
        elif estado_tri == "Presentado": clase_estado = "estado-verde"

        st.markdown(f'<div class="user-info">Sesión: {nom}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{clase_estado}">📊 ESTADO 1T 2026: {estado_tri.upper()}</div>', unsafe_allow_html=True)
        
        # Colores de Aviso
        color_aviso = "#2196f3" if tipo_aviso == "informativo" else "#f44336" if tipo_aviso == "urgente" else "#ff9800"
        st.markdown(f'<div class="aviso-caja" style="border-color: {color_aviso}; background-color: {color_aviso}15;">📢 <b>AVISO:</b> {texto_aviso}</div>', unsafe_allow_html=True)

        if st.button("🔒 SALIR"):
            del st.session_state["u_mail"]
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR FACTURAS", "📥 MIS IMPUESTOS", "⚙️ GESTIÓN"])
        
        with open('token.pickle', 'rb') as tk: creds = pickle.load(tk)
        srv = build('drive', 'v3', credentials=creds)

        with tab1:
            st.subheader("Subir documentación")
            c1, c2 = st.columns(2)
            a_v = c1.selectbox("Año", ["2026", "2025"])
            t_v = c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_v = st.radio("Tipo", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Arrastra aquí tu archivo")
            
            if arc and st.button("🚀 ENVIAR AHORA"):
                try:
                    ahora = datetime.datetime.now()
                    ref = f"REF-{ahora.strftime('%H%M%S')}"
                    n_f = f"{ahora.strftime('%Y-%m-%d')}_{tipo_v.split()[1]}_{ref}{os.path.splitext(arc.name)[1]}"
                    res = srv.files().list(q=f"name='{nom}' and '{ID_CARPETA_RAIZ}' in parents").execute().get('files', [])
                    if res:
                        id_c = res[0]['id']
                        def get_f(n, p):
                            q = f"name='{n}' and '{p}' in parents and trashed=false"
                            r = srv.files().list(q=q).execute().get('files', [])
                            if r: return r[0]['id']
                            return srv.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        
                        id_dest = get_f(t_v, get_f(tipo_v, get_f(a_v, id_c)))
                        srv.files().create(body={'name': n_f, 'parents': [id_dest]}, media_body=MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream')).execute()
                        
                        # Registro .txt
                        linea = f"{ahora.strftime('%d/%m/%y %H:%M')} | {n_f} | {ref}\n"
                        q_txt = f"name='REGISTRO_ENVIOS_{nom}.txt' and '{id_c}' in parents"
                        res_txt = srv.files().list(q=q_txt).execute().get('files', [])
                        if res_txt:
                            f_id = res_txt[0]['id']
                            prev = srv.files().get_media(fileId=f_id).execute().decode('utf-8')
                            srv.files().update(fileId=f_id, media_body=MediaIoBaseUpload(io.BytesIO((prev + linea).encode('utf-8')), mimetype='text/plain')).execute()
                        else:
                            srv.files().create(body={'name':f'REGISTRO_ENVIOS_{nom}.txt', 'parents':[id_c]}, media_body=MediaIoBaseUpload(io.BytesIO(linea.encode('utf-8')), mimetype='text/plain')).execute()
                        st.markdown(f'<div class="justificante">✅ <b>ENVIADO</b><br>Referencia: {ref}</div>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")

        with tab2:
            st.subheader("Documentos e Impuestos")
            a_b = st.selectbox("Selecciona el año:", ["2026", "2025"])
            r_c = srv.files().list(q=f"name='{nom}' and '{ID_CARPETA_RAIZ}' in parents").execute().get('files', [])
            if r_c:
                id_cl = r_c[0]['id']
                r_a = srv.files().list(q=f"name='{a_b}' and '{id_cl}' in parents").execute().get('files', [])
                if r_a:
                    fls = srv.files().list(q=f"'{r_a[0]['id']}' in parents").execute().get('files', [])
                    # Busca carpetas que contengan la palabra IMPUESTOS
                    id_imp = next((x['id'] for x in fls if "IMPUESTOS" in x['name'].upper()), None)
                    if id_imp:
                        docs = srv.files().list(q=f"'{id_imp}' in parents and trashed=false").execute().get('files', [])
                        if not docs: st.info("No hay documentos subidos en esta carpeta todavía.")
                        for d in docs:
                            buf = io.BytesIO()
                            downloader = MediaIoBaseDownload(buf, srv.files().get_media(fileId=d['id']))
                            done = False
                            while not done: _, done = downloader.next_chunk()
                            st.download_button(f"📥 Descargar {d['name']}", buf.getvalue(), file_name=d['name'], key=d['id'])
                    else: st.warning("Crea una carpeta llamada 'IMPUESTOS PRESENTADOS' en Drive para este año.")

        with tab3:
            if st.text_input("Acceso Admin:", type="password") == PW_ADMIN:
                st.write("### Panel de Control")
                c_s = st.selectbox("Cliente:", list(D_CLI.keys()))
                m_txt = st.text_area("Mensaje de Aviso:")
                t_av = st.selectbox("Gravedad:", ["informativo", "tarea", "urgente"])
                e_est = st.selectbox("Estado
