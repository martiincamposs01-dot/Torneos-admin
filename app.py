import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gestión de Torneos", page_icon="🏆", layout="wide")
st.title("🏆 Plataforma Central de Torneos")

# 1. CONEXIÓN A GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_config = conn.read(worksheet="Configuracion")
    if df_config is None or df_config.empty:
        df_config = pd.DataFrame(columns=["Nombre_Copa", "Categoria", "Formato"])
    
    df_equipos = conn.read(worksheet="Equipos")
    if df_equipos is None or df_equipos.empty:
        df_equipos = pd.DataFrame(columns=["Copa", "Categoria", "Grupo", "Nombre_Equipo"])
        
    try:
        df_jugadores = conn.read(worksheet="Jugadores")
        if df_jugadores is None or df_jugadores.empty:
            df_jugadores = pd.DataFrame(columns=["Copa", "Categoria", "Equipo", "Nombre_Jugador", "Dorsal", "Goles"])
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
    
    df_config_clean = df_config.dropna(how="all")
    if not df_config_clean.empty:
        sedes_disponibles = ['Angol', 'Máfil', 'Valdivia']
        sede_seleccionada = st.selectbox("📍 Selecciona la Sede / Ciudad:", sedes_disponibles)
        
        st.divider()
        st.markdown(f"### 🏟️ Torneos activos en: {sede_seleccionada}")
        
        copas_sede = df_config_clean[df_config_clean['Nombre_Copa'].astype(str).str.contains(sede_seleccionada, case=False, na=False)]
        
        if not copas_sede.empty:
            copa_seleccionada = st.selectbox("Selecciona el Torneo específico:", copas_sede['Nombre_Copa'].unique())
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Categorías y Formatos en juego:**")
                categorias_copa = df_config_clean[df_config_clean['Nombre_Copa'] == copa_seleccionada]
                st.dataframe(categorias_copa[['Categoria', 'Formato']], hide_index=True, use_container_width=True)
                
            with col2:
                st.write("**Equipos Inscritos:**")
                df_equipos_clean = df_equipos.dropna(how="all")
                if not df_equipos_clean.empty:
                    equipos_copa = df_equipos_clean[df_equipos_clean['Copa'] == copa_seleccionada]
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
    
    tab1, tab2 = st.tabs(["🏆 Configurar Torneo y Categorías", "⚽ Inscribir Equipo"])
    
    with tab1:
        st.write("Crea las categorías del torneo indicando su formato independiente (Grupos o Liga).")
        
        with st.form("form_crear_copa_detalle"):
            sede_input = st.selectbox("Sede / Ciudad Principal", ["Angol", "Máfil", "Valdivia"])
            nombre_personalizado = st.text_input("Nombre del Torneo / Copa (ej: Mafil Cup 2025, Copa Invierno)")
            
            nombre_copa_final = f"{sede_input} - {nombre_personalizado}" if nombre_personalizado else sede_input
            
            st.markdown("---")
            st.write("### Asigna el formato para cada categoría participante:")
            
            c1_on = st.checkbox("Categoría 2018 / 2019")
            c1_formato = st.selectbox("Formato para 2018/2019", ["Grupos", "Liga"], key="f1")
            
            c2_on = st.checkbox("Categoría 2016 / 2017")
            c2_formato = st.selectbox("Formato para 2016/2017", ["Grupos", "Liga"], key="f2")
            
            c3_on = st.checkbox("Categoría 2014 / 2015")
            c3_formato = st.selectbox("Formato para 2014/2015", ["Grupos", "Liga"], key="f3")
            
            c4_on = st.checkbox("Categoría 2012 / 2013")
            c4_formato = st.selectbox("Formato para 2012/2013", ["Grupos", "Liga"], key="f4")
            
            c5_on = st.checkbox("Categoría 2010 / 2011")
            c5_formato = st.selectbox("Formato para 2010/2011", ["Grupos", "Liga"], key="f5")
            
            cat_extra_nombre = st.text_input("Otra categoría personalizada (opcional, ej: Sub-8)")
            cat_extra_formato = st.selectbox("Formato categoría personalizada", ["Grupos", "Liga"], key="f_extra")
            
            submit_creacion = st.form_submit_button("Guardar Torneo y Categorías")
            
            if submit_creacion:
                nuevos_registros = []
                
                if c1_on:
                    nuevos_registros.append({"Nombre_Copa": nombre_copa_final, "Categoria": "2018/2019", "Formato": c1_formato})
                if c2_on:
                    nuevos_registros.append({"Nombre_Copa": nombre_copa_final, "Categoria": "2016/2017", "Formato": c2_formato})
                if c3_on:
                    nuevos_registros.append({"Nombre_Copa": nombre_copa_final, "Categoria": "2014/2015", "Formato": c3_formato})
                if c4_on:
                    nuevos_registros.append({"Nombre_Copa": nombre_copa_final, "Categoria": "2012/2013", "Formato": c4_formato})
                if c5_on:
                    nuevos_registros.append({"Nombre_Copa": nombre_copa_final, "Categoria": "2010/2011", "Formato": c5_formato})
                if cat_extra_nombre.strip():
                    nuevos_registros.append({"Nombre_Copa": nombre_copa_final, "Categoria": cat_extra_nombre.strip(), "Formato": cat_extra_formato})
                
                if nuevos_registros and nombre_personalizado:
                    df_nuevo = pd.DataFrame(nuevos_registros)
                    df_actual = pd.concat([df_config.dropna(how="all"), df_nuevo], ignore_index=True)
                    conn.update(worksheet="Configuracion", data=df_actual)
                    st.success(f"¡Torneo '{nombre_copa_final}' guardado con sus respectivas categorías y formatos!")
                    st.rerun()
                else:
                    st.warning("Debes ingresar el nombre del torneo y seleccionar al menos una categoría.")
                
    with tab2:
        st.write("Inscribe a los clubes y asigna sus grupos.")
        df_config_clean = df_config.dropna(how="all")
        if not df_config_clean.empty:
            lista_copas = df_config_clean['Nombre_Copa'].dropna().unique()
            copa_eq = st.selectbox("Seleccionar Torneo / Sede:", lista_copas)
            
            categorias_disponibles = df_config_clean[df_config_clean['Nombre_Copa'] == copa_eq]['Categoria'].unique()
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
                    df_eq_actual = pd.concat([df_equipos.dropna(how="all"), nuevo_eq], ignore_index=True)
                    conn.update(worksheet="Equipos", data=df_eq_actual)
                    st.success(f"¡{nombre_equipo} inscrito correctamente!")
                    st.rerun()
        else:
            st.info("Primero debes configurar un torneo en la pestaña anterior.")

