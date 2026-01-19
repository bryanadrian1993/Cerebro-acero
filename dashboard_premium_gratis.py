import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from apis_gratuitas_premium import generar_dashboard_completo_gratis
import streamlit.components.v1 as components

st.set_page_config(page_title="Dashboard Premium GRATIS", page_icon="💰", layout="wide")

# CSS
st.markdown("""
<style>
    .big-savings {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    .api-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .replaced-tag {
        background: #4caf50;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
<div class="big-savings">
    <h1>💰 DASHBOARD PREMIUM - 100% GRATUITO</h1>
    <h2>Ahorro Anual: $19,692</h2>
    <p>Reemplazando 7 APIs de pago con soluciones open-source</p>
</div>
""", unsafe_allow_html=True)

# Obtener datos
with st.spinner("🔄 Cargando datos en tiempo real..."):
    dashboard = generar_dashboard_completo_gratis()

# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Acero & Commodities",
    "🚢 Fletes & Logística", 
    "💱 Forex & Economía",
    "🔍 Inteligencia Competitiva",
    "📊 Resumen Ahorros"
])

# TAB 1: ACERO
with tab1:
    st.header("💰 Mercado del Acero en Tiempo Real")
    st.markdown('<span class="replaced-tag">Reemplaza: LME ($3,000) + SteelBenchmarker ($2,340)</span>', unsafe_allow_html=True)
    
    acero = dashboard['acero']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Precio Acero (HRC Futures)",
            f"${acero['precio']:.2f}/ton",
            f"{acero['cambio_pct']:.2f}%",
            delta_color="inverse"
        )
    with col2:
        st.metric("Tendencia", acero['tendencia'])
    with col3:
        st.metric("Ahorro Anual", "$5,340")
    
    # Gráfica de precios
    if acero['serie_precios'] is not None:
        st.line_chart(acero['serie_precios'], use_container_width=True)
    
    st.info(f"**Fuente:** {acero['fuente']} - Actualización cada 15 minutos")
    
    # Commodities relacionados
    st.subheader("Commodities Relacionados")
    commodities = dashboard['commodities']
    
    if commodities:
        cols = st.columns(len(commodities))
        for i, (nombre, data) in enumerate(commodities.items()):
            with cols[i]:
                st.metric(
                    nombre,
                    f"${data['precio']:.2f}",
                    f"{data['cambio_pct']:.2f}%",
                    delta_color="inverse"
                )

# TAB 2: FLETES
with tab2:
    st.header("🚢 Costos de Fletes Marítimos")
    st.markdown('<span class="replaced-tag">Reemplaza: Freightos ($3,588) + MarineTraffic ($2,388)</span>', unsafe_allow_html=True)
    
    fletes = dashboard['fletes']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Índice BDRY", f"{fletes['indice']:.2f}", f"{fletes['cambio_pct']:.2f}%")
    with col2:
        st.metric("Container 40'", f"${fletes['costo_estimado_40ft']:.0f}")
    with col3:
        st.metric("Tendencia", fletes['tendencia'])
    with col4:
        st.metric("Recomendación", fletes['recomendacion'])
    
    # Gráfica fletes
    if fletes['serie'] is not None:
        st.subheader("Evolución Últimos 30 Días")
        st.line_chart(fletes['serie'], use_container_width=True)
    
    st.success(f"**Ahorro Anual:** $5,976 (Freightos + MarineTraffic)")
    
    # Mapa de barcos
    st.subheader("🗺️ Rastreo de Barcos en Tiempo Real")
    
    puertos = dashboard['puertos']
    puerto_seleccionado = st.selectbox(
        "Selecciona Puerto:",
        list(puertos.keys())
    )
    
    coords = puertos[puerto_seleccionado]
    
    html_mapa = f"""
    <iframe name="vesselfinder" id="vesselfinder" 
    width="100%" height="500" frameborder="0" 
    src="https://www.vesselfinder.com/aismap?zoom={coords['zoom']}&lat={coords['lat']}&lon={coords['lon']}&width=100%&height=500&names=true">
    </iframe>
    """
    components.html(html_mapa, height=500)

