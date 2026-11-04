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
    # Intentamos leer la pestaña de jugadores, si no existe o está vacía, la iniciamos vacía
    try:
        df_jugadores = conn.read(worksheet="Jugadores").dropna(how="all")
    except:
        df_jugadores = pd.DataFrame(columns=["Copa", "Categoria", "Equipo", "Nombre_Jugador", "Dorsal", "Goles"])
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# 2. MENÚ LATERAL PRINCIPAL
menu = st.sidebar.selectbox(
    "Navegación del Sistema", 
    ["🏠 Lobby Público", "⚙️ Panel Staff (Admin)", "📝 Portal Profesores"]
)

# 3. LÓGICA DE LAS PANTALLAS
if menu == "🏠 Lobby Público":
    st.subheader("Bienvenido al Portal de Resultados")
    
    if not df_config.empty:
        sedes_disponibles = ['Angol', 'Máfil', 'Valdivia']
        sede_seleccionada = st.selectbox("📍 Selecciona la Sede / Ciudad:", sedes_disponibles)
        
        st.divider()
        st.markdown(f"### 🏟️ Torneos activos en: {sede_seleccionada}")
        
        copas_sede = df_config[df_config['Nombre_Copa'].str.contains(sede_seleccionada, case=False, na=False)]
        
        if not copas_sede.empty:
            copa_seleccionada = st.selectbox("Selecciona el Torneo específico:", copas_sede['Nombre_Copa'].unique())
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Categorías en juego (Años):**")
                categorias_copa = df_config[df_config['Nombre_Copa'] == copa_seleccionada]
                st.dataframe(categorias_copa[['Categoria', 'Formato']], hide_index=True, use_container_width=True)
                
            with col2:
                st.write("**Equipos Inscritos:**")
                if not df_equipos.empty:
                    equipos_copa = df_equipos[df_equipos['Copa'] == copa_seleccionada]
                    if not equipos_copa.empty:
                        st.dataframe(equipos_copa[['Categoria', 'Grupo', 'Nombre_Equipo']], hide_index=True, use_container_width=True)
                    else:
                        st.info("Aún no hay equipos inscritos en este torneo.")
                else:
                    st.info("Aún no hay equipos inscritos.")
        else:
            st.info(f"Aún no hay torneos configurados para {sede_seleccionada}.")
    else:
        st.info("Aún no hay torneos configurados en la base de datos.")

elif menu == "⚙️ Panel Staff (Admin)":
    st.subheader("Consola de Control del Torneo")
    
    tab1, tab2 = st.tabs(["🏆 Crear Múltiples Categorías", "⚽ Inscribir Equipo"])
    
    with tab1:
        st.write("Selecciona la sede, el torneo y marca **todas las categorías** que jugarán en simultáneo.")
        
        with st.form("form_categorias_multiples"):
            sede_input = st.selectbox("Sede / Ciudad Principal", ["Angol", "Máfil", "Valdivia"])
            nombre_personalizado = st.text_input("Nombre del Torneo / Copa (ej: Mafil Cup 2025, Copa Invierno)")
            
            nombre_copa_final = f"{sede_input} - {nombre_personalizado}" if nombre_personalizado else sede_input
            
            st.write("**Selecciona las categorías que participan:**")
            cat_1 = st.checkbox("2019 / 2018")
            cat_2 = st.checkbox("2017 / 2016")
            cat_3 = st.checkbox("2015 / 2014")
            cat_4 = st.checkbox("2013 / 2012")
            cat_5 = st.checkbox("2011 / 2010")
            
            categoria_extra = st.text_input("Otra categoría adicional (opcional, ej: Sub-8 o 2008-2009)")
            nuevo_formato = st.selectbox("Formato general para estas categorías", ["Grupos", "Liga"])
            
            submit_copa = st.form_submit_button("Crear Todas las Seleccionadas")
            
            if submit_copa:
                lista_nuevas = []
                if cat_1: lista_nuevas.append("2019/2018")
                if cat_2: lista_nuevas.append("2017/2016")
                if cat_3: lista_nuevas.append("2015/2014")
                if cat_4: lista_nuevas.append("2013/2012")
                if cat_5: lista_nuevas.append("2011/2010")
                if categoria_extra.strip(): lista_nuevas.append(categoria_extra.strip())
                
                if lista_nuevas and nombre_personalizado:
                    nuevos_registros = []
                    for c in lista_nuevas:
                        nuevos_registros.append({
                            "Nombre_Copa": nombre_copa_final.strip(),
                            "Categoria": c,
                            "Formato": nuevo_formato
                        })
                    
                    df_nuevo = pd.DataFrame(nuevos_registros)
                    df_actual = df_config.copy()
                    df_actual = pd.concat([df_actual, df_nuevo], ignore_index=True)
                    conn.update(worksheet="Configuracion", data=df_actual)
                    st.success(f"¡Se han creado {len(lista_nuevas)} categorías para {nombre_copa_final} exitosamente!")
                    st.rerun()
                else:
                    st.warning("Debes poner un nombre de torneo y marcar al menos una categoría.")
                
    with tab2:
        st.write("Inscribe a los clubes y asigna sus grupos.")
        if not df_config.empty:
            lista_copas = df_config['Nombre_Copa'].dropna().unique()
            copa_eq = st.selectbox("Seleccionar Torneo / Sede:", lista_copas)
            
            categorias_disponibles = df_config[df_config['Nombre_Copa'] == copa_eq]['Categoria'].unique()
            categoria_eq = st.selectbox("Seleccionar Categoría (Años):", categorias_disponibles)
            
            with st.form("form_nuevo_equipo"):
                nombre_equipo = st.text_input("Nombre del Club / Academia (ej: Río Iñaque, Ñublense)")
                grupo_eq = st.text_input("Grupo (ej: A, B... o dejar en blanco si es Liga)")
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
            st.info("Primero debes crear al menos una categoría en la pestaña anterior.")

