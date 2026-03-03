import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")
st.markdown("""<style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; color: white; }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .estado-box { background-color: #fff9c4; padding: 10px; border-radius: 10px; color: #827717; font-weight: bold; text-align: center; margin-bottom: 15px; border: 1px solid #fbc02d; }
    .aviso-rojo { padding: 15px; border-radius: 10px; background-color: #ffebee; border-left: 6px solid #f44336; color: #b71c1c; margin: 10px 0; }
    .aviso-azul { padding: 15px; border-radius: 10px; background-color: #e3f2fd; border-left: 6px solid #2196f3; color: #0d47a1; margin: 10px 0; }
    .aviso-tarea { padding: 15px; border-radius: 10px; background-color: #fff3e0; border-left: 6px solid #ff9800; color: #e65100; margin: 10px 0; }
    .justificante { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 10px; border: 1px solid #166534; margin: 10px 0; }
    [data-testid="stSidebar"] { display: none; }
</style>""", unsafe_allow_html=True)

def check_password():
    if "pw_ok" not in st.session_state: st.session_state["pw_ok"] = False
    if st.session_state["pw_ok"]: return True
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1></div>', unsafe_allow_html=True)
    pw = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR") and pw == "clara2026":
        st.session_state["pw_ok"] = True
        st.rerun()
    return False

if check_password():
    ID_CARPETA = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PW_ADMIN = "GEST_LA_2025"
    DB_F, AV_F = "clientes_db.json", "avisos_db.json"

    def load_j(f, d):
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8") as f1: return json.load(f1)
        return d
    def save_j(f, d):
        with open(f, "w", encoding="utf-8") as f1: json.dump(d, f1, indent=4, ensure_ascii=False)

    D_CLI = load_j(DB_F, {"asesoriaclara0@gmail.com": "LORENA ALONSO"})
    D_AVI = load_j(AV_F, {})

    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1><p>Tu portal de confianza</p></div>', unsafe_allow_html=True)

    if "u_mail" not in st.session_state:
        em = st.text_input("Correo:")
        if st.button("ACCEDER") and em.lower().strip() in D_CLI:
            st.session_state["u_mail"] = em.lower().strip()
            st.rerun()
    else:
        mail = st.session_state["u_mail"]
        nom = D_CLI[mail]
        st.markdown(f'<div class="user-info">Sesión: {nom}</div>', unsafe_allow_html=True)
        if st.button("🔒 SALIR"):
            del st.session_state["u_mail"]
            st.rerun()

        inf = D_AVI.get(mail, {"texto": "Bienvenido.", "tipo": "azul", "estado": "Pendiente"})
        st.markdown(f'<div class="estado-box">📊 ESTADO 1T 2026: {inf["estado"]}</div>', unsafe_allow_html=True)
        cl = "aviso-rojo" if inf["tipo"]=="urgente" else "aviso-azul" if inf["tipo"]=="informativo" else "aviso-tarea"
        st.markdown(f'<div class="{cl}"><strong>AVISO:</strong> {inf["texto"]}</div>', unsafe_allow_html=True)

        t1, t2, t3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])
        with open('token.pickle', 'rb') as tk: creds = pickle.load(tk)
        srv = build('drive', 'v3', credentials=creds)

        with t1:
            a, t, tp = st.selectbox("Año", ["2026","2025"]), st.selectbox("Tri", ["1T","2T","3T","4T"]), st.radio("Tipo", ["EMITIDAS", "GASTOS"])
            f = st.file_uploader("Archivo")
            if f and st.button("🚀 ENVIAR"):
                ahora = datetime.datetime.now()
                ref = f"REF-{ahora.strftime('%H%M%S')}"
                n_f = f"{ahora.strftime('%Y%m%d')}_{tp}_{ref}{os.path.splitext(f.name)[1]}"
                res = srv.files().list(q=f"name='{nom}' and '{ID_CARPETA}' in parents").execute().get('files', [])
                if res:
                    id_c = res[0]['id']
                    def get_id(n, p):
                        q = f"name='{n}' and '{p}' in parents and trashed=false"
                        r = srv.files().list(q=q).execute().get('files', [])
                        if r: return r[0]['id']
                        return srv.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                    dest = get_id(t, get_id(tp, get_id(a, id_c)))
                    srv.files().create(body={'name': n_f, 'parents': [dest]}, media_body=MediaIoBaseUpload(io.BytesIO(f.getbuffer()), mimetype='application/octet-stream')).execute()
                    st.success(f"Recibido: {ref}")

        with t2:
            a_b = st.selectbox("Año consulta", ["2026", "2025"])
            r_c = srv.files().list(q=f"name='{nom}' and '{ID_CARPETA}' in parents").execute().get('files', [])
            if r_c:
                id_cl = r_c[0]['id']
                r_a = srv.files().list(q=f"name='{a_b}' and '{id_cl}' in parents").execute().get('files', [])
                if r_a:
                    fls = srv.files().list(q=f"'{r_a[0]['id']}' in parents").execute().get('files', [])
                    id_imp = next((x['id'] for x in fls if "IMPUESTOS" in x['name'].upper()), None)
                    if id_imp:
                        docs = srv.files().list(q=f"'{id_imp}' in parents").execute().get('files', [])
                        for d in docs:
                            buf = io.BytesIO()
                            dl = MediaIoBaseDownload(buf, srv.files().get_media(fileId=d['id']))
                            done = False
                            while not done: _, done = dl.next_chunk()
                            st.download_button(f"📥 {d['name']}", buf.getvalue(), file_name=d['name'], key=d['id'])

        with t3:
            if st.text_input("Admin Key", type="password") == PW_ADMIN:
                st.write("### Avisos")
                c_s = st.selectbox("Cliente", list(D_CLI.keys()))
                m = st.text_area("Mensaje")
                tip = st.selectbox("Tipo", ["informativo", "tarea", "urgente"])
                est = st.selectbox("Estado", ["Pendiente", "En revisión", "Presentado"])
                if st.button("ACTUALIZAR"):
                    D_AVI[c_s] = {"texto": m, "tipo": tip, "estado": est}
                    save_j(AV_F, D_AVI); st.success("OK")
                st.write("---")
                for e, n in list(D_CLI.items()):
                    c_i, c_d = st.columns([3, 1])
                    c_i.write(f"{n} ({e})")
                    if c_d.button("X", key=e):
                        del D_CLI[e]; save_j(DB_F, D_CLI); st.rerun()
                st.write("### Nuevo")
                ne, nn = st.text_input("Email"), st.text_input("Nombre")
                if st.button("AÑADIR") and ne and nn:
                    D_CLI[ne.lower()] = nn; save_j(DB_F, D_CLI); st.rerun()

