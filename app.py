import streamlit as st
import pandas as pd
import sqlite3

# 1. CONFIGURACIÓN DE PÁGINA Y ESTÉTICA CLARA DEPORTIVA (MODO ESTADIO DÍA)
st.set_page_config(page_title="Plataforma Oficial de Torneos", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    /* Forzar tema claro, limpio y deportivo */
    .stApp {
        background-color: #f4f7f9;
        color: #1e293b;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #0f172a !important;
    }
    
    /* Encabezado Principal Verde Césped Luminoso */
    .hero-banner {
        background: linear-gradient(135deg, #059669 0%, #10b981 60%, #047857 100%);
        padding: 28px 30px;
        border-radius: 18px;
        color: white !important;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(5, 150, 105, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 5px solid #fbbf24;
    }
    .hero-banner h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    .hero-banner p {
        margin: 6px 0 0 0;
        color: #ecfdf5 !important;
        font-weight: 600;
        font-size: 1.05rem;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
        padding: 10px 18px;
        border-radius: 12px;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.95rem;
        border: 1px solid rgba(255,255,255,0.35);
        text-align: center;
    }

    /* Tarjetas Blancas Limpias para Contenedores */
    .white-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 18px 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        margin-bottom: 16px;
    }

    /* Tarjetas de Partidos (Claras y Modernas estilo Premier / SofaScore) */
    .match-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #10b981;
        border-radius: 14px;
        padding: 16px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        transition: transform 0.15s ease;
    }
    .match-card-finished {
        border-left: 6px solid #2563eb;
    }
    .match-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #e2e8f0;
    }
    .pill-cancha {
        background: #ecfdf5;
        color: #047857;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
    }
    .pill-fase {
        background: #eff6ff;
        color: #1d4ed8;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
    }
    .match-center {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.15rem;
        font-weight: 800;
        color: #0f172a;
    }
    .team-box {
        width: 40%;
        color: #0f172a;
    }
    .team-right {
        text-align: right;
    }
    .score-pill {
        background: #1e293b;
        color: #ffffff !important;
        padding: 8px 20px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.2rem;
        min-width: 95px;
        text-align: center;
        box-shadow: 0 3px 8px rgba(30, 41, 59, 0.2);
    }
    .vs-pill {
        background: #fef3c7;
        color: #b45309 !important;
        padding: 6px 16px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 0.95rem;
        border: 1px solid #fde68a;
    }

    /* Tarjetas de Estadísticas Rápidas */
    .stat-mini {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #10b981;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .stat-mini h3 {
        margin: 0;
        font-size: 1.7rem;
        color: #059669 !important;
    }
    .stat-mini p {
        margin: 2px 0 0 0;
        font-size: 0.85rem;
        color: #64748b !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <div>
        <h1>⚽ Plataforma Oficial de Torneos</h1>
        <p>Gestión Deportiva en Vivo • Series Infantiles y Juveniles</p>
    </div>
    <div class="hero-badge">
        📍 SEDES OFICIALES<br>Angol • Máfil • Valdivia
    </div>
</div>
""", unsafe_allow_html=True)

# 2. BASE DE DATOS SQLITE (USO DE ROWID PARA BORRADO INDIVIDUAL SEGURO)
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
    return pd.read_sql(f"SELECT rowid AS row_id, * FROM {nombre_tabla}", conn)

df_config = cargar_tabla("Configuracion")
df_equipos = cargar_tabla("Equipos")
df_jugadores = cargar_tabla("Jugadores")
df_partidos = cargar_tabla("Partidos")

# Catálogo completo de categorías (2010 a 2019: bisiestas, alternas e individuales)
CATALOGO_CATEGORIAS = [
    "2018/2019", "2017/2018", "2016/2017", "2015/2016", 
    "2014/2015", "2013/2014", "2012/2013", "2011/2012", "2010/2011",
    "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011"
]

# Cálculo automático de Tabla de Posiciones
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
            "Club / Equipo": eq, "PTS": pts, "PJ": pj, "PG": pg, 
            "PE": pe, "PP": pp, "GF": gf, "GC": gc, "DG": dg
        })
    df_t = pd.DataFrame(tabla)
    if not df_t.empty:
        df_t = df_t.sort_values(by=["PTS", "DG", "GF"], ascending=[False, False, False]).reset_index(drop=True)
        df_t.index = df_t.index + 1
    return df_t

# 3. MENÚ LATERAL
st.sidebar.markdown("### 🧭 Navegación Principal")
menu = st.sidebar.radio(
    "Ir a:", 
    ["🏟️ Lobby del Torneo (Público)", "📝 Portal Profesores (Planillas)", "⚙️ Panel Staff (Administración)"]
)
st.sidebar.divider()
st.sidebar.markdown(f"""
**📊 Resumen del Sistema:**
- **Categorías activas:** {len(df_config)}
- **Clubes inscritos:** {len(df_equipos)}
- **Jugadores en nómina:** {len(df_jugadores)}
- **Partidos en fixture:** {len(df_partidos)}
""")

# ==========================================
# MÓDULO 1: LOBBY PÚBLICO
# ==========================================
if menu == "🏟️ Lobby del Torneo (Público)":
    if not df_config.empty:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            sedes_disponibles = ['Angol', 'Máfil', 'Valdivia']
            sede_sel = st.selectbox("📍 1. Selecciona la Sede:", sedes_disponibles)
            
        copas_sede = df_config[df_config['nombre_copa'].str.contains(sede_sel, case=False, na=False)]
        
        if not copas_sede.empty:
            with col_f2:
                copa_sel = st.selectbox("🏆 2. Selecciona el Torneo:", copas_sede['nombre_copa'].unique())
            
            cats_copa = df_config[df_config['nombre_copa'] == copa_sel]
            with col_f3:
                cat_sel = st.selectbox("👟 3. Categoría (Año Nacimiento):", cats_copa['categoria'].unique())
        st.markdown('</div>', unsafe_allow_html=True)
        
        if not copas_sede.empty:
            formato_actual = cats_copa[cats_copa['categoria'] == cat_sel]['formato'].values[0]
            eq_cat = df_equipos[(df_equipos['copa'] == copa_sel) & (df_equipos['categoria'] == cat_sel)]
            part_cat = df_partidos[(df_partidos['copa'] == copa_sel) & (df_partidos['categoria'] == cat_sel)]
            jug_cat_all = df_jugadores[(df_jugadores['copa'] == copa_sel) & (df_jugadores['categoria'] == cat_sel)]

            # Indicadores rápidos de la categoría
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f'<div class="stat-mini"><h3>{formato_actual}</h3><p>Formato de Serie</p></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="stat-mini"><h3>{len(eq_cat)}</h3><p>Clubes Inscritos</p></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="stat-mini"><h3>{len(part_cat)}</h3><p>Partidos Programados</p></div>', unsafe_allow_html=True)
            with m4:
                goles_totales = int(jug_cat_all['goles'].sum()) if not jug_cat_all.empty else 0
                st.markdown(f'<div class="stat-mini"><h3>{goles_totales} ⚽</h3><p>Goles Anotados</p></div>', unsafe_allow_html=True)

            st.write("")
            tab_fix, tab_pos, tab_gol, tab_plan = st.tabs([
                "📅 Fixture y Marcadores", 
                "📊 Tabla de Posiciones", 
                "🥇 Goleadores", 
                "🛡️ Planteles Oficiales"
            ])
            
            with tab_fix:
                if not part_cat.empty:
                    for _, part in part_cat.iterrows():
                        es_fin = part['estado'] == "Finalizado"
                        clase_extra = "match-card-finished" if es_fin else ""
                        if es_fin:
                            centro_html = f'<div class="score-pill">{part["goles_local"]} - {part["goles_visita"]}</div>'
                            est_txt = "✅ FINALIZADO"
                        else:
                            centro_html = '<div class="vs-pill">VS</div>'
                            est_txt = "⏳ POR JUGAR"
                            
                        st.markdown(f"""
                        <div class="match-card {clase_extra}">
                            <div class="match-top">
                                <span class="pill-cancha">🕒 {part['hora']} • 📍 {part['cancha']}</span>
                                <span class="pill-fase">🏆 {part['fase']} • {est_txt}</span>
                            </div>
                            <div class="match-center">
                                <div class="team-box">{part['equipo_local']}</div>
                                {centro_html}
                                <div class="team-box team-right">{part['equipo_visita']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Aún no hay partidos programados en esta categoría.")
                    
            with tab_pos:
                if not eq_cat.empty:
                    df_pos = calcular_posiciones(eq_cat, part_cat)
                    if formato_actual == "Grupos":
                        for g in sorted(df_pos['Grupo'].unique()):
                            st.markdown(f"#### 🟢 Grupo {g}")
                            df_g = df_pos[df_pos['Grupo'] == g].drop(columns=['Grupo']).reset_index(drop=True)
                            df_g.index = df_g.index + 1
                            st.dataframe(df_g, use_container_width=True)
                    else:
                        st.markdown("#### 🏆 Tabla General (Formato Liga)")
                        st.dataframe(df_pos.drop(columns=['Grupo']), use_container_width=True)
                else:
                    st.info("No hay equipos inscritos en esta categoría todavía.")
                    
            with tab_gol:
                goleadores = jug_cat_all[jug_cat_all['goles'] > 0].copy()
                if not goleadores.empty:
                    goleadores = goleadores.sort_values(by="goles", ascending=False).reset_index(drop=True)
                    goleadores.index = goleadores.index + 1
                    goleadores['Camiseta'] = goleadores['dorsal'].apply(lambda x: f"#{int(x)}" if pd.notnull(x) and int(x) > 0 else "S/N")
                    st.dataframe(
                        goleadores[['nombre_jugador', 'equipo', 'Camiseta', 'goles']].rename(columns={
                            'nombre_jugador': 'Jugador',
                            'equipo': 'Club / Escuela',
                            'goles': 'Goles ⚽'
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("Aún no se registran goleadores en esta categoría.")
                    
            with tab_plan:
                if not eq_cat.empty:
                    club_ver = st.selectbox("Selecciona el Club:", eq_cat['nombre_equipo'].unique())
                    nomina = jug_cat_all[jug_cat_all['equipo'] == club_ver].copy()
                    if not nomina.empty:
                        nomina['Dorsal_Txt'] = nomina['dorsal'].apply(lambda x: f"#{int(x)}" if pd.notnull(x) and int(x) > 0 else "Sin asignar")
                        st.dataframe(
                            nomina[['Dorsal_Txt', 'nombre_jugador', 'goles']].rename(columns={
                                'Dorsal_Txt': 'N° Camiseta',
                                'nombre_jugador': 'Nombre del Jugador',
                                'goles': 'Goles'
                            }),
                            hide_index=True, use_container_width=True
                        )
                    else:
                        st.info("Este club aún no ha subido su planilla de jugadores.")
                else:
                    st.info("No hay clubes inscritos.")
        else:
            st.info(f"No hay torneos creados en la sede {sede_sel}.")
    else:
        st.info("Aún no hay torneos activos. Ve al 'Panel Staff (Administración)' para crear el primero.")

# ==========================================
# MÓDULO 2: PORTAL PROFESORES (PLANILLAS DINÁMICAS)
# ==========================================
elif menu == "📝 Portal Profesores (Planillas)":
    st.subheader("📝 Gestión Dinámica de Plantillas y Dorsales")
    st.write("Inscribe jugadores rápidamente sin necesidad de dorsal obligatorio, o edita nombres, dorsales y elimina errores directamente en la tabla.")
    
    if not df_equipos.empty:
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            copa_dt = st.selectbox("1. Torneo:", df_equipos['copa'].dropna().unique())
        with col_p2:
            cats_dt = df_equipos[df_equipos['copa'] == copa_dt]['categoria'].dropna().unique()
            cat_dt = st.selectbox("2. Categoría:", cats_dt)
        with col_p3:
            eqs_dt = df_equipos[(df_equipos['copa'] == copa_dt) & (df_equipos['categoria'] == cat_dt)]['nombre_equipo'].dropna().unique()
            equipo_dt = st.selectbox("3. Club / Academia:", eqs_dt) if len(eqs_dt) > 0 else None
            
        if equipo_dt:
            st.divider()
            col_izq, col_der = st.columns([1, 1.5])
            
            with col_izq:
                st.markdown(f"#### ➕ Inscribir Jugadores en **{equipo_dt}**")
                tab_uno, tab_lote = st.tabs(["👤 Por Jugador", "📋 Carga Rápida (Varios)"])
                
                with tab_uno:
                    with st.form("form_ingresar_jugador", clear_on_submit=True):
                        nombre_jugador = st.text_input("Nombre y Apellido *")
                        dorsal_jugador = st.number_input("Dorsal (Opcional: deja 0 si no tiene)", min_value=0, max_value=99, value=0)
                        if st.form_submit_button("➕ Agregar a la Planilla"):
                            if nombre_jugador.strip():
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO Jugadores (copa, categoria, equipo, nombre_jugador, dorsal, goles) VALUES (?, ?, ?, ?, ?, 0)", 
                                    (copa_dt, cat_dt, equipo_dt, nombre_jugador.strip(), int(dorsal_jugador))
                                )
                                conn.commit()
                                st.success(f"¡{nombre_jugador} agregado!")
                                st.rerun()
                                
                with tab_lote:
                    st.caption("Pega una lista de nombres (uno por línea) para inscribir a todo el plantel de una vez sin dorsal:")
                    lista_nombres = st.text_area("Lista de Jugadores (1 por línea):", height=130, placeholder="Mateo González\nLucas Muñoz\nBenjamín Soto")
                    if st.button("🚀 Cargar Lista Completa"):
                        lineas = [n.strip() for n in lista_nombres.split("\n") if n.strip()]
                        if lineas:
                            cursor = conn.cursor()
                            for nom in lineas:
                                cursor.execute(
                                    "INSERT INTO Jugadores (copa, categoria, equipo, nombre_jugador, dorsal, goles) VALUES (?, ?, ?, ?, 0, 0)", 
                                    (copa_dt, cat_dt, equipo_dt, nom)
                                )
                            conn.commit()
                            st.success(f"¡{len(lineas)} jugadores inscritos de golpe!")
                            st.rerun()
                        
            with col_der:
                st.markdown(f"#### 👕 Planilla Interactiva — **{equipo_dt}** ({cat_dt})")
                st.caption("Edita el **Nombre** o el **Dorsal** haciendo doble clic, o marca la casilla **🗑️ Borrar** si te equivocaste al ingresar a alguien.")
                
                plantel_actual = df_jugadores[
                    (df_jugadores['copa'] == copa_dt) & 
                    (df_jugadores['categoria'] == cat_dt) & 
                    (df_jugadores['equipo'] == equipo_dt)
                ].copy()
                
                if not plantel_actual.empty:
                    plantel_actual['Borrar'] = False
                    df_editable = st.data_editor(
                        plantel_actual[['row_id', 'nombre_jugador', 'dorsal', 'Borrar']],
                        column_config={
                            "row_id": None,
                            "nombre_jugador": st.column_config.TextColumn("Nombre del Jugador (Editable)"),
                            "dorsal": st.column_config.NumberColumn("N° Camiseta (0 = S/N)", min_value=0, max_value=99, step=1),
                            "Borrar": st.column_config.CheckboxColumn("🗑️ Borrar")
                        },
                        hide_index=True,
                        use_container_width=True,
                        key="editor_planilla_dt"
                    )
                    
                    if st.button("💾 Guardar Cambios en la Planilla", type="primary"):
                        cursor = conn.cursor()
                        borrados = 0
                        for _, fila in df_editable.iterrows():
                            if fila['Borrar']:
                                cursor.execute("DELETE FROM Jugadores WHERE rowid = ?", (int(fila['row_id']),))
                                borrados += 1
                            else:
                                cursor.execute(
                                    "UPDATE Jugadores SET nombre_jugador = ?, dorsal = ? WHERE rowid = ?",
                                    (str(fila['nombre_jugador']).strip(), int(fila['dorsal']) if pd.notnull(fila['dorsal']) else 0, int(fila['row_id']))
                                )
                        conn.commit()
                        st.success(f"¡Planilla actualizada! ({borrados} eliminados)" if borrados else "¡Cambios y dorsales guardados!")
                        st.rerun()
                else:
                    st.info("Este equipo aún no tiene jugadores en su nómina.")
    else:
        st.info("Primero debes inscribir equipos en el Panel Staff.")

# ==========================================
# MÓDULO 3: PANEL STAFF (ADMINISTRACIÓN Y CORRECCIÓN DE ERRORES)
# ==========================================
elif menu == "⚙️ Panel Staff (Administración)":
    st.subheader("⚙️ Consola de Administración y Control de Torneos")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 1. Crear Torneo y Categorías", 
        "🛡️ 2. Clubes y Grupos", 
        "📅 3. Fixture y Horarios", 
        "⚽ 4. Resultados y Goles", 
        "🛠️ 5. Corregir Errores y Respaldos"
    ])
    
    # TAB 1: CREACIÓN DINÁMICA DE TORNEOS (TODAS LAS CATEGORÍAS 2010 A 2019)
    with tab1:
        st.markdown("#### ✨ Creador Dinámico de Torneos y Series (2010 a 2019)")
        st.write("Elige la sede, ponle nombre al campeonato y selecciona todas las categorías que necesites en un solo paso.")
        
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            sede_input = st.selectbox("📍 Sede / Ciudad", ["Angol", "Máfil", "Valdivia"])
        with col_c2:
            nombre_personalizado = st.text_input("🏆 Nombre de la Copa (ej: Mafil Cup Verano, Copa Angol)", placeholder="Ej: Mafil Cup 2026")
            
        nombre_copa_final = f"{sede_input} - {nombre_personalizado.strip()}" if nombre_personalizado.strip() else ""
        
        st.markdown("##### 1. Selecciona las categorías por año de nacimiento:")
        cats_seleccionadas = st.multiselect(
            "Puedes elegir categorías combinadas (ej. 2010/2011 o 2011/2012) o por año individual (2011 a 2019):",
            options=CATALOGO_CATEGORIAS,
            default=["2018/2019", "2016/2017", "2014/2015", "2012/2013", "2010/2011"]
        )
        
        cat_extra_input = st.text_input("➕ ¿Necesitas otra categoría especial? Escríbela separada por comas (opcional, ej: Sub-20, 2009/2010, Femenino):")
        
        lista_final_cats = list(cats_seleccionadas)
        if cat_extra_input.strip():
            extras = [x.strip() for x in cat_extra_input.split(",") if x.strip()]
            for ex in extras:
                if ex not in lista_final_cats:
                    lista_final_cats.append(ex)
                    
        if lista_final_cats:
            st.markdown("##### 2. Define el formato (Grupos o Liga) para cada categoría seleccionada:")
            df_pre_cats = pd.DataFrame({
                "Categoría": lista_final_cats,
                "Formato de Competencia": ["Grupos"] * len(lista_final_cats)
            })
            
            df_cats_editadas = st.data_editor(
                df_pre_cats,
                column_config={
                    "Categoría": st.column_config.TextColumn("Categoría (Años)", disabled=True),
                    "Formato de Competencia": st.column_config.SelectboxColumn(
                        "Formato (Haz clic para cambiar entre Grupos o Liga)",
                        options=["Grupos", "Liga"],
                        required=True
                    )
                },
                hide_index=True,
                use_container_width=True,
                key="editor_formatos_creacion"
            )
            
            if st.button("🚀 Guardar Torneo con todas estas Categorías", type="primary"):
                if nombre_personalizado.strip():
                    cursor = conn.cursor()
                    guardadas = 0
                    for _, fila in df_cats_editadas.iterrows():
                        existe = df_config[
                            (df_config['nombre_copa'] == nombre_copa_final) & 
                            (df_config['categoria'] == fila['Categoría'])
                        ]
                        if existe.empty:
                            cursor.execute(
                                "INSERT INTO Configuracion (sede, nombre_copa, categoria, formato) VALUES (?, ?, ?, ?)",
                                (sede_input, nombre_copa_final, fila['Categoría'], fila['Formato de Competencia'])
                            )
                            guardadas += 1
                    conn.commit()
                    st.success(f"¡Torneo '{nombre_copa_final}' configurado con {guardadas} categorías nuevas!")
                    st.rerun()
                else:
                    st.warning("⚠️ Escribe primero el nombre del torneo arriba.")

    # TAB 2: INSCRIBIR EQUIPOS Y EDITAR/BORRAR EN TABLA
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
                    nombre_equipo = st.text_input("Nombre del Club / Academia (ej: Río Iñaque, Ñublense, Angol City)")
                with col_n2:
                    grupo_eq = st.text_input("Grupo (ej: A, B o vacío si es Liga)")
                if st.form_submit_button("➕ Inscribir Equipo"):
                    if nombre_equipo.strip():
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO Equipos (copa, categoria, grupo, nombre_equipo) VALUES (?, ?, ?, ?)",
                            (copa_eq, categoria_eq, grupo_eq.strip().upper(), nombre_equipo.strip())
                        )
                        conn.commit()
                        st.success(f"¡{nombre_equipo} inscrito en {categoria_eq}!")
                        st.rerun()
                        
            # Tabla editable de equipos inscritos en esta categoría para corregir errores o borrar
            eqs_actuales = df_equipos[(df_equipos['copa'] == copa_eq) & (df_equipos['categoria'] == categoria_eq)].copy()
            if not eqs_actuales.empty:
                st.markdown("##### 🛡️ Equipos inscritos en esta serie (Edita el nombre/grupo o marca 🗑️ para borrar)")
                eqs_actuales['Borrar'] = False
                ed_eqs = st.data_editor(
                    eqs_actuales[['row_id', 'nombre_equipo', 'grupo', 'Borrar']],
                    column_config={
                        "row_id": None,
                        "nombre_equipo": st.column_config.TextColumn("Nombre del Club"),
                        "grupo": st.column_config.TextColumn("Grupo"),
                        "Borrar": st.column_config.CheckboxColumn("🗑️ Borrar Club")
                    },
                    hide_index=True, use_container_width=True, key="ed_equipos_staff"
                )
                if st.button("💾 Guardar Cambios en Clubes"):
                    cursor = conn.cursor()
                    for _, f in ed_eqs.iterrows():
                        if f['Borrar']:
                            cursor.execute("DELETE FROM Equipos WHERE rowid = ?", (int(f['row_id']),))
                        else:
                            cursor.execute(
                                "UPDATE Equipos SET nombre_equipo = ?, grupo = ? WHERE rowid = ?",
                                (str(f['nombre_equipo']).strip(), str(f['grupo']).strip().upper(), int(f['row_id']))
                            )
                    conn.commit()
                    st.success("¡Lista de clubes actualizada!")
                    st.rerun()
        else:
            st.info("Crea primero un torneo en la Pestaña 1.")
            
    # TAB 3: PROGRAMAR FIXTURE Y BORRAR/EDITAR PARTIDOS
    with tab3:
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
                    fase_part = st.selectbox("Fase", ["Fase Regular / Grupos", "Cuartos de Final", "Semifinal", "3er y 4to Lugar", "Final Copa Plata", "Final Copa Oro"])
                with c_p2:
                    cancha_part = st.text_input("Cancha", value="CANCHA 1")
                with c_p3:
                    hora_part = st.text_input("Horario", value="10:00 HRS")
                    
                c_eq1, c_eq2 = st.columns(2)
                with c_eq1:
                    eq_local = st.selectbox("Equipo Local:", opciones_equipos, key="loc_fx")
                with c_eq2:
                    eq_visita = st.selectbox("Equipo Visita:", opciones_equipos, index=min(1, len(opciones_equipos)-1), key="vis_fx")
                    
                if st.form_submit_button("📅 Agregar Partido al Fixture"):
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO Partidos 
                        (copa, categoria, fase, cancha, hora, equipo_local, equipo_visita, goles_local, goles_visita, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 'Programado')''',
                        (copa_fx, cat_fx, fase_part, cancha_part.strip().upper(), hora_part.strip().upper(), eq_local, eq_visita)
                    )
                    conn.commit()
                    st.success(f"Partido agregado: {eq_local} vs {eq_visita}")
                    st.rerun()
                    
            # Tabla para editar horarios/canchas o eliminar un partido mal creado
            part_actuales = df_partidos[(df_partidos['copa'] == copa_fx) & (df_partidos['categoria'] == cat_fx)].copy()
            if not part_actuales.empty:
                st.markdown("##### 📋 Partidos de esta categoría (Puedes corregir cancha/hora o marcar 🗑️ para borrar)")
                part_actuales['Borrar'] = False
                ed_part = st.data_editor(
                    part_actuales[['row_id', 'hora', 'cancha', 'fase', 'equipo_local', 'equipo_visita', 'Borrar']],
                    column_config={
                        "row_id": None,
                        "hora": st.column_config.TextColumn("Hora"),
                        "cancha": st.column_config.TextColumn("Cancha"),
                        "fase": st.column_config.TextColumn("Fase"),
                        "equipo_local": st.column_config.TextColumn("Local"),
                        "equipo_visita": st.column_config.TextColumn("Visita"),
                        "Borrar": st.column_config.CheckboxColumn("🗑️ Borrar")
                    },
                    hide_index=True, use_container_width=True, key="ed_fixture_staff"
                )
                if st.button("💾 Actualizar Fixture / Borrar Seleccionados"):
                    cursor = conn.cursor()
                    for _, f in ed_part.iterrows():
                        if f['Borrar']:
                            cursor.execute("DELETE FROM Partidos WHERE rowid = ?", (int(f['row_id']),))
                        else:
                            cursor.execute(
                                "UPDATE Partidos SET hora=?, cancha=?, fase=?, equipo_local=?, equipo_visita=? WHERE rowid=?",
                                (str(f['hora']), str(f['cancha']), str(f['fase']), str(f['equipo_local']), str(f['equipo_visita']), int(f['row_id']))
                            )
                    conn.commit()
                    st.success("¡Fixture actualizado!")
                    st.rerun()
        else:
            st.info("Inscribe equipos en la Pestaña 2 primero.")
            
    # TAB 4: RESULTADOS, GOLES Y DORSALES EN MESA
    with tab4:
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
                    lambda r: f"[{r['hora']} - {r['cancha']}] {r['equipo_local']} vs {r['equipo_visita']} ({r['estado']})", axis=1
                )
                partido_sel_etiqueta = st.selectbox("Selecciona el Partido:", partidos_disp['Etiqueta'])
                partido_row = partidos_disp[partidos_disp['Etiqueta'] == partido_sel_etiqueta].iloc[0]
                rowid_partido = int(partido_row['row_id'])
                loc_actual = partido_row['equipo_local']
                vis_actual = partido_row['equipo_visita']
                
                col_marcador, col_goles = st.columns([1, 1.3])
                
                with col_marcador:
                    st.markdown("##### 🏁 1. Marcador del Partido")
                    with st.form("form_guardar_resultado"):
                        g_loc = st.number_input(f"Goles {loc_actual}", min_value=0, max_value=30, value=int(partido_row['goles_local']))
                        g_vis = st.number_input(f"Goles {vis_actual}", min_value=0, max_value=30, value=int(partido_row['goles_visita']))
                        est_nuevo = st.selectbox("Estado", ["Finalizado", "Programado"], index=0 if partido_row['estado']=="Finalizado" else 1)
                        
                        if st.form_submit_button("✅ Guardar Marcador Oficial"):
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE Partidos SET goles_local = ?, goles_visita = ?, estado = ? WHERE rowid = ?",
                                (int(g_loc), int(g_vis), est_nuevo, rowid_partido)
                            )
                            conn.commit()
                            st.success("¡Marcador actualizado!")
                            st.rerun()
                            
                with col_goles:
                    st.markdown("##### 👟 2. Dorsales y Goles en Mesa (Edición Directa)")
                    st.caption("Pon o corrige el **Dorsal** antes de jugar, o edita directamente la columna **Goles Totales** de cualquier jugador.")
                    nomina_partido = df_jugadores[
                        (df_jugadores['copa'] == copa_res) & 
                        (df_jugadores['categoria'] == cat_res) & 
                        (df_jugadores['equipo'].isin([loc_actual, vis_actual]))
                    ].copy()
                    
                    if not nomina_partido.empty:
                        editor_mesa = st.data_editor(
                            nomina_partido[['row_id', 'equipo', 'nombre_jugador', 'dorsal', 'goles']],
                            column_config={
                                "row_id": None,
                                "equipo": st.column_config.TextColumn("Equipo", disabled=True),
                                "nombre_jugador": st.column_config.TextColumn("Jugador", disabled=True),
                                "dorsal": st.column_config.NumberColumn("Dorsal (0=S/N)", min_value=0, max_value=99, step=1),
                                "goles": st.column_config.NumberColumn("Goles Totales ⚽", min_value=0, max_value=99, step=1)
                            },
                            hide_index=True, use_container_width=True, key="editor_mesa_goles_dorsales"
                        )
                        if st.button("💾 Guardar Dorsales y Goles de Jugadores", type="primary"):
                            cursor = conn.cursor()
                            for _, fila in editor_mesa.iterrows():
                                cursor.execute(
                                    "UPDATE Jugadores SET dorsal = ?, goles = ? WHERE rowid = ?",
                                    (int(fila['dorsal']) if pd.notnull(fila['dorsal']) else 0, int(fila['goles']) if pd.notnull(fila['goles']) else 0, int(fila['row_id']))
                                )
                            conn.commit()
                            st.success("¡Dorsales y goles actualizados correctamente!")
                            st.rerun()
                    else:
                        st.info("Los equipos de este partido aún no tienen jugadores cargados.")
        else:
            st.info("No hay partidos programados todavía.")
            
    # TAB 5: CORRECCIÓN INDIVIDUAL DE CATEGORÍAS, LIMPIEZA Y RESPALDOS
    with tab5:
        st.markdown("#### 🛠️ 1. Modificar o Borrar Categorías Individuales")
        if not df_config.empty:
            st.caption("Si agregaste una categoría por error o quieres cambiar su formato entre Grupos y Liga, hazlo aquí:")
            df_cfg_edit = df_config.copy()
            df_cfg_edit['Borrar'] = False
            ed_cfg = st.data_editor(
                df_cfg_edit[['row_id', 'sede', 'nombre_copa', 'categoria', 'formato', 'Borrar']],
                column_config={
                    "row_id": None,
                    "sede": st.column_config.TextColumn("Sede", disabled=True),
                    "nombre_copa": st.column_config.TextColumn("Torneo"),
                    "categoria": st.column_config.TextColumn("Categoría"),
                    "formato": st.column_config.SelectboxColumn("Formato", options=["Grupos", "Liga"]),
                    "Borrar": st.column_config.CheckboxColumn("🗑️ Borrar Categoría")
                },
                hide_index=True, use_container_width=True, key="ed_config_individual"
            )
            if st.button("💾 Aplicar Cambios en Categorías"):
                cursor = conn.cursor()
                for _, f in ed_cfg.iterrows():
                    if f['Borrar']:
                        cursor.execute("DELETE FROM Configuracion WHERE rowid = ?", (int(f['row_id']),))
                    else:
                        cursor.execute(
                            "UPDATE Configuracion SET nombre_copa=?, categoria=?, formato=? WHERE rowid=?",
                            (str(f['nombre_copa']).strip(), str(f['categoria']).strip(), str(f['formato']), int(f['row_id']))
                        )
                conn.commit()
                st.success("¡Categorías actualizadas!")
                st.rerun()
        else:
            st.caption("No hay categorías registradas.")
            
        st.divider()
        st.markdown("#### 🧹 2. Borrar un Torneo de Prueba o Vaciar Base de Datos")
        col_limp1, col_limp2 = st.columns(2)
        
        with col_limp1:
            st.write("**Eliminar un Torneo Completo:**")
            if not df_config.empty:
                copa_borrar = st.selectbox("Torneo a eliminar:", df_config['nombre_copa'].unique(), key="del_copa")
                if st.button("🗑️ Borrar Torneo Seleccionado"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Configuracion WHERE nombre_copa = ?", (copa_borrar,))
                    cursor.execute("DELETE FROM Equipos WHERE copa = ?", (copa_borrar,))
                    cursor.execute("DELETE FROM Jugadores WHERE copa = ?", (copa_borrar,))
                    cursor.execute("DELETE FROM Partidos WHERE copa = ?", (copa_borrar,))
                    conn.commit()
                    st.success(f"Torneo '{copa_borrar}' eliminado por completo.")
                    st.rerun()
                    
        with col_limp2:
            st.write("**Formateo Total del Sistema:**")
            confirmar_reset = st.checkbox("Confirmo que deseo borrar TODOS los registros")
            if st.button("⚠️ Vaciar Toda la Base de Datos", type="primary", disabled=not confirmar_reset):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Configuracion")
                cursor.execute("DELETE FROM Equipos")
                cursor.execute("DELETE FROM Jugadores")
                cursor.execute("DELETE FROM Partidos")
                conn.commit()
                st.success("¡Sistema limpio desde cero!")
                st.rerun()

        st.divider()
        st.markdown("#### 📥 3. Descargar Respaldos en Excel (CSV)")
        c_b1, c_b2, c_b3, c_b4 = st.columns(4)
        with c_b1:
            st.download_button("📥 Torneos", data=df_config.drop(columns=['row_id'], errors='ignore').to_csv(index=False).encode('utf-8-sig'), file_name="torneos.csv", mime="text/csv")
        with c_b2:
            st.download_button("📥 Equipos", data=df_equipos.drop(columns=['row_id'], errors='ignore').to_csv(index=False).encode('utf-8-sig'), file_name="equipos.csv", mime="text/csv")
        with c_b3:
            st.download_button("📥 Jugadores", data=df_jugadores.drop(columns=['row_id'], errors='ignore').to_csv(index=False).encode('utf-8-sig'), file_name="jugadores.csv", mime="text/csv")
        with c_b4:
            st.download_button("📥 Partidos", data=df_partidos.drop(columns=['row_id'], errors='ignore').to_csv(index=False).encode('utf-8-sig'), file_name="partidos.csv", mime="text/csv")