elif menu == "📝 Portal Profesores":
    st.subheader("📝 Inscripción Digital de Planteles (Profesores / DT)")
    st.write("Registra la nómina oficial de jugadores de tu club para el torneo.")
    
    if not df_equipos.empty:
        # Selección guiada para el profesor
        copa_dt = st.selectbox("1. Selecciona el Torneo:", df_equipos['Copa'].dropna().unique())
        
        cats_dt = df_equipos[df_equipos['Copa'] == copa_dt]['Categoria'].dropna().unique()
        cat_dt = st.selectbox("2. Selecciona la Categoría:", cats_dt)
        
        eqs_dt = df_equipos[(df_equipos['Copa'] == copa_dt) & (df_equipos['Categoria'] == cat_dt)]['Nombre_Equipo'].dropna().unique()
        
        if len(eqs_dt) > 0:
            equipo_dt = st.selectbox("3. Selecciona tu Club / Equipo:", eqs_dt)
            
            st.divider()
            st.markdown(f"### Nómina para: **{equipo_dt}** ({cat_dt})")
            
            # Formulario para ingresar jugador
            with st.form("form_ingresar_jugador", clear_on_submit=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    nombre_jugador = st.text_input("Nombre y Apellido del Jugador")
                with col_b:
                    dorsal_jugador = st.number_input("Dorsal (N°)", min_value=1, max_value=99, value=1)
                
                submit_jugador = st.form_submit_button("Agregar Jugador a la Nómina")
                
                if submit_jugador and nombre_jugador:
                    nuevo_j = pd.DataFrame([{
                        "Copa": copa_dt,
                        "Categoria": cat_dt,
                        "Equipo": equipo_dt,
                        "Nombre_Jugador": nombre_jugador.strip(),
                        "Dorsal": int(dorsal_jugador),
                        "Goles": 0
                    }])
                    df_j_actual = df_jugadores.copy()
                    df_j_actual = pd.concat([df_j_actual, nuevo_j], ignore_index=True)
                    conn.update(worksheet="Jugadores", data=df_j_actual)
                    st.success(f"¡Jugador {nombre_jugador} (#{dorsal_jugador}) agregado a la plantilla!")
                    st.rerun()
            
            # Mostrar la nómina actual del equipo
            st.write("**Plantel Inscrito Hasta el Momento:**")
            if not df_jugadores.empty:
                plantel_actual = df_jugadores[
                    (df_jugadores['Copa'] == copa_dt) & 
                    (df_jugadores['Categoria'] == cat_dt) & 
                    (df_jugadores['Equipo'] == equipo_dt)
                ]
                if not plantel_actual.empty:
                    st.dataframe(plantel_actual[['Dorsal', 'Nombre_Jugador']], hide_index=True, use_container_width=True)
                else:
                    st.info("Aún no hay jugadores inscritos en este equipo.")
            else:
                st.info("Aún no hay jugadores registrados en el sistema.")
        else:
            st.warning("No hay equipos inscritos en esta categoría todavía.")
    else:
        st.info("Aún no hay equipos registrados en el sistema para que los profesores puedan inscribir planteles.")
        
