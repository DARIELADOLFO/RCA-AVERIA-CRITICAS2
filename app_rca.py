import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la página (Modo Ancho y Título)
st.set_page_config(page_title="RCA Averías Críticas - CPAF", layout="wide")

# Estilo CSS para replicar los colores de tu proyecto original
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button { background-color: #E30613; color: white; border-radius: 8px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    h1 { color: #E30613; font-family: 'Arial'; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE LA SESIÓN (Base de datos temporal en memoria) ---
if 'db_registros' not in st.session_state:
    st.session_state.db_registros = pd.DataFrame(columns=[
        "Fecha", "Hora", "Tipo", "Trabajado Por", "Servicio", "Caso 3", 
        "Producto", "Tecnologia", "Distrito", "Sintoma", "Enviado a Distrito"
    ])

# --- CATÁLOGOS (Basados en tu HTML) ---
SINTOMAS = sorted([
    "NO PUEDO ESCUCHAR/NO ME ESCUCHAN", "FALLA IMAGEN", "MODEM/ONT-NO SINCRONIZADO",
    "INTERMITENCIA", "LENTITUD-BIEN CONFIGURADO", "NO NAVEGACIÓN/CON IP",
    "MODEM/ONT-INTERMITENCIA WIFI", "CABLE EN EL SUELO O CORTADO"
    # ... puedes agregar la lista completa aquí
])

PRODUCTOS = ["INTERNET", "IPTV", "DTH", "VOIP", "OTT", "PSTN"]
DISTRITOS = ["METRO 1", "METRO 2", "METRO 3", "ESTE", "NORTE 1", "NORTE 2", "SUR"]

# --- SIDEBAR (Navegación) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/03/Claro_logo.svg", width=100) # Placeholder logo
    menu = st.radio("Menú de Navegación", ["Nuevo Registro", "Histórico", "Dashboard Gráfico"])
    st.info(f"Total Casos: {len(st.session_state.db_registros)}")

# --- LÓGICA DE VISTAS ---

if menu == "Nuevo Registro":
    st.title("🔍 Nuevo Registro RCA")
    
    tipo_proceso = st.radio("Seleccione Proceso:", ["Diagnóstico", "Confirmación"], horizontal=True)
    
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            trabajado = st.selectbox("Trabajado por", ["Dariel Peña", "Jorge Hurtado", "Raquel Rodríguez", "Jan Carlos"])
            servicio = st.text_input("Número del Servicio")
            caso3 = st.text_input("Número del caso 3")
            producto = st.selectbox("Producto", PRODUCTOS)
            
        with col2:
            distrito = st.selectbox("Distrito", DISTRITOS)
            tecnologia = st.selectbox("Tecnología", ["FIBRA", "COBRE", "SATELITAL"])
            sintoma = st.selectbox("Síntoma", SINTOMAS)
            enviado = st.selectbox("Enviado a Distrito", ["SI", "NO"])

        comentario = st.text_area("Comentarios adicionales")
        
        btn_guardar = st.form_submit_button(f"Guardar {tipo_proceso}")
        
        if btn_guardar:
            nuevo_dato = {
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "Tipo": tipo_proceso,
                "Trabajado Por": trabajado,
                "Servicio": servicio,
                "Caso 3": caso3,
                "Producto": producto,
                "Tecnologia": tecnologia,
                "Distrito": distrito,
                "Sintoma": sintoma,
                "Enviado a Distrito": enviado
            }
            st.session_state.db_registros = pd.concat([st.session_state.db_registros, pd.DataFrame([nuevo_dato])], ignore_index=True)
            st.success(f"✅ {tipo_proceso} guardado correctamente en local.")

elif menu == "Histórico":
    st.title("📋 Histórico de Averías")
    
    if st.session_state.db_registros.empty:
        st.warning("No hay registros aún.")
    else:
        # Filtros rápidos
        df = st.session_state.db_registros
        f_tipo = st.multiselect("Filtrar por Tipo:", df["Tipo"].unique(), default=df["Tipo"].unique())
        df_filtrado = df[df["Tipo"].isin(f_tipo)]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Exportar a CSV
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Consolidado (CSV)", csv, "RCA_Consolidado.csv", "text/csv")

elif menu == "Dashboard Gráfico":
    st.title("📊 Dashboard Analítico")
    
    if st.session_state.db_registros.empty:
        st.info("Agregue datos para ver las gráficas.")
    else:
        df = st.session_state.db_registros
        
        # KPIs Superiores
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Analizado", len(df))
        k2.metric("Diagnósticos", len(df[df["Tipo"] == "Diagnóstico"]))
        k3.metric("Confirmaciones", len(df[df["Tipo"] == "Confirmación"]))
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Casos por Producto")
            fig_prod = px.bar(df, x="Producto", color="Producto", title="Distribución por Producto")
            st.plotly_chart(fig_prod, use_container_width=True)
            
        with c2:
            st.subheader("Distribución por Distrito")
            fig_dist = px.pie(df, names="Distrito", hole=0.4, title="Casos por Zona")
            st.plotly_chart(fig_dist, use_container_width=True)

        st.subheader("Top Síntomas")
        fig_sint = px.bar(df['Sintoma'].value_counts().reset_index(), x='Sintoma', y='count', orientation='v')
        st.plotly_chart(fig_sint, use_container_width=True)