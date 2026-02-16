import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# 1. CONFIGURACIÓN Y ESTILOS
# ---------------------------------------------------------
st.set_page_config(page_title="RCA Averías Críticas", layout="wide", page_icon="📡")

# Colores de la marca (Claro / Tu diseño)
COLOR_PRIMARY = "#E30613"
COLOR_BG = "#F5F7FA"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_BG}; }}
    h1, h2, h3 {{ color: {COLOR_PRIMARY} !important; }}
    div[data-testid="stMetricValue"] {{ color: {COLOR_PRIMARY} !important; font-weight: bold; }}
    .stButton>button {{ background-color: {COLOR_PRIMARY}; color: white; border-radius: 8px; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CATÁLOGOS (Copiados de tu HTML)
# ---------------------------------------------------------
SINTOMAS_LISTA = sorted([
    "NO PUEDO ESCUCHAR/NO ME ESCUCHAN", "FALLA IMAGEN", "MODEM/ONT-NO SINCRONIZADO", "STB NO ENCIENDE",
    "NO ME DA TONO", "CONTROL REMOTO DESCONFIGURADO", "CABLE EN EL SUELO O CORTADO", "RUIDO/CRUCE/SE CORTAN LLAMADAS",
    "NO RECIBE/NO SALEN LLAMADAS", "INTERMITENCIA", "MODEM/ONT-INTERMITENCIA WIFI", "LENTITUD-BIEN CONFIGURADO",
    "NO NAVEGACIÓN/CON IP", "MINIHEADEND DTH", "NO RECIBE LLAMADAS", "TODOS LOS CANALES SIN SENAL",
    "NO NAVEGACION-NO IP", "MODEM/ONT-NO NAVEGA WIFI", "NO SENAL-CON IP DE VIDEO", "FALLA DE VIDEO",
    "STB CARGANDO", "ALGUNOS CANALES SIN SENAL", "MODEM / ONT AVERIADO", "SMART CARD NO VINCULADO",
    "MENSAJE DE SUSPENSION", "TODOS LOS CANALES SIN SEÑAL", "LENTITUD-MAL CONFIGURADO", "STB AVERIADO",
    "EQUIPO MESH-NO CONECTA O NO NAVEGA", "FALLA STB FISICO O DE ACTUALIZACION", "NO NAVEGA/INTERMITENCIA REPETIDOR WIFI",
    "INCONVENIENTE CONTENIDO", "STB SE VISUALIZA, NO SE ESCUCHA", "EXTENSIONES", "CALLER ID",
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
    "LE ESTÁN SALIENDO LLAMADAS A CELULARES", "FALLA CANALES PREMIUN", "GRABACION NO FUNCIONA", "BUZON DE MENSAJE-SALE MENSAJE ERRONEO",
    "SALEN LLAMADAS LD FUERA DE PLAN", "EQUIPO MESH-CAMBIO CREDENCIALES", "PAGO RECHAZADO/PERFIL ENGANCHADO",
    "EQUIPO MESH-ERROR DE VINCULACION", "MI NEGOCIO TOTAL INCONVENIENTES VOZ", "BUZON DE MENSAJE-PROB.LLAMADA DESPERTAD",
    "STB SOLICITA INICIO DE SESION", "SMART CARD NUNCA VINCULADO", "CONTROL REMOTO AVERIADO", "RETORNO LLAMADAS",
    "VISITA TÉCNICA DIAL-UP", "NO INFORMADO", "STB PIDE CONTRATAR PLAN/PAQUETE", "NO HAY ACCESO A SMART CARD",
    "BUZON DE MENSAJE-TIENE MENSAJE, SIN TONO", "DIAGNÓSTICO", "BUZON DE MENSAJE-CLAVE NO FUNCIONA",
    "PROBLEMA PELÍCULA", "NO LE SALEN LLAMADAS USA/PR", "BUZÓN MENSAJES", "MARCADO ABREVIADO", "ERROR PAUSA EN VIVO",
    "PROACTIVO - CORRECCION PARAMETROS LINEA", "PROACTIVO - CORRECCION POTENCIA RX", "VINCULACION DE STB"
])

# Lista Maestra de Columnas para Google Sheets
COLUMNAS_MAESTRAS = [
    "ID", "Fecha", "Hora", "Tipo", "TrabajadoPor", "NumeroServicio", 
    "NumeroCaso3", "Producto", "StatusServicio", "Distrito", "Sintoma", 
    "Tecnologia", "EnviadoADistrito", "Comentario", "AmeritabanCriticos", "RelacionanCasos",
    # Diagnóstico Específico
    "ParametrosLinea", "CerradoInterno", "CausaCierreInterno", 
    "SintomaCierreInterno", "SolucionCierreInterno", "RespuestaTecnicaAnterior", 
    "GrupoResponsable", "SatisfaccionCPAF", "RespuestaTecnicaCompleta", "Herramientas", 
    # Confirmación Específica
    "CausaAveria", "AccionTecnicaRealizada", "ConversacionCliente", 
    "OportunidadCaso", "SatisfaccionTecnico"
]

# ---------------------------------------------------------
# 3. CONEXIÓN A GOOGLE SHEETS
# ---------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df = conn.read(ttl=0) # TTL=0 para que siempre traiga lo fresco
        # Asegurar que existan todas las columnas
        for col in COLUMNAS_MAESTRAS:
            if col not in df.columns:
                df[col] = ""
        # Convertir Fecha a datetime para filtrar
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        return df
    except Exception as e:
        st.error(f"⚠️ Error conectando a la hoja: {e}")
        return pd.DataFrame(columns=COLUMNAS_MAESTRAS)

def guardar_registro(nuevo_df):
    try:
        conn.update(data=nuevo_df)
        st.toast("✅ ¡Registro Guardado en la Nube!", icon="☁️")
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")
        return False

# Carga inicial
df = cargar_datos()

# ---------------------------------------------------------
# 4. INTERFAZ: HEADER
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("RCA AVERIAS CRITICAS")
    st.markdown("**CENTRO PROACTIVO DE ANÁLISIS Y FALLAS / GESTIÓN REDUCCIÓN DE AVERÍAS**")
with col_h2:
    st.metric("Total Casos", len(df))

# Navegación
tab_form, tab_hist, tab_dash = st.tabs(["📝 Nuevo Registro", "📋 Histórico y Análisis", "📊 Dashboard Gráfico"])

# ---------------------------------------------------------
# 5. PESTAÑA 1: FORMULARIOS
# ---------------------------------------------------------
with tab_form:
    tipo_proceso = st.radio("Seleccione Proceso:", ["Diagnóstico", "Confirmación"], horizontal=True)
    
    with st.form("form_entry", clear_on_submit=True):
        st.subheader(f"Formulario de {tipo_proceso}")
        
        # --- CAMPOS COMUNES ---
        c1, c2, c3 = st.columns(3)
        trabajado_por = c1.selectbox("Trabajado por", ["", "Dariel Peña", "Jorge Hurtado", "Raquel Rodríguez", "Jan Carlos"])
        num_servicio = c2.text_input("Número del Servicio")
        num_caso3 = c3.text_input("Número del Caso 3")
        
        c4, c5, c6 = st.columns(3)
        producto = c4.selectbox("Producto", ["", "INTERNET", "IPTV", "DTH", "VOIP", "OTT", "PSTN"])
        
        # Status con "Otros"
        status_sel = c5.selectbox("Status del Servicio", ["", "Activo", "Cancelado", "Suspendido", "Otros"])
        status_final = st.text_input("Especifique Status") if status_sel == "Otros" else status_sel
            
        distrito = c6.selectbox("Distrito", ["", "METRO 1", "METRO 2", "METRO 3", "ESTE", "NORTE 1", "NORTE 2", "SUR"])
        
        # Síntoma
        sintoma = st.selectbox("SÍNTOMA", [""] + SINTOMAS_LISTA)
        
        c7, c8 = st.columns(2)
        tecnologia = c7.selectbox("Tecnología", ["", "FIBRA", "COBRE", "SATELITAL"])
        enviado = c8.selectbox("Enviado a Distrito", ["", "SI", "NO"])

        # --- LÓGICA ESPECÍFICA ---
        datos_extra = {}
        
        if tipo_proceso == "Diagnóstico":
            col_d1, col_d2 = st.columns(2)
            params = col_d1.selectbox("Parámetros de Línea", ["", "Correctos", "Incorrectos"])
            cerrado_int = col_d2.selectbox("Cerrado Interno", ["", "SI", "NO"])
            
            st.markdown("---")
            st.markdown("**Cierre Interno**")
            causa_cierre = st.text_area("Causa de la Avería (Cierre Interno)")
            sintoma_cierre = st.text_area("Síntoma de Cierre Interno")
            sol_cierre = st.text_area("Solución del Cierre Interno")
            
            st.markdown("---")
            k1, k2 = st.columns(2)
            amerita = k1.selectbox("¿Debió ser crítico?", ["", "SI", "NO"])
            relacion = k2.selectbox("¿Se relacionan los 3 casos?", ["", "SI", "NO"])
            
            resp_ant = st.text_area("Respuesta Técnica Completa del Caso Anterior")
            
            grupo_sel = st.selectbox("Grupo Responsable", ["", "AVERIA MAYOR PLANTA EXTERNA", "DISTRITO", "HELP DESK", "MANTENIMIENTO PLANTA EXTERNA", "DIAGNOSTICO", "SOPORTE OS CAMPO", "OTRO"])
            satisf_cpaf = st.selectbox("Satisfacción CPAF", ["", "POSITIVA", "NEGATIVA"])
            
            resp_compl = st.text_area("Respuesta Técnica Completa (Actual)")
            
            # Herramientas
            tools_opts = ["KUNAI", "SACS", "NMIS", "NETCRACKET", "SISTEMA DE PUERTOS", "ORION", "SMART WIFI", "NCE-FAN", "OTROS"]
            tools_sel = st.multiselect("Herramientas Utilizadas", tools_opts)
            tools_str = ", ".join(tools_sel)
            if "OTROS" in tools_sel:
                otro_tool = st.text_input("Especifique Otra Herramienta")
                tools_str = tools_str.replace("OTROS", f"OTROS: {otro_tool}")
            
            comentario = st.text_area("Comentario")
            
            datos_extra = {
                "ParametrosLinea": params, "CerradoInterno": cerrado_int,
                "CausaCierreInterno": causa_cierre, "SintomaCierreInterno": sintoma_cierre,
                "SolucionCierreInterno": sol_cierre, "RespuestaTecnicaAnterior": resp_ant,
                "GrupoResponsable": grupo_sel, "SatisfaccionCPAF": satisf_cpaf,
                "RespuestaTecnicaCompleta": resp_compl, "Herramientas": tools_str,
                "AmeritabanCriticos": amerita, "RelacionanCasos": relacion, "Comentario": comentario
            }

        else: # Confirmación
            st.markdown("---")
            causa_av = st.text_area("CAUSA DE LA AVERÍA")
            accion = st.text_area("ACCIÓN TÉCNICA REALIZADA")
            resp_compl = st.text_area("Respuesta técnica completa")
            
            conv_opts = ["", "CONFIRMADO, AVERÍA SE SOLUCIONÓ", "CONFIRMADO, SIGUE CON AVERÍA", "CERRADO SIN CONFIRMAR", "Otros"]
            conv_sel = st.selectbox("Conversación con Cliente", conv_opts)
            conv_final = st.text_input("Especifique Conversación") if conv_sel == "Otros" else conv_sel
            
            oportunidad = st.text_area("¿Dónde estuvo la oportunidad?")
            
            kc1, kc2, kc3 = st.columns(3)
            amerita = kc1.selectbox("¿Debió ser crítico?", ["", "SI", "NO"])
            relacion = kc2.selectbox("¿Se relacionan los 3 casos?", ["", "SI", "NO"])
            satisf_tec = kc3.selectbox("Satisfacción Cliente (Técnico)", ["", "POSITIVA", "NEGATIVA"])
            
            comentario = st.text_area("Comentario")
            
            datos_extra = {
                "CausaAveria": causa_av, "AccionTecnicaRealizada": accion,
                "RespuestaTecnicaCompleta": resp_compl, "ConversacionCliente": conv_final,
                "OportunidadCaso": oportunidad, "AmeritabanCriticos": amerita,
                "RelacionanCasos": relacion, "SatisfaccionTecnico": satisf_tec,
                "Comentario": comentario
            }

        # Guardar
        if st.form_submit_button(f"💾 Guardar {tipo_proceso}"):
            # Construir registro vacío
            nuevo = {col: "" for col in COLUMNAS_MAESTRAS}
            # Llenar comunes
            nuevo.update({
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
                "EnviadoADistrito": enviado
            })
            # Llenar específicos
            nuevo.update(datos_extra)
            
            # Guardar
            df_new = pd.DataFrame([nuevo])
            df_final = pd.concat([df, df_new], ignore_index=True)
            if guardar_registro(df_final):
                st.rerun()

# ---------------------------------------------------------
# 6. PESTAÑA 2: HISTÓRICO
# ---------------------------------------------------------
with tab_hist:
    # KPIs Histórico
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Casos", len(df))
    k2.metric("Diagnósticos", len(df[df['Tipo'] == 'Diagnóstico']))
    k3.metric("Confirmaciones", len(df[df['Tipo'] == 'Confirmación']))
    
    st.divider()
    
    # Filtros
    with st.expander("🔎 Filtros de Búsqueda", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        filtro_tipo = f1.multiselect("Tipo", df['Tipo'].unique())
        filtro_dist = f2.multiselect("Distrito", df['Distrito'].unique())
        filtro_prod = f3.multiselect("Producto", df['Producto'].unique())
        filtro_caso = f4.text_input("Buscar Caso 3")
        
        df_view = df.copy()
        if filtro_tipo: df_view = df_view[df_view['Tipo'].isin(filtro_tipo)]
        if filtro_dist: df_view = df_view[df_view['Distrito'].isin(filtro_dist)]
        if filtro_prod: df_view = df_view[df_view['Producto'].isin(filtro_prod)]
        if filtro_caso: df_view = df_view[df_view['NumeroCaso3'].astype(str).str.contains(filtro_caso, case=False)]
    
    # Tabla
    st.dataframe(df_view, use_container_width=True)
    
    # Botón borrar
    c_del, c_exp = st.columns([1, 4])
    with c_del:
        if not df_view.empty:
            id_borrar = st.selectbox("Seleccionar ID para borrar", [""] + list(df_view['ID'].values))
            if id_borrar and st.button("🗑️ Borrar ID Seleccionado"):
                df_final = df[df['ID'] != id_borrar]
                guardar_registro(df_final)
                st.rerun()

# ---------------------------------------------------------
# 7. PESTAÑA 3: DASHBOARD
# ---------------------------------------------------------
with tab_dash:
    if df.empty:
        st.warning("No hay datos para mostrar.")
    else:
        # Filtros Dashboard
        st.markdown("### 📊 Filtros del Dashboard")
        d1, d2, d3 = st.columns(3)
        dash_dist = d1.multiselect("Distrito (Dash)", df['Distrito'].unique())
        dash_prod = d2.multiselect("Producto (Dash)", df['Producto'].unique())
        dash_cola = d3.selectbox("Cola", ["Todos", "Diagnóstico", "Confirmación"])
        
        df_dash = df.copy()
        if dash_dist: df_dash = df_dash[df_dash['Distrito'].isin(dash_dist)]
        if dash_prod: df_dash = df_dash[df_dash['Producto'].isin(dash_prod)]
        if dash_cola != "Todos": df_dash = df_dash[df_dash['Tipo'] == dash_cola]
        
        # Resumen Analítico
        diag_len = len(df_dash[df_dash['Tipo']=='Diagnóstico'])
        conf_len = len(df_dash[df_dash['Tipo']=='Confirmación'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Analizado", len(df_dash), "100%")
        m2.metric("Diagnóstico", diag_len, f"{(diag_len/len(df_dash)*100):.1f}%" if len(df_dash)>0 else "0%")
        m3.metric("Confirmación", conf_len, f"{(conf_len/len(df_dash)*100):.1f}%" if len(df_dash)>0 else "0%")
        
        st.divider()
        
        # Gráficos Generales
        g1, g2 = st.columns(2)
        
        # Distribución de Casos (Barras)
        casos_prod = df_dash['Producto'].value_counts().reset_index()
        casos_prod.columns = ['Producto', 'Casos']
        fig_bar = px.bar(casos_prod, x='Producto', y='Casos', color='Producto', title="Distribución por Producto")
        fig_bar.update_traces(text=casos_prod['Casos'], textposition='outside')
        g1.plotly_chart(fig_bar, use_container_width=True)
        
        # Donut Total
        fig_donut = px.pie(df_dash, names='Tipo', title="Volumen Total por Cola", hole=0.5, color_discrete_sequence=[COLOR_PRIMARY, "#2C3E50"])
        g2.plotly_chart(fig_donut, use_container_width=True)
        
        # TOP 10 Síntomas
        st.subheader("TOP 10 Síntomas")
        top_sint = df_dash['Sintoma'].value_counts().head(10).reset_index()
        top_sint.columns = ['Síntoma', 'Total']
        fig_sint = px.bar(top_sint, x='Total', y='Síntoma', orientation='h', text='Total', color_discrete_sequence=[COLOR_PRIMARY])
        fig_sint.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_sint, use_container_width=True)
        
        # Sección Específica (Dependiendo del filtro)
        st.divider()
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.markdown("### 🔬 Diagnóstico - Top Drivers")
            df_d = df_dash[df_dash['Tipo']=='Diagnóstico']
            if not df_d.empty:
                # Ameritaban
                fig_am = px.pie(df_d, names='AmeritabanCriticos', title="¿Debió ser crítico?", hole=0.4)
                st.plotly_chart(fig_am, use_container_width=True)
                # Distrito
                dist_d = df_d['Distrito'].value_counts().reset_index()
                fig_dd = px.bar(dist_d, x='Distrito', y='count', title="Casos por Distrito (Diag)")
                st.plotly_chart(fig_dd, use_container_width=True)
                
        with c_right:
            st.markdown("### ✅ Confirmación - Top Drivers")
            df_c = df_dash[df_dash['Tipo']=='Confirmación']
            if not df_c.empty:
                # Top Causas (Tabla gráfica)
                top_causa = df_c['CausaAveria'].value_counts().head(5).reset_index()
                st.table(top_causa.rename(columns={'count':'Cant', 'CausaAveria':'Causa Top'}))
                
                # Relacionan
                fig_rel = px.pie(df_c, names='RelacionanCasos', title="¿Se relacionan los casos?", hole=0.4)
                st.plotly_chart(fig_rel, use_container_width=True)