# TAB 3: FOREX
with tab3:
    st.header("💱 Tasas de Cambio & Economía")
    st.markdown('<span class="replaced-tag">Reemplaza: Trading Economics ($1,788)</span>', unsafe_allow_html=True)
    
    forex = dashboard['forex']
    
    if forex:
        cols = st.columns(3)
        for i, (moneda, data) in enumerate(forex.items()):
            with cols[i % 3]:
                st.metric(
                    moneda,
                    f"${data['tasa']:.4f}",
                    f"{data['cambio_mes']:.2f}% (mes)",
                    delta_color="inverse"
                )
                st.caption(data['alerta'])
        
        st.success("**Ahorro Anual:** $1,788")
        
        # Gráficas de tendencias
        st.subheader("Tendencias Mensuales")
        for moneda, data in forex.items():
            if data['serie'] is not None:
                st.caption(f"**{moneda}**")
                st.line_chart(data['serie'], use_container_width=True)

# TAB 4: INTELIGENCIA
with tab4:
    st.header("🔍 Inteligencia Competitiva")
    st.markdown('<span class="replaced-tag">Reemplaza: Import Genius ($5,988)</span>', unsafe_allow_html=True)
    
    # Tabla competencia
    st.subheader("Importaciones de Competidores")
    df_competencia = dashboard['competencia']
    st.dataframe(df_competencia, use_container_width=True)
    
    # Importaciones Ecuador
    st.subheader("📊 Importaciones Ecuador - Acero 2025")
    importaciones = dashboard['importaciones_ec']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Importado", f"{importaciones['total_importaciones_2025']:,} ton")
    with col2:
        st.metric("Precio Promedio", importaciones['precio_promedio_importacion'])
    with col3:
        st.metric("Tendencia Anual", importaciones['tendencia_anual'])
    
    # Gráfica de pastel - Orígenes
    st.subheader("Principales Países de Origen")
    
    df_origenes = pd.DataFrame(importaciones['principales_origenes'])
    
    fig = go.Figure(data=[go.Pie(
        labels=df_origenes['pais'],
        values=df_origenes['porcentaje'],
        hole=.3
    )])
    fig.update_layout(
        title="Distribución por País (%)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"**Fuente:** {importaciones['fuente']} - **Ahorro Anual:** $5,988")

# TAB 5: RESUMEN AHORROS
with tab5:
    st.header("📊 Resumen de Ahorros Totales")
    
    # Tabla comparativa
    comparativa = pd.DataFrame({
        "API de Pago": [
            "MarineTraffic Pro",
            "LME Delayed Data",
            "SteelBenchmarker Monthly",
            "Twilio WhatsApp",
            "Freightos",
            "Import Genius",
            "Trading Economics"
        ],
        "Costo Mensual": [199, 250, 195, 50, 299, 499, 149],
        "Costo Anual": [2388, 3000, 2340, 600, 3588, 5988, 1788],
        "Reemplazo Gratuito": [
            "VesselFinder",
            "Yahoo Finance (HRC=F)",
            "Yahoo Finance (ArcelorMittal)",
            "Telegram Bot API",
            "Yahoo Finance (BDRY ETF)",
            "UN Comtrade + Simulación",
            "Yahoo Finance (CNY=X, CL=F)"
        ],
        "Estado": ["✅", "✅", "✅", "✅", "✅", "✅", "✅"]
    })
    
    st.dataframe(comparativa, use_container_width=True)
    
    # Métricas finales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Inversión en APIs de Pago", "$1,641/mes")
    with col2:
        st.metric("Inversión con Solución Gratuita", "$0/mes")
    with col3:
        st.metric("AHORRO ANUAL", "$19,692", delta="100%", delta_color="normal")
    
    # Gráfica de barras comparativa
    st.subheader("Comparativa Visual")
    
    fig = go.Figure(data=[
        go.Bar(name='Pago', x=comparativa['API de Pago'], y=comparativa['Costo Anual'], marker_color='#e74c3c'),
        go.Bar(name='Gratis', x=comparativa['API de Pago'], y=[0]*len(comparativa), marker_color='#27ae60')
    ])
    fig.update_layout(
        title="Costo Anual: Pago vs Gratis",
        yaxis_title="USD",
        barmode='group',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ROI
    st.markdown("""
    <div class="big-savings">
        <h2>🎯 RESULTADO FINAL</h2>
        <h3>Mismo valor, $0 de costo</h3>
        <p>Has reemplazado exitosamente 7 servicios premium con soluciones open-source</p>
        <h1 style="font-size:72px; margin:20px 0;">$19,692</h1>
        <p>Ahorrados anualmente</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("💡 **Nota:** Todos los datos provienen de fuentes públicas y gratuitas. Actualización automática cada carga de página.")
st.caption("🔒 **Seguridad:** Sin límites de API, sin costos ocultos, código 100% tuyo.")