elif menu == "📝 Portal Profesores":
    st.subheader("📝 Inscripción Digital de Planteles (Profesores / DT)")
    st.write("Registra la nómina oficial de jugadores de tu club para el torneo.")
    
    df_equipos_clean = df_equipos.dropna(how="all")
    if not df_equipos_clean.empty:
        copa_dt = st.selectbox("1. Selecciona el Torneo:", df_equipos_clean['Copa'].dropna().unique())
        
        cats_dt = df_equipos_clean[df_equipos_clean['Copa'] == copa_dt]['Categoria'].dropna().unique()
        cat_dt = st.selectbox("2. Selecciona la Categoría:", cats_dt)
        
        eqs_dt = df_equipos_clean[(df_equipos_clean['Copa'] == copa_dt) & (df_equipos_clean['Categoria'] == cat_dt)]['Nombre_Equipo'].dropna().unique()
        
        if len(eqs_dt) > 0:
            equipo_dt = st.selectbox("3. Selecciona tu Club / Equipo:", eqs_dt)
            
            st.divider()
            st.markdown(f"### Nómina para: **{equipo_dt}** ({cat_dt})")
            
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
                    df_j_actual = pd.concat([df_jugadores.dropna(how="all"), nuevo_j], ignore_index=True)
                    conn.update(worksheet="Jugadores", data=df_j_actual)
                    st.success(f"¡Jugador {nombre_jugador} (#{dorsal_jugador}) agregado!")
                    st.rerun()
            
            st.write("**Plantel Inscrito Hasta el Momento:**")
            df_jugadores_clean = df_jugadores.dropna(how="all")
            if not df_jugadores_clean.empty:
                plantel_actual = df_jugadores_clean[
                    (df_jugadores_clean['Copa'] == copa_dt) & 
                    (df_jugadores_clean['Categoria'] == cat_dt) & 
                    (df_jugadores_clean['Equipo'] == equipo_dt)
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
        st.info("Aún no hay equipos registrados en el sistema.")
