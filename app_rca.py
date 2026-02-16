import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------
st.set_page_config(page_title="RCA AVERIAS CRITICAS", layout="wide")

# Lista MAESTRA de todas las columnas posibles (Shared + Diag + Conf)
COLUMNAS_MAESTRAS = [
    "ID", "Fecha", "Hora", "Tipo", "TrabajadoPor", "NumeroServicio", 
    "NumeroCaso3", "Producto", "StatusServicio", "Distrito", "Sintoma", 
    "Tecnologia", "EnviadoADistrito", "Comentario",
    # Exclusivos Diagnóstico
    "ParametrosLinea", "CerradoInterno", "CausaCierreInterno", 
    "SintomaCierreInterno", "SolucionCierreInterno", "GrupoResponsable", 
    "SatisfaccionCPAF", "Herramientas", 
    # Exclusivos Confirmación
    "CausaAveria", "AccionTecnicaRealizada", "ConversacionCliente", 
    "OportunidadCaso", "AmeritabanCriticos", "RelacionanCasos", 
    "SatisfaccionTecnico", "RespuestaTecnicaCompleta"
]

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%); }
    h1 { color: #E30613; text-align: center; }
    div[data-testid="stMetricValue"] { color: #E30613; font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CONEXIÓN GOOGLE SHEETS
# ---------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Leemos la hoja
        df = conn.read(ttl=5)
        # Aseguramos que tenga todas las columnas maestras aunque la hoja esté vacía
        for col in COLUMNAS_MAESTRAS:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=COLUMNAS_MAESTRAS)

def guardar_registro(nuevo_df):
    try:
        conn.update(data=nuevo_df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

df = cargar_datos()

# ---------------------------------------------------------
# 3. INTERFAZ
# ---------------------------------------------------------
st.title("RCA AVERIAS CRITICAS 📡")

tab1, tab2, tab3 = st.tabs(["📝 Nuevo Registro", "📋 Histórico", "📊 Dashboard"])

# --- PESTAÑA 1: FORMULARIO DINÁMICO ---
with tab1:
    tipo_proceso = st.radio("Seleccione Proceso:", ["Diagnóstico", "Confirmación"], horizontal=True)

    with st.form("main_form", clear_on_submit=True):
        st.subheader(f"Datos de {tipo_proceso}")
        
        # CAMPOS COMUNES (Siempre aparecen)
        c1, c2, c3 = st.columns(3)
        trabajado_por = c1.selectbox("Trabajado por", ["Dariel Peña", "Jorge Hurtado", "Raquel Rodríguez", "Jan Carlos"])
        num_servicio = c2.text_input("Número Servicio")
        num_caso3 = c3.text_input("Número Caso 3")
        
        c4, c5, c6 = st.columns(3)
        producto = c4.selectbox("Producto", ["INTERNET", "IPTV", "DTH", "VOIP", "OTT"])
        distrito = c5.selectbox("Distrito", ["METRO 1", "METRO 2", "METRO 3", "ESTE", "NORTE", "SUR"])
        sintoma = c6.selectbox("Síntoma", ["NO NAVEGA", "LENTITUD", "SIN TONO", "IMAGEN PIXELADA", "MODEM ROJO"]) # Pon tu lista completa aquí
        
        c7, c8 = st.columns(2)
        tecnologia = c7.selectbox("Tecnología", ["FIBRA", "COBRE", "SATELITAL"])
        enviado = c8.selectbox("Enviado a Distrito", ["SI", "NO"])

        # VARIABLES PARA CAMPOS ESPECÍFICOS (Se llenan según el if)
        datos_especificos = {} 

        # --- LÓGICA CONDICIONAL ---
        if tipo_proceso == "Diagnóstico":
            st.divider()
            st.markdown("### 🔬 Detalles de Diagnóstico")
            col_d1, col_d2 = st.columns(2)
            parametros = col_d1.selectbox("Parámetros de Línea", ["Correctos", "Incorrectos"])
            cerrado_int = col_d2.selectbox("Cerrado Interno", ["SI", "NO"])
            
            herramientas = st.multiselect("Herramientas", ["KUNAI", "SACS", "NMIS", "ORION", "SMART WIFI"])
            tools_str = ", ".join(herramientas)
            
            resp_tecnica = st.text_area("Respuesta Técnica Completa")
            comentario = st.text_area("Comentario Adicional")

            # Guardamos en el diccionario temporal
            datos_especificos = {
                "ParametrosLinea": parametros,
                "CerradoInterno": cerrado_int,
                "Herramientas": tools_str,
                "RespuestaTecnicaCompleta": resp_tecnica,
                "Comentario": comentario
            }

        else: # Confirmación
            st.divider()
            st.markdown("### ✅ Detalles de Confirmación")
            causa = st.text_area("Causa de la Avería")
            accion = st.text_area("Acción Técnica Realizada")
            conversacion = st.selectbox("Conversación Cliente", ["CONFIRMADO SOLUCIONADO", "CONFIRMADO FALLA", "NO CONTACTADO"])
            
            col_c1, col_c2 = st.columns(2)
            amerita = col_c1.selectbox("¿Debió ser crítico?", ["SI", "NO"])
            relacion = col_c2.selectbox("¿Se relacionan los 3 casos?", ["SI", "NO"])
            
            comentario = st.text_area("Comentario Adicional")

            # Guardamos en el diccionario temporal
            datos_especificos = {
                "CausaAveria": causa,
                "AccionTecnicaRealizada": accion,
                "ConversacionCliente": conversacion,
                "AmeritabanCriticos": amerita,
                "RelacionanCasos": relacion,
                "Comentario": comentario
            }

        # --- BOTÓN DE GUARDADO ---
        submitted = st.form_submit_button(f"💾 Guardar {tipo_proceso}")
        
        if submitted:
            # 1. Crear un diccionario con TODAS las columnas vacías por defecto
            registro_final = {col: "" for col in COLUMNAS_MAESTRAS}
            
            # 2. Llenar los datos comunes
            registro_final.update({
                "ID": str(datetime.now().timestamp()),
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "Tipo": tipo_proceso,
                "TrabajadoPor": trabajado_por,
                "NumeroServicio": num_servicio,
                "NumeroCaso3": num_caso3,
                "Producto": producto,
                "StatusServicio": "Activo",
                "Distrito": distrito,
                "Sintoma": sintoma,
                "Tecnologia": tecnologia,
                "EnviadoADistrito": enviado
            })
            
            # 3. Llenar los datos específicos (sobreescribiendo los vacíos)
            registro_final.update(datos_especificos)
            
            # 4. Crear DataFrame y Guardar
            nueva_fila = pd.DataFrame([registro_final])
            df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
            
            if guardar_registro(df_actualizado):
                st.success("✅ Registro guardado en la Sábana Maestra")
                st.rerun()

# --- PESTAÑA 2: HISTÓRICO ---
with tab2:
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Descargar Excel", df.to_csv().encode("utf-8"), "rca_data.csv")

# --- PESTAÑA 3: DASHBOARD ---
with tab3:
    if not df.empty:
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Casos", len(df))
        k2.metric("Diagnósticos", len(df[df["Tipo"]=="Diagnóstico"]))
        k3.metric("Confirmaciones", len(df[df["Tipo"]=="Confirmación"]))
        
        c1, c2 = st.columns(2)
        # Gráfico que usa datos comunes (funciona para ambos)
        fig_prod = px.bar(df, x="Producto", color="Tipo", title="Casos por Producto")
        c1.plotly_chart(fig_prod, use_container_width=True)
        
        # Gráfico que usa datos comunes
        fig_dist = px.pie(df, names="Distrito", title="Distribución por Distrito")
        c2.plotly_chart(fig_dist, use_container_width=True)
        
        # Gráfico específico (Solo filtra filas que tengan datos)
        st.subheader("Causas de Avería (Solo Confirmaciones)")
        df_conf = df[df["Tipo"]=="Confirmación"]
        if not df_conf.empty:
            fig_causa = px.bar(df_conf, y="CausaAveria", title="Top Causas")
            st.plotly_chart(fig_causa, use_container_width=True)
