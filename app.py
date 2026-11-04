import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="Gestión de Torneos", page_icon="🏆", layout="wide")

# Título Principal
st.title("🏆 Plataforma Central de Torneos")

# 1. CONEXIÓN A GOOGLE SHEETS
try:
    # Conectamos con el robot que configuramos en los secretos
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos las pestañas principales (borramos filas vacías por si acaso)
    df_config = conn.read(worksheet="Configuracion").dropna(how="all")
    df_equipos = conn.read(worksheet="Equipos").dropna(how="all")
    
    st.success("✅ Base de datos conectada correctamente y lista para operar.")
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# 2. MENÚ DE NAVEGACIÓN LATERAL
menu = st.sidebar.selectbox(
    "Navegación del Sistema", 
    ["🏠 Lobby Público", "📝 Portal Profesores", "⚙️ Panel Staff (Admin)"]
)

# 3. LÓGICA DE LAS PANTALLAS
if menu == "🏠 Lobby Público":
    st.subheader("Bienvenido al Portal de Resultados")
    
    # Selector de Copas Dinámico
    if not df_config.empty:
        # Extraemos los nombres únicos de las copas desde el Excel
        copas_disponibles = df_config['Nombre_Copa'].dropna().unique()
        
        # Dibujamos el selector
        copa_seleccionada = st.selectbox("Selecciona el Torneo:", copas_disponibles)
        
        st.divider()
        st.markdown(f"### 📍 Estás viendo: {copa_seleccionada}")
        
        # Dividimos la pantalla en dos columnas para que se vea ordenado
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Categorías y Formatos en juego:**")
            categorias_copa = df_config[df_config['Nombre_Copa'] == copa_seleccionada]
            st.dataframe(categorias_copa[['Categoria', 'Formato']], hide_index=True, use_container_width=True)
            
        with col2:
            st.write("**Equipos Inscritos Oficialmente:**")
            equipos_copa = df_equipos[df_equipos['Copa'] == copa_seleccionada]
            st.dataframe(equipos_copa[['Categoria', 'Grupo', 'Nombre_Equipo']], hide_index=True, use_container_width=True)
            
    else:
        st.info("Aún no hay torneos configurados en la base de datos.")

elif menu == "📝 Portal Profesores":
    st.subheader("Inscripción Digital de Planteles")
    st.info("Próximamente: Aquí habilitaremos el formulario digital para que los DTs suban sus nóminas sin usar papel.")

elif menu == "⚙️ Panel Staff (Admin)":
    st.subheader("Consola de Control del Torneo")
    st.info("Próximamente: Panel exclusivo del staff para crear copas, registrar marcadores y asignar los goles a los niños.")
