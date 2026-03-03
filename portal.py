import streamlit as st
import os, pickle, json, io, datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="ASESORIACLARA", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .header-box { background-color: #223a8e; padding: 1.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .header-box h1 { color: white !important; margin: 0; letter-spacing: 2px; font-size: 2.5rem; font-weight: bold; }
    .user-info { background-color: #e8f0fe; padding: 10px; border-radius: 10px; color: #1e3a8a; font-weight: bold; text-align: center; }
    .estado-box { background-color: #fff9c4; padding: 10px; border-radius: 10px; color: #827717; font-weight: bold; margin: 10px 0; text-align: center; border: 1px solid #fbc02d; }
    .aviso-rojo { padding: 15px; border-radius: 10px; background-color: #ffebee; border-left: 6px solid #f44336; color: #b71c1c; margin: 10px 0; }
    .aviso-azul { padding: 15px; border-radius: 10px; background-color: #e3f2fd; border-left: 6px solid #2196f3; color: #0d47a1; margin: 10px 0; }
    .aviso-tarea { padding: 15px; border-radius: 10px; background-color: #fff3e0; border-left: 6px solid #ff9800; color: #e65100; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE BASE DE DATOS PARA AVISOS ---
# (Simulamos una pequeña base de datos para los avisos y estados)
if 'db_avisos' not in st.session_state:
    st.session_state.db_avisos = {} # Formato: {email: {'texto': '', 'tipo': '', 'estado': ''}}

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    st.markdown('<div class="header-box"><h1>ASESORIACLARA</h1></div>', unsafe_allow_html=True)
    password_input = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR AL PORTAL"):
        if password_input == "clara2026":
            st.session_state["password_correct"] = True
            st.rerun()
    return False

if check_password():
    ID_CARPETA_CLIENTES = "1-9CVv8RoKG4MSalJQtPYKNozleWgLKlH" 
    PASSWORD_ADMIN = "GEST_LA_2025"
    DB_FILE = "clientes_db.json"

    def cargar_clientes():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        return {"asesoriaclara0@gmail.com": "LORENA ALONSO"}

    DICCIONARIO_CLIENTES = cargar_clientes()

    if "user_email" not in st.session_state:
        em_log = st.text_input("Correo electrónico para acceder:")
        if st.button("ACCEDER"):
            if em_log.lower().strip() in DICCIONARIO_CLIENTES:
                st.session_state["user_email"] = em_log.lower().strip()
                st.rerun()
    else:
        email_act = st.session_state["user_email"]
        nombre_act = DICCIONARIO_CLIENTES[email_act]

        # 1. CABECERA Y ESTADO
        st.markdown(f'<div class="user-info">Sesión: {nombre_act}</div>', unsafe_allow_html=True)
        
        # Recuperar estado y aviso del cliente
        datos_cliente = st.session_state.db_avisos.get(email_act, {'texto': 'Bienvenido al portal.', 'tipo': 'azul', 'estado': 'Pendiente documentación'})
        
        st.markdown(f'<div class="estado-box">📊 ESTADO 1T 2026: {datos_cliente["estado"]}</div>', unsafe_allow_html=True)

        # 2. MOSTRAR AVISO SEGÚN TIPO
        clase_aviso = "aviso-rojo" if datos_cliente['tipo'] == 'rojo' else "aviso-azul" if datos_cliente['tipo'] == 'azul' else "aviso-tarea"
        titulo_aviso = "⚠️ URGENTE" if datos_cliente['tipo'] == 'rojo' else "📢 INFORMATIVO" if datos_cliente['tipo'] == 'azul' else f"📝 TAREA PENDIENTE - {nombre_act.split()[0]}"
        
        st.markdown(f'<div class="{clase_aviso}"><strong>{titulo_aviso}:</strong> {datos_cliente["texto"]}</div>', unsafe_allow_html=True)
        if st.button("✔️ MARCAR COMO LEÍDO"):
            st.balloons()
            with open(f"REGISTRO_LECTURA_{nombre_act}.txt", "a") as f:
                f.write(f"{datetime.datetime.now()}: Leído aviso '{datos_cliente['texto']}'\n")

        tab1, tab2, tab3 = st.tabs(["📤 ENVIAR", "📥 IMPUESTOS", "⚙️ GESTIÓN"])

        with tab3:
            st.subheader("⚙️ Panel de Control Lorena")
            ad_pass = st.text_input("Clave Maestra:", type="password")
            if ad_pass == PASSWORD_ADMIN:
                st.write("---")
                st.write("### 📝 Gestionar Avisos y Estados")
                cli_sel = st.selectbox("Seleccionar Cliente:", list(DICCIONARIO_CLIENTES.keys()))
                nuevo_texto = st.text_area("Mensaje del Aviso:")
                nuevo_tipo = st.selectbox("Tipo de Aviso:", ["rojo", "azul", "tarea"])
                nuevo_estado = st.radio("Estado del Trimestre:", ["⚪ Pendiente documentación", "🟡 En revisión", "🟢 Presentado"])
                
                if st.button("PUBLICAR ACTUALIZACIÓN"):
                    st.session_state.db_avisos[cli_sel] = {
                        'texto': nuevo_texto,
                        'tipo': nuevo_tipo,
                        'estado': nuevo_estado
                    }
                    st.success(f"Actualizado el portal de {cli_sel}")
