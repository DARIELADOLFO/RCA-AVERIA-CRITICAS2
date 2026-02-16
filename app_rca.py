import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="RCA AVERIAS CRITICAS", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%); }
    h1 { color: #E30613; text-align: center; }
    div[data-testid="stMetricValue"] { color: #E30613; font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXIÓN A GOOGLE SHEETS
# ---------------------------------------------------------
# URL de tu Google Sheet (CÁMBIALO POR EL TUYO QUE PUSISTE PÚBLICO)
# Ejemplo: "https://docs.google.com/spreadsheets/d/TU_ID_LARGO_AQUI/edit?usp=sharing"
url_sheet = st.secrets["public_gsheets_url"] 

# Crear conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para cargar datos (con caché de 10 segundos para ver cambios rápido)
def cargar_datos():
    try:
        return conn.read(spreadsheet=url_sheet, ttl=10)
    except:
        return pd.DataFrame()

# Función para guardar datos
def guardar_registro(nuevo_df):
    try:
        conn.update(spreadsheet=url_sheet, data=nuevo_df)
        st.cache_data.clear() # Limpiar caché para ver el cambio de una vez
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# Cargar la base de datos al iniciar
df = cargar_datos()

# Si la hoja está vacía, inicializar columnas (seguridad)
if df.empty:
    columnas_base = [
        "ID", "Fecha", "Hora", "Tipo", "TrabajadoPor", "NumeroServicio", 
        "NumeroCaso3", "Producto", "StatusServicio", "Distrito", "Sintoma", 
        "Tecnologia", "EnviadoADistrito", "Comentario"
    ]
    df = pd.DataFrame(columns=columnas_base)

# ---------------------------------------------------------
# INTERFAZ GRÁFICA
# ---------------------------------------------------------
st.title("RCA AVERIAS CRITICAS - ONLINE 🔴")
st.markdown(f"**Registros actuales:** {len(df)}")

tab1, tab2, tab3 = st.tabs(["📝 Nuevo Registro", "📋 Histórico", "📊 Dashboard"])

# --- PESTAÑA 1: NUEVO REGISTRO ---
with tab1:
    with st.form("formulario_rca", clear_on_submit=True):
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo", ["Diagnóstico", "Confirmación"])
        trabajado_por = c2.selectbox("Trabajado Por", ["Dariel Peña", "Jorge Hurtado", "Raquel Rodríguez", "Jan Carlos"])
        
        c3, c4, c5 = st.columns(3)
        servicio = c3.text_input("Número Servicio")
        caso3 = c4.text_input("Caso 3")
        producto = c5.selectbox("Producto", ["INTERNET", "IPTV", "DTH", "VOIP"])
        
        c6, c7 = st.columns(2)
        distrito = c6.selectbox("Distrito", ["METRO 1", "METRO 2", "ESTE", "NORTE", "SUR"])
        sintoma = c7.selectbox("Síntoma", ["NO NAVEGA", "LENTITUD", "SIN TONO", "IMAGEN PIXELADA"]) # Agrega tu lista completa aquí
        
        comentario = st.text_area("Comentario")
        
        enviar = st.form_submit_button("💾 Guardar en Nube")
        
        if enviar:
            # Crear la fila nueva
            nueva_fila = pd.DataFrame([{
                "ID": str(datetime.now().timestamp()),
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "Tipo": tipo,
                "TrabajadoPor": trabajado_por,
                "NumeroServicio": servicio,
                "NumeroCaso3": caso3,
                "Producto": producto,
                "StatusServicio": "Activo", # Simplificado
                "Distrito": distrito,
                "Sintoma": sintoma,
                "Tecnologia": "FIBRA", # Simplificado
                "EnviadoADistrito": "NO",
                "Comentario": comentario
            }])
            
            # Unir con lo viejo y guardar
            df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
            if guardar_registro(df_actualizado):
                st.success("¡Guardado! Tu gerente ya puede verlo.")
                st.rerun()

# --- PESTAÑA 2: HISTÓRICO ---
with tab2:
    if st.button("🔄 Refrescar Datos"):
        st.cache_data.clear()
        st.rerun()
        
    st.dataframe(df, use_container_width=True)

# --- PESTAÑA 3: DASHBOARD ---
with tab3:
    if not df.empty:
        col1, col2 = st.columns(2)
        fig1 = px.pie(df, names='Producto', title="Casos por Producto")
        col1.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.bar(df, x='Distrito', title="Casos por Distrito")
        col2.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Aún no hay datos.")
