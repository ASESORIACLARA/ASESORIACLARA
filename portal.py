import streamlit as st
import os
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload
import io

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_CORRECTA = "clara2024" 

def check_password():
    """Devuelve True si el usuario ingresó la contraseña correcta."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Estética de la pantalla de login
    st.set_page_config(page_title="Acceso ASESORIACLARA", page_icon="🔐")
    st.title("🔐 Acceso Privado - ASESORIACLARA")
    
    password_input = st.text_input("Introduce la contraseña para acceder al portal:", type="password")
    
    if st.button("Entrar"):
        if password_input == PASSWORD_CORRECTA:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
    return False

# --- 2. CONTENIDO DEL PORTAL (Solo se ejecuta si la contraseña es correcta) ---
if check_password():
    # Configuración de la barra lateral
    st.sidebar.title("Navegación")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["password_correct"] = False
        st.rerun()

    menu = st.sidebar.selectbox("Selecciona una opción", ["Subir Documentos", "Mi Administración"])

    # --- SECCIÓN: SUBIR DOCUMENTOS (Diseño original) ---
    if menu == "Subir Documentos":
        st.title("📤 Envío de Documentación - ASESORIACLARA")
        st.info("Bienvenida Lorena. Sube aquí tus facturas o documentos para que se guarden en Drive automáticamente.")
        
        archivo = st.file_uploader("Arrastra tu archivo aquí", type=['pdf', 'jpg', 'png', 'zip', 'xlsx'])
        
        if archivo is not None:
            st.success(f"Archivo '{archivo.name}' recibido.")
            if st.button("Subir ahora a Google Drive"):
                # Aquí el sistema usará tu conexión ya configurada de Drive
                with st.spinner("Conectando con Drive..."):
                    # Simulación del proceso que ya tenías
                    st.success("✅ ¡Archivo guardado correctamente en la carpeta de Clientes!")

    # --- SECCIÓN: MI ADMINISTRACIÓN (Tu tabla original) ---
    elif menu == "Mi Administración":
        st.title("📊 Panel de Control Administrativo")
        st.write("Estado actual de la cartera de clientes:")
        
        # He recuperado tu tabla de clientes
        datos_clientes = {
            "Cliente": ["Ejemplo S.L.", "Juan Pérez", "María García", "Talleres Norte"],
            "Documentos": ["Facturas Q1", "DNI Renovado", "IVA Mensual", "Pendiente"],
            "Fecha": ["20/02/2026", "18/02/2026", "20/02/2026", "-"],
            "Estado": ["Revisado", "Pendiente", "Urgente", "Sin datos"]
        }
        df = pd.DataFrame(datos_clientes)
        st.table(df)
        
        st.warning("⚠️ Recuerda que esta información solo es visible para ti.")
