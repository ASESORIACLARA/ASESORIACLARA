import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- CONFIGURACIÓN ---
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
    ID_RAIZ = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PW_ADM = "GEST_LA_2025"
    DB_F, AV_F = "clientes_db.json", "avisos_db.json"

    def load_j(f, d):
        if os.path.exists(f):
            try:
                with open(f, "r", encoding="utf-8") as f1: return json.load(f1)
            except: return d
        return d
    def save_j(f, d):
        with open(f, "w", encoding="utf-8") as f1: json.dump(d, f1, indent=4, ensure_ascii=False)

    D_CLI = load_j(DB_F, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    D_AVI = load_j(AV_F, {})

    if "u_mail" not in st.session_state:
        st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1></div>', unsafe_allow_html=True)
        em = st.text_input("Correo registrado:")
        if st.button("ACCEDER") and em.lower().strip() in D_CLI:
            st.session_state["u_mail"] = em.lower().strip()
            st.rerun()
    else:
        mail, nom = st.session_state["u_mail"], D_CLI[st.session_state["u_mail"]]
        inf = D_AVI.get(mail, {})
        txt_av, tip_av, est_tri = inf.get("texto", "Bienvenido."), inf.get("tipo", "informativo"), inf.get("estado", "Pendiente documentación")

        clase_est = "estado-rojo"
        if est_tri == "En revisión": clase_est = "estado-amarillo"
        elif est_tri == "Presentado": clase_est = "estado-verde"

        st.markdown(f'<div class="user-info">Sesión: {nom}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{clase_est}">📊 ESTADO 1T 2026: {est_tri.upper()}</div>', unsafe_allow_html=True)
        
        col_av = "#2196f3" if tip_av == "informativo" else "#f44336" if tip_av == "urgente" else "#ff9800"
        st.markdown(f'<div class="aviso-caja" style="border-color:{col_av}; background-color:{col_av}15;">📢 <b>AVISO:</b> {txt_av}</div>', unsafe_allow_html=True)

        if st.button("🔒 SALIR"):
            del st.session_state["u_mail"]; st.rerun()

        t1, t2, t3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])
        with open('token.pickle', 'rb') as tk: srv = build('drive', 'v3', credentials=pickle.load(tk))

        with t1:
            st.subheader("Subir documentación")
            c1, c2 = st.columns(2)
            a_v, t_v = c1.selectbox("Año", ["2026", "2025"]), c2.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tipo_v = st.radio("Tipo", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"], horizontal=True)
            arc = st.file_uploader("Archivo")
            if arc and st.button("🚀 ENVIAR"):
                try:
                    ahora = datetime.datetime.now()
                    ref = f"REF-{ahora.strftime('%H%M%S')}"
                    n_f = f"{ahora.strftime('%Y-%m-%d')}_{tipo_v.split()[1]}_{ref}{os.path.splitext(arc.name)[1]}"
                    res = srv.files().list(q=f"name='{nom}' and '{ID_RAIZ}' in parents").execute().get('files', [])
                    if res:
                        id_c = res[0]['id']
                        def get_f(n, p):
                            q = f"name='{n}' and '{p}' in parents and trashed=false"
                            r = srv.files().list(q=q).execute().get('files', [])
                            if r: return r[0]['id']
                            return srv.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                        id_dest = get_f(t_v, get_f(tipo_v, get_f(a_v, id_c)))
                        srv.files().create(body={'name':n_f, 'parents':[id_dest]}, media_body=MediaIoBaseUpload(io.BytesIO(arc.getbuffer()), mimetype='application/octet-stream')).execute()
                        st.markdown(f'<div class="justificante">✅ <b>ENVIADO</b> (Ref: {ref})</div>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")

        with t2:
            st.subheader("Impuestos")
            a_b = st.selectbox("Año:", ["2026", "2025"])
            r_c = srv.files().list(q=f"name='{nom}' and '{ID_RAIZ}' in parents").execute().get('files', [])
            if r_c:
                id_cl = r_c[0]['id']
                r_a = srv.files().list(q=f"name='{a_b}' and '{id_cl}' in parents").execute
