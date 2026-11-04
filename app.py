import streamlit as st
import pandas as pd
import sqlite3

# 1. CONFIGURACIÓN DE PÁGINA Y ESTÉTICA DE FÚTBOL (CSS)
st.set_page_config(page_title="Plataforma Oficial de Torneos", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    /* Fondo general y textos */
    .main-header {
        background: linear-gradient(135deg, #0b3d20 0%, #146b3a 50%, #092916 100%);
        padding: 25px;
        border-radius: 15px;
        border-bottom: 4px solid #f5b041;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #ffffff;
    }
    .main-header p {
        margin: 5px 0 0 0;
        color: #f5b041;
        font-weight: 600;
        font-size: 1.05rem;
    }
    /* Tarjetas de Partidos estilo Mafil Cup */
    .match-card {
        background: linear-gradient(90deg, #1a242f 0%, #243447 50%, #1a242f 100%);
        border: 1px solid #34495e;
        border-left: 5px solid #f5b041;
        border-radius: 12px;
        padding: 15px 20px;
        margin-bottom: 14px;
        color: white;
        box-shadow: 0 3px 8px rgba(0,0,0,0.25);
    }
    .match-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        font-weight: 700;
        color: #5dade2;
        text-transform: uppercase;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 5px;
    }
    .match-body {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.15rem;
        font-weight: 700;
    }
    .team-name {
        width: 40%;
        text-transform: uppercase;
    }
    .team-right {
        text-align: right;
    }
    .score-badge {
        background: #b01e28;
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 1.1rem;
        border: 2px solid #f5b041;
        min-width: 85px;
        text-align: center;
    }
    .vs-badge {
        background: #2e4053;
        color: #f5b041;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.95rem;
        border: 1px solid #f5b041;
    }
    .stat-box {
        background-color: #16202a;
        border: 1px solid #2c3e50;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🏆 Plataforma Oficial de Torneos</h1>
    <p>⚽ Gestión en Vivo • Angol • Máfil • Valdivia</p>
</div>
""", unsafe_allow_html=True)

# 2. CONEXIÓN Y CREACIÓN DE TABLAS EN SQLITE
def conectar_db():
    conexion = sqlite3.connect("torneos.db", check_same_thread=False)
    cursor = conexion.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Configuracion (
        sede TEXT, nombre_copa TEXT, categoria TEXT, formato TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Equipos (
        copa TEXT, categoria TEXT, grupo TEXT, nombre_equipo TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Jugadores (
        copa TEXT, categoria TEXT, equipo TEXT, nombre_jugador TEXT, dorsal INTEGER, goles INTEGER
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Partidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        copa TEXT, categoria TEXT, fase TEXT, cancha TEXT, hora TEXT,
        equipo_local TEXT, equipo_visita TEXT,
        goles_local INTEGER, goles_visita INTEGER, estado TEXT
    )''')
    conexion.commit()
    return conexion

conn = conectar_db()

def cargar_tabla(nombre_tabla):
    return pd.read_sql(f"SELECT * FROM {nombre_tabla}", conn)

df_config = cargar_tabla("Configuracion")
df_equipos = cargar_tabla("Equipos")
df_jugadores = cargar_tabla("Jugadores")
df_partidos = cargar_tabla("Partidos")

# Función para calcular Tabla de Posiciones automáticamente
def calcular_posiciones(df_eq_cat, df_part_cat):
    equipos = df_eq_cat['nombre_equipo'].unique()
    tabla = []
    for eq in equipos:
        grupo = df_eq_cat[df_eq_cat['nombre_equipo'] == eq]['grupo'].values[0]
        pj = pg = pe = pp = gf = gc = pts = 0
        
        partidos_jugados = df_part_cat[
            (df_part_cat['estado'] == 'Finalizado') & 
            (df_part_cat['fase'] == 'Fase Regular / Grupos')
        ]
        
        for _, p in partidos_jugados.iterrows():
            if p['equipo_local'] == eq:
                pj += 1
                gf += int(p['goles_local'])
                gc += int(p['goles_visita'])
                if p['goles_local'] > p['goles_visita']:
                    pg += 1; pts += 3
                elif p['goles_local'] == p['goles_visita']:
                    pe += 1; pts += 1
                else:
                    pp += 1
            elif p['equipo_visita'] == eq:
                pj += 1
                gf += int(p['goles_visita'])
                gc += int(p['goles_local'])
                if p['goles_visita'] > p['goles_local']:
                    pg += 1; pts += 3
                elif p['goles_visita'] == p['goles_local']:
                    pe += 1; pts += 1
                else:
                    pp += 1
                    
        dg = gf - gc
        tabla.append({
            "Grupo": grupo if grupo else "General",
            "Equipo": eq, "PTS": pts, "PJ": pj, "PG": pg, 
            "PE": pe, "PP": pp, "GF": gf, "GC": gc, "DG": dg
        })
    df_t = pd.DataFrame(tabla)
    if not df_t.empty:
        df_t = df_t.sort_values(by=["PTS", "DG", "GF"], ascending=[False, False, False]).reset_index(drop=True)
        df_t.index = df_t.index + 1
    return df_t

# 3. MENÚ LATERAL
st.sidebar.markdown("## 🧭 Panel de Navegación")
menu = st.sidebar.radio(
    "Selecciona el módulo:", 
    ["🏟️ Lobby Público (En Vivo)", "📝 Portal Profesores (Planillas)", "⚙️ Panel Staff (Admin)"]
)
st.sidebar.divider()
st.sidebar.caption("⚽ Sistema Oficial de Campeonatos")

# ==========================================
# MÓDULO 1: LOBBY PÚBLICO
# ==========================================
if menu == "🏟️ Lobby Público (En Vivo)":
    if not df_config.empty:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            sedes_disponibles = ['Angol', 'Máfil', 'Valdivia']
            sede_sel = st.selectbox("📍 1. Sede / Ciudad:", sedes_disponibles)
            
        copas_sede = df_config[df_config['nombre_copa'].str.contains(sede_sel, case=False, na=False)]
        
        if not copas_sede.empty:
            with col_f2:
                copa_sel = st.selectbox("🏆 2. Torneo:", copas_sede['nombre_copa'].unique())
            
            cats_copa = df_config[df_config['nombre_copa'] == copa_sel]
            with col_f3:
                cat_sel = st.selectbox("👟 3. Categoría (Año):", cats_copa['categoria'].unique())
                
            formato_actual = cats_copa[cats_copa['categoria'] == cat_sel]['formato'].values[0]
            
            st.markdown(f"#### 📌 Viendo: **{copa_sel}** — Categoría **{cat_sel}** *(Formato: {formato_actual})*")
            
            tab_fix, tab_pos, tab_gol, tab_plan = st.tabs([
                "📅 Fixture y Resultados", 
                "📊 Tabla de Posiciones", 
                "🥇 Tabla de Goleadores", 
                "🛡️ Equipos y Planteles"
            ])
            
            # PESTAÑA 1: FIXTURE Y RESULTADOS
            with tab_fix:
                partidos_cat = df_partidos[
                    (df_partidos['copa'] == copa_sel) & 
                    (df_partidos['categoria'] == cat_sel)
                ]
                if not partidos_cat.empty:
                    for _, part in partidos_cat.iterrows():
                        if part['estado'] == "Finalizado":
                            marcador_html = f'<div class="score-badge">{part["goles_local"]} - {part["goles_visita"]}</div>'
                            estado_badge = "✅ FINALIZADO"
                        else:
                            marcador_html = '<div class="vs-badge">VS</div>'
                            estado_badge = "⏳ PROGRAMADO"
                            
                        st.markdown(f"""
                        <div class="match-card">
                            <div class="match-header">
                                <span>🕒 {part['hora']} | 📍 {part['cancha']}</span>
                                <span>🏆 {part['fase']} — {estado_badge}</span>
                            </div>
                            <div class="match-body">
                                <div class="team-name">{part['equipo_local']}</div>
                                {marcador_html}
                                <div class="team-name team-right">{part['equipo_visita']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Aún no se han programado partidos para esta categoría.")
                    
            # PESTAÑA 2: TABLA DE POSICIONES
            with tab_pos:
                eq_cat = df_equipos[(df_equipos['copa'] == copa_sel) & (df_equipos['categoria'] == cat_sel)]
                part_cat = df_partidos[(df_partidos['copa'] == copa_sel) & (df_partidos['categoria'] == cat_sel)]
                
                if not eq_cat.empty:
                    df_pos = calcular_posiciones(eq_cat, part_cat)
                    if formato_actual == "Grupos":
                        grupos_unicos = sorted(df_pos['Grupo'].unique())
                        for g in grupos_unicos:
                            st.markdown(f"##### 🟢 Grupo {g}")
                            df_g = df_pos[df_pos['Grupo'] == g].drop(columns=['Grupo']).reset_index(drop=True)
                            df_g.index = df_g.index + 1
                            st.dataframe(df_g, use_container_width=True)
                    else:
                        st.markdown("##### 🏆 Clasificación General (Liga)")
                        st.dataframe(df_pos.drop(columns=['Grupo']), use_container_width=True)
                else:
                    st.info("Inscribe equipos en esta categoría para ver la tabla de posiciones.")
                    
            # PESTAÑA 3: GOLEADORES
            with tab_gol:
                jug_cat = df_jugadores[
                    (df_jugadores['copa'] == copa_sel) & 
                    (df_jugadores['categoria'] == cat_sel) & 
                    (df_jugadores['goles'] > 0)
                ].copy()
                
                if not jug_cat.empty:
                    jug_cat = jug_cat.sort_values(by="goles", ascending=False).reset_index(drop=True)
                    jug_cat.index = jug_cat.index + 1
                    jug_cat['Dorsal_Txt'] = jug_cat['dorsal'].apply(lambda x: f"#{int(x)}" if pd.notnull(x) and int(x) > 0 else "S/N")
                    st.dataframe(
                        jug_cat[['nombre_jugador', 'equipo', 'Dorsal_Txt', 'goles']].rename(columns={
                            'nombre_jugador': 'Jugador',
                            'equipo': 'Club / Escuela',
                            'Dorsal_Txt': 'Dorsal',
                            'goles': 'Goles ⚽'
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("Aún no se han registrado goles en esta categoría.")
                    
            # PESTAÑA 4: PLANTELES
            with tab_plan:
                eq_cat = df_equipos[(df_equipos['copa'] == copa_sel) & (df_equipos['categoria'] == cat_sel)]
                if not eq_cat.empty:
                    club_ver = st.selectbox("Selecciona un Club para ver su nómina:", eq_cat['nombre_equipo'].unique())
                    nomina = df_jugadores[
                        (df_jugadores['copa'] == copa_sel) & 
                        (df_jugadores['categoria'] == cat_sel) & 
                        (df_jugadores['equipo'] == club_ver)
                    ].copy()
                    if not nomina.empty:
                        nomina['Camiseta'] = nomina['dorsal'].apply(lambda x: f"#{int(x)}" if pd.notnull(x) and int(x) > 0 else "Pendiente (S/N)")
                        st.dataframe(
                            nomina[['Camiseta', 'nombre_jugador', 'goles']].rename(columns={
                                'nombre_jugador': 'Nombre del Jugador',
                                'goles': 'Goles'
                            }),
                            hide_index=True, use_container_width=True
                        )
                    else:
                        st.info("Este club aún no ha cargado jugadores en su planilla.")
                else:
                    st.info("No hay clubes inscritos en esta categoría.")
        else:
            st.info(f"Aún no hay torneos activos para la sede {sede_sel}.")
    else:
        st.info("Bienvenido. Aún no hay torneos configurados. Ingresa al 'Panel Staff (Admin)' para crear el primero.")

# ==========================================
# MÓDULO 2: PORTAL PROFESORES (PLANILLAS)
# ==========================================
elif menu == "📝 Portal Profesores (Planillas)":
    st.subheader("📝 Inscripción Digital de Planteles y Asignación de Dorsales")
    st.write("Inscribe a tus jugadores (el dorsal es **opcional** al inscribir y puedes agregarlo o editarlo justo antes de jugar).")
    
    if not df_equipos.empty:
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            copa_dt = st.selectbox("1. Torneo:", df_equipos['copa'].dropna().unique())
        with col_p2:
            cats_dt = df_equipos[df_equipos['copa'] == copa_dt]['categoria'].dropna().unique()
            cat_dt = st.selectbox("2. Categoría:", cats_dt)
        with col_p3:
            eqs_dt = df_equipos[(df_equipos['copa'] == copa_dt) & (df_equipos['categoria'] == cat_dt)]['nombre_equipo'].dropna().unique()
            equipo_dt = st.selectbox("3. Tu Club / Academia:", eqs_dt) if len(eqs_dt) > 0 else None
            
        if equipo_dt:
            st.divider()
            col_izq, col_der = st.columns([1, 1.4])
            
            with col_izq:
                st.markdown(f"#### ➕ Agregar Jugador a **{equipo_dt}**")
                with st.form("form_ingresar_jugador", clear_on_submit=True):
                    nombre_jugador = st.text_input("Nombre y Apellido del Jugador *")
                    dorsal_jugador = st.number_input(
                        "Dorsal / N° Camiseta (Deja en 0 si aún no tiene dorsal asignado)", 
                        min_value=0, max_value=99, value=0
                    )
                    submit_jugador = st.form_submit_button("Inscribir Jugador en Nómina")
                    
                    if submit_jugador and nombre_jugador.strip():
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO Jugadores (copa, categoria, equipo, nombre_jugador, dorsal, goles) VALUES (?, ?, ?, ?, ?, ?)", 
                            (copa_dt, cat_dt, equipo_dt, nombre_jugador.strip(), int(dorsal_jugador), 0)
                        )
                        conn.commit()
                        st.success(f"¡{nombre_jugador} inscrito correctamente!")
                        st.rerun()
                        
            with col_der:
                st.markdown(f"#### 👕 Nómina y Dorsales Pre-Partido ({cat_dt})")
                st.caption("Haz doble clic en la columna **Dorsal** para anotar o cambiar los números de camiseta antes del partido y presiona Guardar.")
                
                plantel_actual = df_jugadores[
                    (df_jugadores['copa'] == copa_dt) & 
                    (df_jugadores['categoria'] == cat_dt) & 
                    (df_jugadores['equipo'] == equipo_dt)
                ].copy()
                
                if not plantel_actual.empty:
                    df_editable = st.data_editor(
                        plantel_actual[['nombre_jugador', 'dorsal']],
                        column_config={
                            "nombre_jugador": st.column_config.TextColumn("Nombre del Jugador", disabled=True),
                            "dorsal": st.column_config.NumberColumn("Dorsal (0 = S/N)", min_value=0, max_value=99, step=1)
                        },
                        hide_index=True,
                        use_container_width=True,
                        key="editor_dorsales_dt"
                    )
                    
                    if st.button("💾 Guardar Dorsales Actualizados"):
                        cursor = conn.cursor()
                        for _, fila in df_editable.iterrows():
                            cursor.execute(
                                "UPDATE Jugadores SET dorsal = ? WHERE copa = ? AND categoria = ? AND equipo = ? AND nombre_jugador = ?",
                                (int(fila['dorsal']) if pd.notnull(fila['dorsal']) else 0, copa_dt, cat_dt, equipo_dt, fila['nombre_jugador'])
                            )
                        conn.commit()
                        st.success("¡Dorsales actualizados para el partido!")
                        st.rerun()
                else:
                    st.info("Aún no hay jugadores inscritos en este equipo.")
    else:
        st.info("Aún no hay clubes registrados en el sistema.")

# ==========================================
# MÓDULO 3: PANEL STAFF (ADMIN)
# ==========================================
elif menu == "⚙️ Panel Staff (Admin)":
    st.subheader("⚙️ Consola Central de Control y Mesa Técnica")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 1. Crear Torneo", 
        "🛡️ 2. Inscribir Equipos", 
        "📅 3. Programar Fixture", 
        "⚽ 4. Resultados y Goles", 
        "📥 5. Respaldos"
    ])
    
    # TAB 1: CONFIGURAR TORNEO Y CATEGORÍAS
    with tab1:
        st.write("Configura el torneo y selecciona los formatos independientes (Grupos o Liga) para cada categoría.")
        with st.form("form_crear_copa"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                sede_input = st.selectbox("Sede / Ciudad Principal", ["Angol", "Máfil", "Valdivia"])
            with col_s2:
                nombre_personalizado = st.text_input("Nombre del Torneo (ej: Mafil Cup 2026)")
                
            nombre_copa_final = f"{sede_input} - {nombre_personalizado.strip()}" if nombre_personalizado.strip() else sede_input
            
            st.markdown("##### Selecciona las categorías participantes y su formato:")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c1_on = st.checkbox("Categoría 2018 / 2019")
                c1_formato = st.selectbox("Formato 2018/2019", ["Grupos", "Liga"], key="f1")
                
                c2_on = st.checkbox("Categoría 2016 / 2017")
                c2_formato = st.selectbox("Formato 2016/2017", ["Grupos", "Liga"], key="f2")
                
                c3_on = st.checkbox("Categoría 2014 / 2015")
                c3_formato = st.selectbox("Formato 2014/2015", ["Grupos", "Liga"], key="f3")
            with c_col2:
                c4_on = st.checkbox("Categoría 2012 / 2013")
                c4_formato = st.selectbox("Formato 2012/2013", ["Grupos", "Liga"], key="f4")
                
                c5_on = st.checkbox("Categoría 2010 / 2011")
                c5_formato = st.selectbox("Formato 2010/2011", ["Grupos", "Liga"], key="f5")
                
                cat_extra_nombre = st.text_input("Otra categoría (ej: 2011-2012 o 2017-2018)")
                cat_extra_formato = st.selectbox("Formato otra categoría", ["Grupos", "Liga"], key="f_extra")
                
            submit_creacion = st.form_submit_button("💾 Guardar Torneo y Categorías")
            
            if submit_creacion and nombre_personalizado.strip():
                cursor = conn.cursor()
                cats_a_guardar = []
                if c1_on: cats_a_guardar.append(("2018/2019", c1_formato))
                if c2_on: cats_a_guardar.append(("2016/2017", c2_formato))
                if c3_on: cats_a_guardar.append(("2014/2015", c3_formato))
                if c4_on: cats_a_guardar.append(("2012/2013", c4_formato))
                if c5_on: cats_a_guardar.append(("2010/2011", c5_formato))
                if cat_extra_nombre.strip(): cats_a_guardar.append((cat_extra_nombre.strip(), cat_extra_formato))
                
                if cats_a_guardar:
                    for cat_nom, cat_form in cats_a_guardar:
                        cursor.execute(
                            "INSERT INTO Configuracion (sede, nombre_copa, categoria, formato) VALUES (?, ?, ?, ?)",
                            (sede_input, nombre_copa_final, cat_nom, cat_form)
                        )
                    conn.commit()
                    st.success(f"¡Torneo '{nombre_copa_final}' creado con {len(cats_a_guardar)} categoría(s)!")
                    st.rerun()
                else:
                    st.warning("Marca al menos una categoría.")
                    
    # TAB 2: INSCRIBIR EQUIPOS
    with tab2:
        if not df_config.empty:
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                copa_eq = st.selectbox("Seleccionar Torneo:", df_config['nombre_copa'].unique(), key="eq_copa")
            with col_e2:
                cats_disp = df_config[df_config['nombre_copa'] == copa_eq]['categoria'].unique()
                categoria_eq = st.selectbox("Seleccionar Categoría:", cats_disp, key="eq_cat")
                
            with st.form("form_nuevo_equipo", clear_on_submit=True):
                col_n1, col_n2 = st.columns([2, 1])
                with col_n1:
                    nombre_equipo = st.text_input("Nombre del Club / Escuela (ej: Río Iñaque, Ñublense Temuco, Angol City)")
                with col_n2:
                    grupo_eq = st.text_input("Grupo (ej: A, B o vacío si es Liga)")
                submit_equipo = st.form_submit_button("➕ Inscribir Club")
                
                if submit_equipo and nombre_equipo.strip():
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO Equipos (copa, categoria, grupo, nombre_equipo) VALUES (?, ?, ?, ?)",
                        (copa_eq, categoria_eq, grupo_eq.strip().upper(), nombre_equipo.strip())
                    )
                    conn.commit()
                    st.success(f"¡Club {nombre_equipo} inscrito en {categoria_eq}!")
                    st.rerun()
        else:
            st.info("Primero crea un torneo en la Pestaña 1.")
            
    # TAB 3: PROGRAMAR FIXTURE Y HORARIOS
    with tab3:
        st.write("Programa los cruces, asignando cancha, horario y fase del campeonato.")
        if not df_equipos.empty:
            col_fx1, col_fx2 = st.columns(2)
            with col_fx1:
                copa_fx = st.selectbox("Torneo:", df_equipos['copa'].unique(), key="fx_copa")
            with col_fx2:
                cats_fx = df_equipos[df_equipos['copa'] == copa_fx]['categoria'].unique()
                cat_fx = st.selectbox("Categoría:", cats_fx, key="fx_cat")
                
            equipos_cat_fx = list(df_equipos[(df_equipos['copa'] == copa_fx) & (df_equipos['categoria'] == cat_fx)]['nombre_equipo'].unique())
            opciones_equipos = equipos_cat_fx + ["1° Grupo A", "1° Grupo B", "2° Grupo A", "2° Grupo B", "Ganador Semifinal 1", "Ganador Semifinal 2"]
            
            with st.form("form_programar_partido", clear_on_submit=True):
                c_p1, c_p2, c_p3 = st.columns(3)
                with c_p1:
                    fase_part = st.selectbox("Fase del Torneo", [
                        "Fase Regular / Grupos", "Semifinal", "3er y 4to Lugar", 
                        "Final Copa Plata", "Final Copa Oro"
                    ])
                with c_p2:
                    cancha_part = st.text_input("Cancha (ej: CANCHA A, CANCHA B)", value="CANCHA A")
                with c_p3:
                    hora_part = st.text_input("Horario (ej: 09:00 HRS, 10:00 HRS)", value="09:00 HRS")
                    
                c_eq1, c_eq2 = st.columns(2)
                with c_eq1:
                    eq_local = st.selectbox("Equipo Local:", opciones_equipos, key="loc_fx")
                with c_eq2:
                    eq_visita = st.selectbox("Equipo Visita:", opciones_equipos, index=min(1, len(opciones_equipos)-1), key="vis_fx")
                    
                submit_partido = st.form_submit_button("📅 Publicar Partido en el Fixture")
                
                if submit_partido:
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO Partidos 
                        (copa, categoria, fase, cancha, hora, equipo_local, equipo_visita, goles_local, goles_visita, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 'Programado')''',
                        (copa_fx, cat_fx, fase_part, cancha_part.strip().upper(), hora_part.strip().upper(), eq_local, eq_visita)
                    )
                    conn.commit()
                    st.success(f"Partido programado: {eq_local} vs {eq_visita} ({hora_part} - {cancha_part})")
                    st.rerun()
        else:
            st.info("Inscribe equipos en la Pestaña 2 para poder armar el fixture.")
            
    # TAB 4: INGRESAR RESULTADOS, GOLES Y DORSALES EN MESA
    with tab4:
        st.write("Ingresa el marcador final del partido, asigna goles a los jugadores o actualiza dorsales en mesa.")
        if not df_partidos.empty:
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                copa_res = st.selectbox("Torneo:", df_partidos['copa'].unique(), key="res_copa")
            with col_r2:
                cats_res = df_partidos[df_partidos['copa'] == copa_res]['categoria'].unique()
                cat_res = st.selectbox("Categoría:", cats_res, key="res_cat")
                
            partidos_disp = df_partidos[(df_partidos['copa'] == copa_res) & (df_partidos['categoria'] == cat_res)].copy()
            
            if not partidos_disp.empty:
                partidos_disp['Etiqueta'] = partidos_disp.apply(
                    lambda r: f"#{r['id']} | [{r['hora']} - {r['cancha']}] {r['equipo_local']} vs {r['equipo_visita']} ({r['estado']})", axis=1
                )
                partido_sel_etiqueta = st.selectbox("Selecciona el Partido:", partidos_disp['Etiqueta'])
                partido_row = partidos_disp[partidos_disp['Etiqueta'] == partido_sel_etiqueta].iloc[0]
                id_partido = int(partido_row['id'])
                loc_actual = partido_row['equipo_local']
                vis_actual = partido_row['equipo_visita']
                
                # Opción rápida para revisar/poner dorsales justo antes de jugar
                with st.expander(f"👕 Revisar o Asignar Dorsales Antes del Partido ({loc_actual} vs {vis_actual})"):
                    nomina_partido = df_jugadores[
                        (df_jugadores['copa'] == copa_res) & 
                        (df_jugadores['categoria'] == cat_res) & 
                        (df_jugadores['equipo'].isin([loc_actual, vis_actual]))
                    ].copy()
                    if not nomina_partido.empty:
                        editor_mesa = st.data_editor(
                            nomina_partido[['equipo', 'nombre_jugador', 'dorsal']],
                            column_config={
                                "equipo": st.column_config.TextColumn("Equipo", disabled=True),
                                "nombre_jugador": st.column_config.TextColumn("Jugador", disabled=True),
                                "dorsal": st.column_config.NumberColumn("Dorsal (0 = S/N)", min_value=0, max_value=99, step=1)
                            },
                            hide_index=True, use_container_width=True, key="editor_mesa_staff"
                        )
                        if st.button("💾 Actualizar Dorsales en Mesa"):
                            cursor = conn.cursor()
                            for _, fila in editor_mesa.iterrows():
                                cursor.execute(
                                    "UPDATE Jugadores SET dorsal = ? WHERE copa = ? AND categoria = ? AND equipo = ? AND nombre_jugador = ?",
                                    (int(fila['dorsal']) if pd.notnull(fila['dorsal']) else 0, copa_res, cat_res, fila['equipo'], fila['nombre_jugador'])
                                )
                            conn.commit()
                            st.success("¡Dorsales actualizados!")
                            st.rerun()
                    else:
                        st.info("Los clubes de este partido aún no tienen jugadores cargados en sus nóminas.")
                
                col_marcador, col_goles = st.columns(2)
                
                with col_marcador:
                    st.markdown("##### 🏁 1. Marcador Oficial del Partido")
                    with st.form("form_guardar_resultado"):
                        g_loc = st.number_input(f"Goles {loc_actual}", min_value=0, max_value=30, value=int(partido_row['goles_local']))
                        g_vis = st.number_input(f"Goles {vis_actual}", min_value=0, max_value=30, value=int(partido_row['goles_visita']))
                        est_nuevo = st.selectbox("Estado del Partido", ["Finalizado", "Programado"], index=0 if partido_row['estado']=="Finalizado" else 1)
                        
                        if st.form_submit_button("✅ Guardar Marcador y Actualizar Tabla"):
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE Partidos SET goles_local = ?, goles_visita = ?, estado = ? WHERE id = ?",
                                (int(g_loc), int(g_vis), est_nuevo, id_partido)
                            )
                            conn.commit()
                            st.success("¡Marcador guardado y Tabla de Posiciones actualizada!")
                            st.rerun()
                            
                with col_goles:
                    st.markdown("##### 👟 2. Sumar Goles a Jugadores (Goleadores)")
                    jug_partido = df_jugadores[
                        (df_jugadores['copa'] == copa_res) & 
                        (df_jugadores['categoria'] == cat_res) & 
                        (df_jugadores['equipo'].isin([loc_actual, vis_actual]))
                    ].copy()
                    
                    if not jug_partido.empty:
                        with st.form("form_sumar_goles"):
                            jug_partido['Etiqueta_Jug'] = jug_partido.apply(
                                lambda j: f"{j['equipo']} | #{int(j['dorsal']) if pd.notnull(j['dorsal']) and int(j['dorsal'])>0 else 'S/N'} - {j['nombre_jugador']} ({j['goles']} goles)", axis=1
                            )
                            jug_sel_et = st.selectbox("Seleccionar Goleador:", jug_partido['Etiqueta_Jug'])
                            cant_goles = st.number_input("Cantidad de goles a sumar en este partido:", min_value=1, max_value=15, value=1)
                            
                            if st.form_submit_button("⚽ Sumar Gol(es) al Jugador"):
                                jug_row = jug_partido[jug_partido['Etiqueta_Jug'] == jug_sel_et].iloc[0]
                                cursor = conn.cursor()
                                cursor.execute(
                                    "UPDATE Jugadores SET goles = goles + ? WHERE copa = ? AND categoria = ? AND equipo = ? AND nombre_jugador = ?",
                                    (int(cant_goles), copa_res, cat_res, jug_row['equipo'], jug_row['nombre_jugador'])
                                )
                                conn.commit()
                                st.success(f"¡Se sumaron {cant_goles} gol(es) a {jug_row['nombre_jugador']}!")
                                st.rerun()
                    else:
                        st.info("Inscribe jugadores en el Portal Profesores para poder asignarles goles individuales.")
        else:
            st.info("Aún no hay partidos programados en el fixture.")
            
    # TAB 5: RESPALDOS
    with tab5:
        st.write("Descarga en un clic toda la información del campeonato en formato Excel (CSV).")
        c_b1, c_b2, c_b3, c_b4 = st.columns(4)
        with c_b1:
            st.download_button("📥 Descargar Torneos", data=df_config.to_csv(index=False).encode('utf-8-sig'), file_name="torneos.csv", mime="text/csv")
        with c_b2:
            st.download_button("📥 Descargar Equipos", data=df_equipos.to_csv(index=False).encode('utf-8-sig'), file_name="equipos.csv", mime="text/csv")
        with c_b3:
            st.download_button("📥 Descargar Jugadores", data=df_jugadores.to_csv(index=False).encode('utf-8-sig'), file_name="jugadores.csv", mime="text/csv")
        with c_b4:
            st.download_button("📥 Descargar Partidos", data=df_partidos.to_csv(index=False).encode('utf-8-sig'), file_name="partidos.csv", mime="text/csv")
