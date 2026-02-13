import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(
    page_title="RCA AVERIAS CRITICAS",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS idénticos a tu HTML (Rojo y Gris)
st.markdown("""
    <style>
    /* Colores Globales */
    :root { --primary: #E30613; }
    .stApp { background: linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%); }
    
    /* Header parecido al HTML */
    .header-container {
        background: white; padding: 20px; border-radius: 16px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.08); margin-bottom: 20px;
        text-align: center; border-bottom: 4px solid #E30613;
    }
    .header-title { color: #E30613; font-size: 24px; font-weight: bold; margin: 0; }
    .header-subtitle { color: #6B7280; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
    
    /* KPIs */
    div[data-testid="stMetric"] {
        background-color: white; border: 1px solid #e0e0e0;
        padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] { color: #6B7280; font-size: 12px; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #E30613; font-size: 24px; }
    
    /* Botones */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS (Simulada en Memoria) ---
if 'df_registros' not in st.session_state:
    # Definimos las columnas exactas de tu sistema
    st.session_state.df_registros = pd.DataFrame(columns=[
        "ID", "Fecha", "Hora", "Tipo", "TrabajadoPor", "NumeroServicio", "NumeroCaso3",
        "Producto", "StatusServicio", "Distrito", "Sintoma", "Tecnologia",
        "ParametrosLinea", "EnviadoADistrito", "CerradoInterno", "CausaAveriaCierreInterno",
        "SintomaCierreInterno", "SolucionCierreInterno", "AmeritabanCriticos", 
        "RelacionanCasos", "SatisfaccionTecnico", "GrupoResponsable", "SatisfaccionCPAF",
        "RespuestaTecnicaCompleta", "Herramientas", "Comentario", 
        "CausaAveria", "AccionTecnicaRealizada", "ConversacionCliente", "OportunidadCaso"
    ])

# --- LISTAS Y CATÁLOGOS (Copiados de tu HTML) ---
SINTOMAS = sorted([
"NO PUEDO ESCUCHAR/NO ME ESCUCHAN", "FALLA IMAGEN", "MODEM/ONT-NO SINCRONIZADO", "STB NO ENCIENDE",
"NO ME DA TONO", "CONTROL REMOTO DESCONFIGURADO", "CABLE EN EL SUELO O CORTADO", "RUIDO/CRUCE/SE CORTAN LLAMADAS",
"NO RECIBE/NO SALEN LLAMADAS", "INTERMITENCIA", "MODEM/ONT-INTERMITENCIA WIFI", "LENTITUD-BIEN CONFIGURADO",
"NO NAVEGACIÓN/CON IP", "MINIHEADEND DTH", "NO RECIBE LLAMADAS", "TODOS LOS CANALES SIN SENAL",
"NO NAVEGACION-NO IP", "MODEM/ONT-NO NAVEGA WIFI", "NO SENAL-CON IP DE VIDEO", "FALLA DE VIDEO",
"STB CARGANDO", "ALGUNOS CANALES SIN SENAL", "MODEM / ONT AVERIADO", "SMART CARD NO VINCULADO",
"MENSAJE DE SUSPENSION", "TODOS LOS CANALES SIN SEÑAL", "LENTITUD-MAL CONFIGURADO", "STB AVERIADO",
"EQUIPO MESH-NO CONECTA O NO NAVEGA", "FALLA STB FISICO O DE ACTUALIZACION", "NO NAVEGA/INTERMITENCIA REPETIDOR WIFI",
"INCONVENIENTE CONTENIDO", "STB  SE VISUALIZA, NO SE ESCUCHA", "EXTENSIONES", "CALLER ID",
"PARÁBOLA MOVIDA/DESPRENDIDA", "STB O TV DESCONFIGURADO", "NO RECIBE LLAMADAS NUMEROS ESPECIFICOS",
"CONFIGURACION PERFIL", "NO LE HAN RECONECTADO", "STB SE ESCUCHA, NO SE VISUALIZA", "NO SALEN LLAMADAS LDN",
"FALLA EN CANAL ESPECÍFICO", "STB NO CONECTADO A INTERNET", "DESVÍO LLAMADA", "NO SENAL-SIN IP DE VIDEO",
"STB-PIXELACION O FRISADO", "EQUIPO MESH-INTERMITENCIA", "SMART CARD EXPIRADO", "ERROR GRABACION",
"VINCULACION DISPOSITIVO", "NO SEÑAL-CANAL ESPECÍFICO", "FALLA DE AUDIO", "STB NO SE ESCUCHA, SE VISUALIZA",
"INTERMITENCIA DEL SERVICIO", "PIN ACCESO 0 Y 1", "INTERFERENCIA", "IMAGEN PIXCELADA", "SMART CARD REMOVIDO",
"T1 SIN SERVICIO", "PIN PROTECCION", "SMART CARD INVALIDO", "NO SALEN LLAMADAS LDI", "CAMBIO DE CORREO",
"SMART CARD MUDO", "LLAMADA EN CONFERENCIA", "MODEM /ONT AVERIADO", "TELEFONO PRIVADO", "REPETIDOR WIFI NO ENCIENDE",
"LENTITUD", "EQUIPO MESH-LENTITUD", "EQUIPO MESH-AVERIADO/NO FUNCIONA", "CANAL DE SUSCRIPCIÓN/ADD-ONS OTROS",
"EQUIPO MESH-CONFIGURACION AVANZADA", "EQUIPO MESH-BAJA COBERTURA", "STB-DVR - NO GRABA", "CORREO ERRONEO",
"NO SALEN LLAMADAS", "CABLE DE RED AVERIADO", "DOBLE LÍNEA", "LE ESTAN SALIENDO LLAMADAS A CELULARES",
"FALLA CANALES PREMIUN", "GRABACION NO FUNCIONA", "BUZON DE MENSAJE-SALE MENSAJE ERRONEO",
"SALEN LLAMADAS LD FUERA DE PLAN", "EQUIPO MESH-CAMBIO CREDENCIALES", "PAGO RECHAZADO/PERFIL ENGANCHADO",
"EQUIPO MESH-ERROR DE VINCULACION", "MI NEGOCIO TOTAL INCONVENIENTES VOZ", "BUZON DE MENSAJE-PROB.LLAMADA DESPERTAD",
"STB SOLICITA INICIO DE SESION", "SMART CARD NUNCA VINCULADO", "CONTROL REMOTO AVERIADO", "RETORNO LLAMADAS",
"VISITA TÉCNICA DIAL-UP", "NO INFORMADO", "STB PIDE CONTRATAR PLAN/PAQUETE", "NO HAY ACCESO A SMART CARD",
"BUZON DE MENSAJE-TIENE MENSAJE, SIN TONO", "DIAGNÓSTICO", "BUZON DE MENSAJE-CLAVE NO FUNCIONA",
"PROBLEMA PELÍCULA", "NO LE SALEN LLAMADAS USA/PR", "BUZÓN MENSAJES", "MARCADO ABREVIADO", "ERROR PAUSA EN VIVO",
"PROACTIVO - CORRECCION PARAMETROS LINEA", "PROACTIVO - CORRECCION POTENCIA RX", "VINCULACION DE STB"
])

PRODUCTOS = ["INTERNET", "IPTV", "DTH", "VOIP", "OTT", "PSTN"]
DISTRITOS = ["METRO 1", "METRO 2", "METRO 3", "ESTE", "NORTE 1", "NORTE 2", "SUR"]
TECNOLOGIAS = ["FIBRA", "COBRE", "SATELITAL"]
TRABAJADO_POR = ["Dariel Peña", "Jorge Hurtado", "Raquel Rodríguez", "Jan Carlos"]
GRUPOS = ["AVERIA MAYOR PLANTA EXTERNA", "DISTRITO", "HELP DESK", "MANTENIMIENTO PLANTA EXTERNA", "DIAGNOSTICO", "SOPORTE OS CAMPO", "OTRO"]
HERRAMIENTAS_LIST = ["KUNAI", "SACS", "NMIS", "NETCRACKET", "SISTEMA DE PUERTOS", "ORION", "SMART WIFI", "NCE-FAN"]

# ==========================================
# 2. HEADER Y NAVEGACIÓN
# ==========================================

st.markdown("""
    <div class="header-container">
        <h1 class="header-title">RCA AVERIAS CRITICAS - DIAGNOSTICO Y CONFIRMACION</h1>
        <div class="header-subtitle">CENTRO PROACTIVO DE ANÁLISIS Y FALLAS / GESTIÓN REDUCCIÓN DE AVERÍAS</div>
        <div style="margin-top:5px; font-size:11px; color:#999;">CREADO POR DARIEL A. PEÑA</div>
    </div>
""", unsafe_allow_html=True)

# KPIs Principales en el tope
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
total_recs = len(st.session_state.df_registros)
col_kpi1.metric("Total de Casos", total_recs)

# Navegación Tipo Pestañas
tab_form, tab_hist, tab_dash = st.tabs(["📝 Nuevo Registro", "📋 Histórico y Análisis", "📊 Dashboard Gráfico"])

# ==========================================
# 3. PESTAÑA: FORMULARIOS
# ==========================================
with tab_form:
    st.info("Seleccione el tipo de proceso a registrar:")
    tipo_proceso = st.radio("Tipo de Proceso", ["Diagnóstico", "Confirmación"], horizontal=True)

    with st.form("main_form", clear_on_submit=True):
        st.subheader(f"Formulario de {tipo_proceso}")
        
        # --- CAMPOS COMUNES ---
        c1, c2, c3 = st.columns(3)
        trabajado_por = c1.selectbox("Trabajado por", [""] + TRABAJADO_POR)
        num_servicio = c2.text_input("Número del Servicio")
        num_caso3 = c3.text_input("Número del Caso 3")
        
        c4, c5, c6 = st.columns(3)
        producto = c4.selectbox("Producto", [""] + PRODUCTOS)
        
        # Status con lógica "Otros"
        status_base = c5.selectbox("Status del Servicio", ["", "Activo", "Cancelado", "Suspendido", "Otros"])
        status_final = status_base
        if status_base == "Otros":
            status_otro = c5.text_input("Especifique Status")
            status_final = status_otro if status_otro else "Otros"
            
        distrito = c6.selectbox("Distrito", [""] + DISTRITOS)
        
        # Síntoma (Buscador integrado de Streamlit)
        sintoma = st.selectbox("Síntoma", [""] + SINTOMAS)
        
        c7, c8, c9 = st.columns(3)
        tecnologia = c7.selectbox("Tecnología", [""] + TECNOLOGIAS)
        enviado_distrito = c8.selectbox("Enviado a Distrito", ["", "SI", "NO"])
        
        # Variables específicas por tipo
        datos_adicionales = {}
        
        if tipo_proceso == "Diagnóstico":
            parametros = c9.selectbox("Parámetros de Línea", ["", "Correctos", "Incorrectos"])
            cerrado_int = st.selectbox("Cerrado interno", ["", "SI", "NO"])
            
            st.markdown("---")
            st.markdown("**Cierre Interno**")
            causa_cierre = st.text_area("Causa de la Avería (Cierre Interno)")
            sintoma_cierre = st.text_area("Síntoma de Cierre Interno")
            solucion_cierre = st.text_area("Solución del Cierre Interno")
            
            st.markdown("---")
            cc1, cc2 = st.columns(2)
            amerita = cc1.selectbox("¿Debió ser crítico?", ["", "SI", "NO"])
            relacionan = cc2.selectbox("¿Se relacionan los 3 casos?", ["", "SI", "NO"])
            
            resp_tec_ant = st.text_area("Respuesta Técnica Completa del Caso Anterior")
            grupo_resp = st.selectbox("Grupo Responsable", [""] + GRUPOS)
            satisfaccion = st.selectbox("Satisfacción CPAF", ["", "POSITIVA", "NEGATIVA"])
            
            resp_completa = st.text_area("Respuesta Técnica Completa (Actual)")
            
            # Herramientas (Multiselect funciona mejor que checkboxes individuales)
            tools_sel = st.multiselect("Herramientas Utilizadas", HERRAMIENTAS_LIST + ["OTROS"])
            tools_final = ", ".join(tools_sel)
            if "OTROS" in tools_sel:
                tools_txt = st.text_input("Especifique Otra Herramienta")
                tools_final = tools_final.replace("OTROS", f"OTROS: {tools_txt}")
                
            comentario = st.text_area("Comentarios")
            
            # Guardar datos específicos en diccionario temporal
            datos_adicionales = {
                "ParametrosLinea": parametros, "CerradoInterno": cerrado_int,
                "CausaAveriaCierreInterno": causa_cierre, "SintomaCierreInterno": sintoma_cierre,
                "SolucionCierreInterno": solucion_cierre, "AmeritabanCriticos": amerita,
                "RelacionanCasos": relacionan, "SatisfaccionTecnico": resp_tec_ant, # Mapeo al campo HTML
                "GrupoResponsable": grupo_resp, "SatisfaccionCPAF": satisfaccion,
                "RespuestaTecnicaCompleta": resp_completa, "Herramientas": tools_final,
                "Comentario": comentario
            }

        else: # Confirmación
            st.markdown("---")
            causa_averia = st.text_area("Causa de la Avería")
            accion_realizada = st.text_area("Acción Técnica Realizada")
            resp_completa = st.text_area("Respuesta Técnica Completa")
            
            conv_cliente = st.selectbox("Conversación con Cliente", ["", "CONFIRMADO, AVERÍA SE SOLUCIONÓ", "CONFIRMADO, SIGUE CON AVERÍA", "CERRADO SIN CONFIRMAR", "Otros"])
            if conv_cliente == "Otros":
                conv_txt = st.text_input("Especifique Conversación")
                conv_cliente = conv_txt
                
            oportunidad = st.text_area("¿Dónde estuvo la oportunidad?")
            
            cc1, cc2, cc3 = st.columns(3)
            amerita = cc1.selectbox("¿Debió ser crítico?", ["", "SI", "NO"])
            satisfaccion_tec = cc2.selectbox("Satisfacción Cliente (Técnico)", ["", "POSITIVA", "NEGATIVA"])
            relacionan = cc3.selectbox("¿Se relacionan los 3 casos?", ["", "SI", "NO"])
            
            comentario = st.text_area("Comentarios")
            
            datos_adicionales = {
                "CausaAveria": causa_averia, "AccionTecnicaRealizada": accion_realizada,
                "RespuestaTecnicaCompleta": resp_completa, "ConversacionCliente": conv_cliente,
                "OportunidadCaso": oportunidad, "AmeritabanCriticos": amerita,
                "SatisfaccionTecnico": satisfaccion_tec, "RelacionanCasos": relacionan,
                "Comentario": comentario
            }

        # --- BOTÓN DE GUARDADO ---
        submitted = st.form_submit_button(f"💾 Guardar {tipo_proceso}")
        
        if submitted:
            # Construir registro completo
            nuevo_registro = {
                "ID": str(datetime.now().timestamp()),
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "Tipo": tipo_proceso,
                "TrabajadoPor": trabajado_por,
                "NumeroServicio": num_servicio,
                "NumeroCaso3": num_caso3,
                "Producto": producto,
                "StatusServicio": status_final,
                "Distrito": distrito,
                "Sintoma": sintoma,
                "Tecnologia": tecnologia,
                "EnviadoADistrito": enviado_distrito,
                # ... unir con los datos específicos
                **datos_adicionales
            }
            
            # Asegurar que todas las columnas del DF existan en el nuevo registro (rellenar con vacío)
            for col in st.session_state.df_registros.columns:
                if col not in nuevo_registro:
                    nuevo_registro[col] = ""
            
            # Guardar en Session State
            st.session_state.df_registros = pd.concat(
                [st.session_state.df_registros, pd.DataFrame([nuevo_registro])], 
                ignore_index=True
            )
            st.success("✅ Registro guardado exitosamente.")
            st.rerun()

# ==========================================
# 4. PESTAÑA: HISTÓRICO Y ANÁLISIS
# ==========================================
with tab_hist:
    df = st.session_state.df_registros
    
    # --- FILTROS ---
    with st.expander("🔎 Filtros y Opciones", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        filtro_tipo = f1.multiselect("Tipo", df["Tipo"].unique(), default=df["Tipo"].unique())
        filtro_distrito = f2.multiselect("Distrito", df["Distrito"].unique())
        filtro_prod = f3.multiselect("Producto", df["Producto"].unique())
        filtro_caso = f4.text_input("Buscar Caso 3")
        
        # Aplicar filtros
        df_filtered = df.copy()
        if filtro_tipo: df_filtered = df_filtered[df_filtered["Tipo"].isin(filtro_tipo)]
        if filtro_distrito: df_filtered = df_filtered[df_filtered["Distrito"].isin(filtro_distrito)]
        if filtro_prod: df_filtered = df_filtered[df_filtered["Producto"].isin(filtro_prod)]
        if filtro_caso: df_filtered = df_filtered[df_filtered["NumeroCaso3"].str.contains(filtro_caso, case=False, na=False)]

    # --- ACCIONES DE IMPORT/EXPORT ---
    col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
    
    # Importar Excel
    uploaded_file = col_act1.file_uploader("📥 Importar Excel", type=['xlsx'])
    if uploaded_file:
        try:
            df_import = pd.read_excel(uploaded_file)
            # Normalizar columnas si es necesario o concatenar directo si coinciden
            # (Simplificado para este ejemplo, asumiendo estructura similar)
            st.session_state.df_registros = pd.concat([st.session_state.df_registros, df_import], ignore_index=True)
            st.success(f"Importados {len(df_import)} registros.")
        except Exception as e:
            st.error(f"Error al importar: {e}")

    # Exportar Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='RCA')
        
    col_act2.download_button(
        label="📤 Exportar Filtrado (Excel)",
        data=buffer.getvalue(),
        file_name=f"RCA_Export_{datetime.now().date()}.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    col_act3.metric("Registros Visibles", len(df_filtered))

    # --- TABLA DE DATOS ---
    st.dataframe(
        df_filtered, 
        column_order=("Fecha", "Hora", "Tipo", "TrabajadoPor", "NumeroCaso3", "Producto", "Distrito", "Sintoma"),
        use_container_width=True,
        hide_index=True
    )
    
    # Botón de borrado (Simulado con checkbox para seleccionar ID sería mejor, pero esto es rápido)
    if not df_filtered.empty:
        id_to_delete = st.selectbox("Seleccione ID para borrar (Temporal)", [""] + list(df_filtered["ID"].unique()))
        if id_to_delete:
            if st.button("🗑️ Eliminar Registro Seleccionado"):
                st.session_state.df_registros = st.session_state.df_registros[st.session_state.df_registros["ID"] != id_to_delete]
                st.success("Borrado.")
                st.rerun()

# ==========================================
# 5. PESTAÑA: DASHBOARD
# ==========================================
with tab_dash:
    if df.empty:
        st.warning("No hay datos para mostrar gráficos.")
    else:
        # Filtros de Dashboard (reutilizamos el DF filtrado de la lógica anterior o creamos nuevos)
        # Para el ejemplo usamos el DF completo, pero podrías añadir filtros de fecha aquí
        
        # --- RESUMEN ANALÍTICO (Lógica de Texto) ---
        df_diag = df[df["Tipo"] == "Diagnóstico"]
        df_conf = df[df["Tipo"] == "Confirmación"]
        
        # Funciones auxiliares para Top Drivers
        def get_top(dataframe, col):
            if dataframe.empty: return "—", 0
            vc = dataframe[col].value_counts()
            return vc.index[0], vc.values[0]

        top_prod_diag, val_prod_diag = get_top(df_diag, "Producto")
        top_dist_diag, val_dist_diag = get_top(df_diag, "Distrito")
        top_sint_diag, val_sint_diag = get_top(df_diag, "Sintoma")
        
        # Visualización tipo Tarjetas (Card)
        st.subheader("Resumen Analítico Visual")
        ra1, ra2, ra3 = st.columns(3)
        ra1.info(f"**Top Producto (Diag):** {top_prod_diag} ({val_prod_diag} casos)")
        ra2.info(f"**Top Distrito (Diag):** {top_dist_diag} ({val_dist_diag} casos)")
        ra3.info(f"**Top Síntoma (Diag):** {top_sint_diag} ({val_sint_diag} casos)")
        
        st.markdown("---")

        # --- GRÁFICOS (Plotly) ---
        
        # 1. Distribución y Donut
        g1, g2 = st.columns(2)
        
        # Line Chart: Casos por Producto (Comparativo)
        prod_counts = df.groupby(["Producto", "Tipo"]).size().reset_index(name="Casos")
        fig_lines = px.line(prod_counts, x="Producto", y="Casos", color="Tipo", markers=True, title="Distribución por Producto")
        fig_lines.update_layout(xaxis_title="Producto", yaxis_title="Volumen")
        g1.plotly_chart(fig_lines, use_container_width=True)
        
        # Donut: Por Cola
        fig_donut = px.pie(df, names="Tipo", title="Volumen Total por Cola", hole=0.6, color_discrete_sequence=['#E30613', '#2C3E50'])
        g2.plotly_chart(fig_donut, use_container_width=True)
        
        # 2. Top Síntomas (Tabla Gráfica)
        st.subheader("TOP 10 Síntomas")
        top_sintomas = df["Sintoma"].value_counts().head(10).reset_index()
        top_sintomas.columns = ["Síntoma", "Total"]
        fig_bar_sint = px.bar(top_sintomas, x="Total", y="Síntoma", orientation='h', title="Síntomas Más Frecuentes", text="Total")
        fig_bar_sint.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_sint, use_container_width=True)
        
        # 3. Tablas de Texto (Análisis de Causa Raíz)
        st.markdown("### 📝 Análisis de Texto (Top Drivers)")
        
        t1, t2 = st.columns(2)
        
        with t1:
            st.markdown("**Top Causas (Confirmación)**")
            if not df_conf.empty:
                top_causas = df_conf["CausaAveria"].value_counts().head(5)
                st.table(top_causas)
            else:
                st.write("Sin datos de confirmación.")
                
        with t2:
            st.markdown("**Top Acciones (Confirmación)**")
            if not df_conf.empty:
                top_acciones = df_conf["AccionTecnicaRealizada"].value_counts().head(5)
                st.table(top_acciones)
            else:
                st.write("Sin datos de confirmación.")

        # 4. Sección Diagnóstico (Gráficos específicos)
        st.markdown("### 🔬 Deep Dive: Diagnóstico")
        d1, d2, d3 = st.columns(3)
        
        if not df_diag.empty:
            fig_amerita = px.pie(df_diag, names="AmeritabanCriticos", title="¿Debió ser crítico?", hole=0.4)
            d1.plotly_chart(fig_amerita, use_container_width=True)
            
            fig_env = px.pie(df_diag, names="EnviadoADistrito", title="Enviado a Distrito", hole=0.4)
            d2.plotly_chart(fig_env, use_container_width=True)
            
            dist_counts = df_diag["Distrito"].value_counts().reset_index()
            fig_dist = px.bar(dist_counts, x="Distrito", y="count", title="Casos por Distrito")
            d3.plotly_chart(fig_dist, use_container_width=True)
