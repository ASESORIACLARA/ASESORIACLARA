import streamlit as st
import os, pickle, json, io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

st.set_page_config(page_title="ASESORIACLARA", layout="centered")

def check_password():
    if "pw" not in st.session_state: st.session_state["pw"] = False
    if st.session_state["pw"]: return True
    st.title("ASESORIACLARA")
    if st.text_input("Contraseña:", type="password") == "clara2026":
        st.session_state["pw"] = True
        st.rerun()
    return False

if check_password():
    ID_CLI = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    AD_PW = "GEST_LA_2025"
    DB_F = "clientes_db.json"

    def load_db():
        if os.path.exists(DB_F):
            with open(DB_F, "r") as f: return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    def save_db(data):
        with open(DB_F, "w") as f: json.dump(data, f)

    DB = load_db()
    
    st.markdown('<div style="background:#223a8e;padding:2rem;border-radius:15px;text-align:center;color:white;"><h1>ASESORIACLARA</h1></div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

    with open('token.pickle', 'rb') as t:
        service = build('drive', 'v3', credentials=pickle.load(t))

    with t3:
        if st.text_input("Admin PW:", type="password") == AD_PW:
            st.subheader("Nuevo Cliente")
            ne, nn = st.text_input("Email:"), st.text_input("Carpeta:")
            if st.button("Añadir"):
                DB[ne.lower().strip()] = nn
                save_db(DB)
                st.rerun()
            st.subheader("Bajas")
            for e, n in list(DB.items()):
                if st.button(f"Eliminar {n}", key=e):
                    del DB[e]
                    save_db(DB)
                    st.rerun()

    if "user" not in st.session_state:
        with t1:
            u = st.text_input("Tu Correo:").lower().strip()
            if st.button("Entrar"):
                if u in DB: 
                    st.session_state["user"] = u
                    st.rerun()
                else: st.error("No registrado")
    else:
        nom = DB[st.session_state["user"]]
        with t1:
            st.write(f"Hola, **{nom}**")
            a, tr = st.selectbox("Año", ["2026", "2025"]), st.selectbox("Trimestre", ["1T", "2T", "3T", "4T"])
            tp = st.radio("Tipo", ["FACTURAS EMITIDAS", "FACTURAS GASTOS"])
            f = st.file_uploader("Archivo")
            if f and st.button("Enviar"):
                q = f"name='{nom}' and '{ID_CLI}' in parents and trashed=false"
                r = service.files().list(q=q).execute().get('files', [])
                if r:
                    pid = r[0]['id']
                    def get_id(n, p):
                        qf = f"name='{n}' and '{p}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                        rf = service.files().list(q=qf).execute().get('files', [])
                        if rf: return rf[0]['id']
                        return service.files().create(body={'name':n,'mimeType':'application/vnd.google-apps.folder','parents':[p]}, fields='id').execute()['id']
                    final_id = get_id(tr, get_id(tp, get_id(a, pid)))
                    with open(f.name, "wb") as tmp: tmp.write(f.getbuffer())
                    service.files().create(body={'name':f.name, 'parents':[final_id]}, media_body=MediaFileUpload(f.name)).execute()
                    os.remove(f.name)
                    st.success("¡Enviado!")

        with t2:
            st.subheader("Mis Impuestos")
            any_b = st.selectbox("Año:", ["2026", "2025"], key="any_b")
            q = f"name='{nom}' and '{ID_CLI}' in parents and trashed=false"
            r = service.files().list(q=q).execute().get('files', [])
            if r:
                qa = f"name='{any_b}' and '{r[0]['id']}' in parents"
                ra = service.files().list(q=qa).execute().get('files', [])
                if ra:
                    qi = f"name='IMPUESTOS PRESENTADOS' and '{ra[0]['id']}' in parents"
                    ri = service.files().list(q=qi).execute().get('files', [])
                    if ri:
                        for d in service.files().list(q=f"'{ri[0]['id']}' in parents").execute().get('files', []):
                            c1, c2 = st.columns([3,1])
                            c1.write(d['name'])
                            res = service.files().get_media(fileId=d['id'])
                            fh = io.BytesIO()
                            downloader = MediaIoBaseDownload(fh, res)
                            done = False
                            while not done: _, done = downloader.next_chunk()
                            c2.download_button("Bajar", fh.getvalue(), file_


