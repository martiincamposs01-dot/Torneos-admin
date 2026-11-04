import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Gestión de Torneos", page_icon="🏆", layout="wide")
st.title("🏆 Plataforma Central de Torneos")

# 1. BASE DE DATOS SQLITE (Local, rápida y sin errores de API)
def conectar_db():
    # check_same_thread=False es necesario para Streamlit
    conexion = sqlite3.connect("torneos.db", check_same_thread=False)
    cursor = conexion.cursor()
    
    # Creamos las tablas con estructura flexible si no existen
    cursor.execute('''CREATE TABLE IF NOT EXISTS Configuracion (sede TEXT, nombre_copa TEXT, categoria TEXT, formato TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Equipos (copa TEXT, categoria TEXT, grupo TEXT, nombre_equipo TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Jugadores (copa TEXT, categoria TEXT, equipo TEXT, nombre_jugador TEXT, dorsal INTEGER, goles INTEGER)''')
    conexion.commit()
    return conexion

conn = conectar_db()

# Función rápida para convertir tablas SQL a Pandas DataFrames
def cargar_tabla(nombre_tabla):
    return pd.read_sql(f"SELECT * FROM {nombre_tabla}", conn)

df_config = cargar_tabla("Configuracion")
df_equipos = cargar_tabla("Equipos")
df_jugadores = cargar_tabla("Jugadores")

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
        
        copas_sede = df_config[df_config['nombre_copa'].str.contains(sede_seleccionada, case=False, na=False)]
        
        if not copas_sede.empty:
            copa_seleccionada = st.selectbox("Selecciona el Torneo específico:", copas_sede['nombre_copa'].unique())
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Categorías y Formatos en juego:**")
                categorias_copa = df_config[df_config['nombre_copa'] == copa_seleccionada]
                st.dataframe(categorias_copa[['categoria', 'formato']], hide_index=True, use_container_width=True)
                
            with col2:
                st.write("**Equipos Inscritos:**")
                if not df_equipos.empty:
                    equipos_copa = df_equipos[df_equipos['copa'] == copa_seleccionada]
                    if not equipos_copa.empty:
                        st.dataframe(equipos_copa[['categoria', 'grupo', 'nombre_equipo']], hide_index=True, use_container_width=True)
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
    
    tab1, tab2, tab3 = st.tabs(["🏆 Configurar Torneo", "⚽ Inscribir Equipo", "📥 Descargar Respaldos"])
    
    with tab1:
        st.write("Crea las categorías del torneo indicando su formato independiente.")
        
        with st.form("form_crear_copa"):
            sede_input = st.selectbox("Sede / Ciudad Principal", ["Angol", "Máfil", "Valdivia"])
            nombre_personalizado = st.text_input("Nombre del Torneo / Copa (ej: Mafil Cup 2025)")
            nombre_copa_final = f"{sede_input} - {nombre_personalizado}" if nombre_personalizado else sede_input
            
            st.markdown("---")
            st.write("### Asigna el formato para cada categoría participante:")
            
            c1_on = st.checkbox("Categoría 2018 / 2019")
            c1_formato = st.selectbox("Formato para 2018/2019", ["Grupos", "Liga"], key="f1")
            
            c2_on = st.checkbox("Categoría 2016 / 2017")
            c2_formato = st.selectbox("Formato para 2016/2017", ["Grupos", "Liga"], key="f2")
            
            cat_extra_nombre = st.text_input("Otra categoría personalizada (opcional)")
            cat_extra_formato = st.selectbox("Formato categoría personalizada", ["Grupos", "Liga"], key="f_extra")
            
            submit_creacion = st.form_submit_button("Guardar Torneo y Categorías")
            
            if submit_creacion and nombre_personalizado:
                cursor = conn.cursor()
                if c1_on:
                    cursor.execute("INSERT INTO Configuracion (sede, nombre_copa, categoria, formato) VALUES (?, ?, ?, ?)", (sede_input, nombre_copa_final, "2018/2019", c1_formato))
                if c2_on:
                    cursor.execute("INSERT INTO Configuracion (sede, nombre_copa, categoria, formato) VALUES (?, ?, ?, ?)", (sede_input, nombre_copa_final, "2016/2017", c2_formato))
                if cat_extra_nombre.strip():
                    cursor.execute("INSERT INTO Configuracion (sede, nombre_copa, categoria, formato) VALUES (?, ?, ?, ?)", (sede_input, nombre_copa_final, cat_extra_nombre.strip(), cat_extra_formato))
                
                conn.commit()
                st.success(f"¡Torneo '{nombre_copa_final}' guardado exitosamente!")
                st.rerun()
                
    with tab2:
        st.write("Inscribe a los clubes y asigna sus grupos.")
        if not df_config.empty:
            lista_copas = df_config['nombre_copa'].dropna().unique()
            copa_eq = st.selectbox("Seleccionar Torneo / Sede:", lista_copas)
            
            categorias_disponibles = df_config[df_config['nombre_copa'] == copa_eq]['categoria'].unique()
            categoria_eq = st.selectbox("Seleccionar Categoría (Años):", categorias_disponibles)
            
            with st.form("form_nuevo_equipo"):
                nombre_equipo = st.text_input("Nombre del Club / Academia (ej: Río Iñaque)")
                grupo_eq = st.text_input("Grupo (ej: A, B... o dejar en blanco si es Liga)")
                submit_equipo = st.form_submit_button("Inscribir Equipo")
                
                if submit_equipo and nombre_equipo:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Equipos (copa, categoria, grupo, nombre_equipo) VALUES (?, ?, ?, ?)", (copa_eq, categoria_eq, grupo_eq.strip().upper(), nombre_equipo.strip()))
                    conn.commit()
                    st.success(f"¡{nombre_equipo} inscrito correctamente!")
                    st.rerun()
        else:
            st.info("Primero debes configurar un torneo.")
            
    with tab3:
        st.write("Descarga la base de datos actual para respaldar en tu computador.")
        st.write("*(Nota: Streamlit Cloud borra datos locales si la app se suspende por inactividad. Descarga un respaldo siempre al terminar de trabajar).*")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.download_button("📥 Descargar Torneos", data=df_config.to_csv(index=False).encode('utf-8-sig'), file_name="respaldo_torneos.csv", mime="text/csv")
        with col_b:
            st.download_button("📥 Descargar Equipos", data=df_equipos.to_csv(index=False).encode('utf-8-sig'), file_name="respaldo_equipos.csv", mime="text/csv")
        with col_c:
            st.download_button("📥 Descargar Jugadores", data=df_jugadores.to_csv(index=False).encode('utf-8-sig'), file_name="respaldo_jugadores.csv", mime="text/csv")

