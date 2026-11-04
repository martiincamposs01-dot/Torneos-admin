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
                if not equipos_copa.empty:
                    st.dataframe(equipos_copa[['Categoria', 'Grupo', 'Nombre_Equipo']], hide_index=True, use_container_width=True)
                else:
                    st.info("Aún no hay equipos inscritos en esta copa.")
            else:
                st.info("Aún no hay equipos inscritos.")
    else:
        st.info("Aún no hay torneos configurados en la base de datos.")

elif menu == "⚙️ Panel Staff (Admin)":
    st.subheader("Consola de Control del Torneo")
    
    tab1, tab2 = st.tabs(["🏆 Crear Copa/Categoría", "⚽ Inscribir Equipo"])
    
    with tab1:
        st.write("Agrega las categorías (años de nacimiento) que se jugarán.")
        with st.form("form_nueva_copa"):
            nueva_copa = st.text_input("Nombre del Torneo (ej: Mafil Cup 2025)")
            nueva_categoria = st.text_input("Categoría (ej: 2011-2012 o 2017/2018)")
            nuevo_formato = st.selectbox("Formato", ["Grupos", "Liga"])
            submit_copa = st.form_submit_button("Crear y Guardar")
            
            if submit_copa and nueva_copa and nueva_categoria:
                nuevo_registro = pd.DataFrame([{
                    "Nombre_Copa": nueva_copa.strip(),
                    "Categoria": nueva_categoria.strip(),
                    "Formato": nuevo_formato
                }])
                df_actual = df_config.copy()
                df_actual = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                conn.update(worksheet="Configuracion", data=df_actual)
                st.success(f"¡Categoría {nueva_categoria} creada en {nueva_copa}!")
                st.rerun()
                
    with tab2:
        st.write("Inscribe a los clubes y asígnalos a sus grupos.")
        if not df_config.empty:
            # Los selectores van fuera del form para que se actualicen en tiempo real
            lista_copas = df_config['Nombre_Copa'].dropna().unique()
            copa_eq = st.selectbox("Seleccionar Torneo:", lista_copas)
            
            categorias_disponibles = df_config[df_config['Nombre_Copa'] == copa_eq]['Categoria'].unique()
            categoria_eq = st.selectbox("Seleccionar Categoría:", categorias_disponibles)
            
            with st.form("form_nuevo_equipo"):
                nombre_equipo = st.text_input("Nombre del Club / Academia (ej: Río Iñaque)")
                grupo_eq = st.text_input("Grupo (ej: A, B, C... o dejar en blanco si es Liga)")
                submit_equipo = st.form_submit_button("Inscribir Equipo")
                
                if submit_equipo and nombre_equipo:
                    nuevo_eq = pd.DataFrame([{
                        "Copa": copa_eq,
                        "Categoria": categoria_eq,
                        "Grupo": grupo_eq.strip().upper(),
                        "Nombre_Equipo": nombre_equipo.strip()
                    }])
                    df_eq_actual = df_equipos.copy()
                    df_eq_actual = pd.concat([df_eq_actual, nuevo_eq], ignore_index=True)
                    conn.update(worksheet="Equipos", data=df_eq_actual)
                    st.success(f"¡{nombre_equipo} inscrito correctamente!")
                    st.rerun()
        else:
            st.info("Primero debes crear un torneo en la pestaña 'Crear Copa/Categoría'.")

elif menu == "📝 Portal Profesores":
    st.subheader("Inscripción Digital de Planteles")
    st.info("Próximamente: Formulario para que los DTs ingresen a sus jugadores.")
