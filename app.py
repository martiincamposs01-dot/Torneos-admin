import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gestión de Torneos", page_icon="🏆", layout="wide")
st.title("🏆 Plataforma Central de Torneos")

# 1. CONEXIÓN A GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_config = conn.read(worksheet="Configuracion").dropna(how="all")
    df_equipos = conn.read(worksheet="Equipos").dropna(how="all")
    st.success("✅ Base de datos conectada correctamente y lista para operar.")
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# 2. MENÚ LATERAL
menu = st.sidebar.selectbox(
    "Navegación del Sistema", 
    ["🏠 Lobby Público", "⚙️ Panel Staff (Admin)", "📝 Portal Profesores"]
)

# 3. LÓGICA DE LAS PANTALLAS
if menu == "🏠 Lobby Público":
    st.subheader("Bienvenido al Portal de Resultados")
    
    if not df_config.empty:
        copas_disponibles = df_config['Nombre_Copa'].dropna().unique()
        copa_seleccionada = st.selectbox("Selecciona el Torneo:", copas_disponibles)
        st.divider()
        st.markdown(f"### 📍 Estás viendo: {copa_seleccionada}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Categorías en juego:**")
            categorias_copa = df_config[df_config['Nombre_Copa'] == copa_seleccionada]
            st.dataframe(categorias_copa[['Categoria', 'Formato']], hide_index=True, use_container_width=True)
            
        with col2:
            st.write("**Equipos Inscritos:**")
            if not df_equipos.empty:
                equipos_copa = df_equipos[df_equipos['Copa'] == copa_seleccionada]
                st.dataframe(equipos_copa[['Categoria', 'Grupo', 'Nombre_Equipo']], hide_index=True, use_container_width=True)
            else:
                st.info("Aún no hay equipos inscritos en esta copa.")
    else:
        st.info("Aún no hay torneos configurados en la base de datos.")

elif menu == "⚙️ Panel Staff (Admin)":
    st.subheader("Consola de Control del Torneo")
    
    tab1, tab2 = st.tabs(["🏆 Crear Copa/Categoría", "⚽ Inscribir Equipo (Fixture)"])
    
    with tab1:
        st.write("Agrega las categorías que se jugarán en tus torneos.")
        with st.form("form_nueva_copa"):
            nueva_copa = st.text_input("Nombre de la Copa (ej: Copa Máfil 2026)")
            nueva_categoria = st.selectbox("Categoría", ["Sub-8", "Sub-10", "Sub-12", "Sub-14"])
            nuevo_formato = st.selectbox("Formato", ["Grupos", "Liga"])
            submit_copa = st.form_submit_button("Crear y Guardar")
            
            if submit_copa and nueva_copa:
                nuevo_registro = pd.DataFrame([{
                    "Nombre_Copa": nueva_copa,
                    "Categoria": nueva_categoria,
                    "Formato": nuevo_formato
                }])
                df_actual = df_config.copy()
                df_actual = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                
                # Guardar en Google Sheets
                conn.update(worksheet="Configuracion", data=df_actual)
                st.success(f"¡La {nueva_copa} categoría {nueva_categoria} ha sido creada!")
                st.rerun()
                
    with tab2:
        st.info("Aquí agregaremos el formulario para asignar equipos a sus grupos en el próximo paso.")

elif menu == "📝 Portal Profesores":
    st.subheader("Inscripción Digital de Planteles")
    st.info("Próximamente: Formulario para que los DTs ingresen a sus jugadores.")
