import streamlit as st
import os

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_CORRECTA = "clara2024" 

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.set_page_config(page_title="Acceso ASESORIACLARA", page_icon="🔐")
    st.title("🔐 Acceso Privado - ASESORIACLARA")
    
    password_input = st.text_input("Introduce la contraseña para acceder:", type="password")
    
    if st.button("Entrar"):
        if password_input == PASSWORD_CORRECTA:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
    return False

# --- 2. CONTENIDO DEL PORTAL ---
if check_password():
    st.sidebar.title("Menú Principal")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["password_correct"] = False
        st.rerun()

    menu = st.sidebar.selectbox("Ir a:", ["Subir Documentos", "Panel de Administración"])

    if menu == "Subir Documentos":
        st.title("📤 Envío de Documentación")
        st.write("Bienvenida, **Lorena**. Selecciona los archivos para tu gestión.")
        uploaded_file = st.file_uploader("Arrastra aquí tus archivos (PDF, JPG, PNG)", accept_multiple_files=False)
        if uploaded_file is not None:
            st.success(f"Archivo '{uploaded_file.name}' listo para enviar.")

    elif menu == "Panel de Administración":
        st.title("📊 Control de Administración")
        st.subheader("Clientes Activos")
        st.table({
            "Cliente": ["Ejemplo S.L.", "Juan Pérez", "María García"],
            "Estado": ["Pendiente Factura", "Al día", "Revisión IVA"]
        })