elif menu == "📝 Portal Profesores":
    st.subheader("📝 Inscripción Digital de Planteles (Profesores / DT)")
    
    if not df_equipos.empty:
        copa_dt = st.selectbox("1. Selecciona el Torneo:", df_equipos['copa'].dropna().unique())
        cats_dt = df_equipos[df_equipos['copa'] == copa_dt]['categoria'].dropna().unique()
        cat_dt = st.selectbox("2. Selecciona la Categoría:", cats_dt)
        eqs_dt = df_equipos[(df_equipos['copa'] == copa_dt) & (df_equipos['categoria'] == cat_dt)]['nombre_equipo'].dropna().unique()
        
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
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Jugadores (copa, categoria, equipo, nombre_jugador, dorsal, goles) VALUES (?, ?, ?, ?, ?, ?)", (copa_dt, cat_dt, equipo_dt, nombre_jugador.strip(), int(dorsal_jugador), 0))
                    conn.commit()
                    st.success(f"¡Jugador {nombre_jugador} (#{dorsal_jugador}) agregado!")
                    st.rerun()
            
            st.write("**Plantel Inscrito Hasta el Momento:**")
            if not df_jugadores.empty:
                plantel_actual = df_jugadores[(df_jugadores['copa'] == copa_dt) & (df_jugadores['categoria'] == cat_dt) & (df_jugadores['equipo'] == equipo_dt)]
                if not plantel_actual.empty:
                    st.dataframe(plantel_actual[['dorsal', 'nombre_jugador']], hide_index=True, use_container_width=True)
                else:
                    st.info("Aún no hay jugadores inscritos en este equipo.")
        else:
            st.warning("No hay equipos inscritos en esta categoría todavía.")
    else:
        st.info("Aún no hay equipos registrados en el sistema.")
