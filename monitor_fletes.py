"""
MONITOR DE FLETES MARÍTIMOS
============================
Estrategia "Proxy Hacker" para estimar tendencia de fletes:
- Si acciones de navieras suben → Fletes están subiendo
- Si acciones de navieras bajan → Fletes están bajando

Navieras monitoreadas:
- ZIM (Israel) - Especialista en Asia-Latam
- MAERSK (Dinamarca) - Líder mundial
- COSCO (China) - Principal naviera china
- Hapag-Lloyd (Alemania) - Fuerte en Sudamérica

Índices de referencia:
- Baltic Dry Index (BDI) - Graneles secos
- Freightos Baltic Index (FBX) - Contenedores
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ========================================
# NAVIERAS Y ETFs DE FLETES
# ========================================

NAVIERAS = {
    "ZIM": {
        "ticker": "ZIM",
        "nombre": "ZIM Integrated Shipping",
        "pais": "🇮🇱 Israel",
        "rutas": "Asia → Sudamérica (especialista)",
        "relevancia": "ALTA - Ruta China-Ecuador"
    },
    "Maersk": {
        "ticker": "AMKBY",  # ADR en USA
        "nombre": "A.P. Moller-Maersk",
        "pais": "🇩🇰 Dinamarca",
        "rutas": "Global - Líder mundial",
        "relevancia": "ALTA - Mayor naviera"
    },
    "COSCO": {
        "ticker": "CICOY",  # ADR en USA
        "nombre": "COSCO Shipping Holdings",
        "pais": "🇨🇳 China",
        "rutas": "Asia → Todo el mundo",
        "relevancia": "ALTA - Principal naviera china"
    },
    "Hapag-Lloyd": {
        "ticker": "HLAGF",
        "nombre": "Hapag-Lloyd AG",
        "pais": "🇩🇪 Alemania",
        "rutas": "Europa ↔ Sudamérica",
        "relevancia": "MEDIA - Fuerte en Latam"
    }
}

# ETFs relacionados con transporte marítimo
ETFS_FLETES = {
    "BDRY": {
        "nombre": "Breakwave Dry Bulk Shipping ETF",
        "descripcion": "Sigue futuros del Baltic Dry Index",
        "tipo": "Graneles secos (acero a granel)"
    },
    "BOAT": {
        "nombre": "SonicShares Global Shipping ETF",
        "descripcion": "Acciones de navieras globales",
        "tipo": "Contenedores y graneles"
    }
}


def obtener_precio_naviera(ticker):
    """Obtiene precio actual y cambio de una naviera"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if len(hist) >= 2:
            precio_actual = hist['Close'].iloc[-1]
            precio_ayer = hist['Close'].iloc[-2]
            precio_semana = hist['Close'].iloc[0]
            
            cambio_dia = ((precio_actual - precio_ayer) / precio_ayer) * 100
            cambio_semana = ((precio_actual - precio_semana) / precio_semana) * 100
            
            return {
                "precio": round(precio_actual, 2),
                "cambio_dia": round(cambio_dia, 2),
                "cambio_semana": round(cambio_semana, 2),
                "disponible": True
            }
    except Exception as e:
        print(f"Error obteniendo {ticker}: {e}")
    
    return {"disponible": False}


def obtener_historico_naviera(ticker, periodo="3mo"):
    """Obtiene histórico de precios de una naviera"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=periodo)
        return hist
    except:
        return None


def analizar_tendencia_fletes():
    """
    Analiza tendencia de fletes basado en acciones de navieras
    
    Lógica:
    - Promedio ponderado del cambio % de las principales navieras
    - ZIM tiene más peso porque es especialista en Asia-Latam
    """
    
    pesos = {"ZIM": 0.4, "Maersk": 0.25, "COSCO": 0.25, "Hapag-Lloyd": 0.1}
    
    cambios = []
    datos_navieras = {}
    
    for nombre, datos in NAVIERAS.items():
        precio = obtener_precio_naviera(datos["ticker"])
        datos_navieras[nombre] = {**datos, **precio}
        
        if precio.get("disponible"):
            cambios.append({
                "naviera": nombre,
                "cambio": precio["cambio_semana"],
                "peso": pesos.get(nombre, 0.1)
            })
    
    # Calcular índice ponderado
    if cambios:
        indice_fletes = sum(c["cambio"] * c["peso"] for c in cambios)
        
        # Determinar tendencia
        if indice_fletes > 5:
            tendencia = "SUBIENDO FUERTE"
            alerta = "🔴 Fletes disparándose - Negociar contratos AHORA"
            color = "red"
        elif indice_fletes > 2:
            tendencia = "SUBIENDO"
            alerta = "🟡 Fletes en alza - Considerar compra anticipada"
            color = "orange"
        elif indice_fletes < -5:
            tendencia = "BAJANDO FUERTE"
            alerta = "🟢 Oportunidad - Fletes cayendo, negociar descuentos"
            color = "green"
        elif indice_fletes < -2:
            tendencia = "BAJANDO"
            alerta = "🟢 Fletes a la baja - Buen momento para importar"
            color = "lightgreen"
        else:
            tendencia = "ESTABLE"
            alerta = "⚪ Mercado estable"
            color = "gray"
        
        return {
            "indice": round(indice_fletes, 2),
            "tendencia": tendencia,
            "alerta": alerta,
            "color": color,
            "navieras": datos_navieras,
            "disponible": True
        }
    
    return {"disponible": False}


def estimar_flete_china_guayaquil(tendencia_info):
    """
    Estima costo de flete China → Guayaquil basado en tendencia
    
    Base: $2,500 - $4,500 USD por contenedor 40'
    Ajuste según tendencia del mercado
    """
    
    # Precio base (promedio histórico)
    precio_base_40ft = 3500  # USD
    precio_base_ton = 85     # USD por tonelada (breakbulk)
    
    if not tendencia_info.get("disponible"):
        return {
            "flete_40ft": precio_base_40ft,
            "flete_ton": precio_base_ton,
            "ajuste_pct": 0,
            "modo": "ESTIMADO"
        }
    
    indice = tendencia_info["indice"]
    
    # Ajustar según tendencia (±20% máximo)
    ajuste_pct = min(max(indice * 2, -20), 20)
    
    flete_40ft_ajustado = precio_base_40ft * (1 + ajuste_pct / 100)
    flete_ton_ajustado = precio_base_ton * (1 + ajuste_pct / 100)
    
    return {
        "flete_40ft": round(flete_40ft_ajustado, 0),
        "flete_ton": round(flete_ton_ajustado, 2),
        "ajuste_pct": round(ajuste_pct, 1),
        "precio_base_40ft": precio_base_40ft,
        "modo": "PROXY"
    }


# ========================================
# COMPONENTE UI SIDEBAR
# ========================================

def mostrar_fletes_sidebar():
    """Muestra indicador de fletes en sidebar"""
    
    st.markdown("---")
    st.markdown("### 🚢 **Tendencia Fletes**")
    
    tendencia = analizar_tendencia_fletes()
    
    if tendencia.get("disponible"):
        # Indicador principal
        st.metric(
            "📊 Índice Navieras",
            tendencia["tendencia"],
            delta=f"{tendencia['indice']:+.1f}% semanal",
            delta_color="inverse"
        )
        
        # Estimación de flete
        flete = estimar_flete_china_guayaquil(tendencia)
        st.caption(f"🇨🇳→🇪🇨 ~${flete['flete_40ft']:,.0f}/40ft")
        
        # Alerta
        if "🔴" in tendencia["alerta"]:
            st.error(tendencia["alerta"])
        elif "🟢" in tendencia["alerta"]:
            st.success(tendencia["alerta"])
        else:
            st.info(tendencia["alerta"])
    else:
        st.caption("⚠️ Datos no disponibles")


# ========================================
# PANEL PRINCIPAL
# ========================================

def mostrar_panel_fletes():
    """Panel completo de monitoreo de fletes"""
    
    st.subheader("🚢 Monitor de Fletes Marítimos")
    st.markdown("*Estrategia 'Proxy Hacker' - Correlación acciones navieras ↔ fletes*")
    
    # Análisis de tendencia
    tendencia = analizar_tendencia_fletes()
    
    if not tendencia.get("disponible"):
        st.warning("⚠️ No se pudieron obtener datos de navieras")
        return
    
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    flete = estimar_flete_china_guayaquil(tendencia)
    
    with col1:
        st.metric(
            "📊 Índice Fletes",
            tendencia["tendencia"],
            delta=f"{tendencia['indice']:+.1f}%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "📦 Container 40'",
            f"${flete['flete_40ft']:,.0f}",
            delta=f"{flete['ajuste_pct']:+.1f}% vs base",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "⚖️ Por Tonelada",
            f"${flete['flete_ton']:.0f}/ton",
            delta="Breakbulk"
        )
    
    with col4:
        st.metric(
            "📍 Ruta",
            "China → GYE",
            delta="~35 días"
        )
    
    # Alerta
    st.markdown("---")
    if "🔴" in tendencia["alerta"]:
        st.error(f"**ALERTA:** {tendencia['alerta']}")
    elif "🟢" in tendencia["alerta"]:
        st.success(f"**OPORTUNIDAD:** {tendencia['alerta']}")
    else:
        st.info(tendencia["alerta"])
    
    st.markdown("---")
    
    # Tabla de navieras
    st.markdown("### 🏢 Acciones de Navieras (Proxy de Fletes)")
    
    datos_tabla = []
    for nombre, datos in tendencia["navieras"].items():
        if datos.get("disponible"):
            datos_tabla.append({
                "Naviera": nombre,
                "País": datos["pais"],
                "Precio USD": f"${datos['precio']:.2f}",
                "Cambio Día": f"{datos['cambio_dia']:+.1f}%",
                "Cambio Semana": f"{datos['cambio_semana']:+.1f}%",
                "Relevancia": datos["relevancia"]
            })
    
    if datos_tabla:
        df = pd.DataFrame(datos_tabla)
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    # Gráfico de ZIM (más relevante para China-Latam)
    st.markdown("---")
    st.markdown("### 📈 ZIM Shipping - Tendencia 3 meses")
    st.caption("*ZIM es especialista en rutas Asia-Sudamérica*")
    
    hist_zim = obtener_historico_naviera("ZIM", "3mo")
    
    if hist_zim is not None and len(hist_zim) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_zim.index,
            y=hist_zim['Close'],
            mode='lines',
            name='ZIM',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))
        
        fig.update_layout(
            title="Precio de ZIM (correlación con fletes China→Latam)",
            xaxis_title="Fecha",
            yaxis_title="USD",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Explicación
    with st.expander("ℹ️ ¿Por qué funciona este 'proxy'?"):
        st.markdown("""
        ## Estrategia "Proxy Hacker" para Fletes
        
        ### ¿Por qué las acciones de navieras reflejan los fletes?
        
        Las navieras (ZIM, Maersk, COSCO) ganan dinero cuando los fletes suben. 
        Por eso, **cuando sus acciones suben, es porque el mercado espera que cobren más por los contenedores**.
        
        ### Correlación histórica
        
        | Evento | Acciones Navieras | Fletes |
        |--------|-------------------|--------|
        | COVID 2021 | +500% | +400% |
        | Post-COVID 2023 | -60% | -50% |
        | Crisis Mar Rojo 2024 | +30% | +25% |
        
        ### ¿Por qué ZIM es el más relevante?
        
        - **ZIM es especialista en rutas transpacíficas y Asia-Sudamérica**
        - Maersk y COSCO son más diversificados
        - El precio de ZIM refleja mejor el flete China → Ecuador
        
        ### Limitaciones
        
        - No es precio exacto, es **tendencia**
        - Retraso de 1-2 semanas vs. cotizaciones reales
        - Mejor para decisiones estratégicas, no para negociación de centavos
        
        ### APIs pagadas (si necesitas datos exactos)
        
        | Servicio | Costo | Datos |
        |----------|-------|-------|
        | Freightos FBX | $500+/mes | Índice diario por ruta |
        | Xeneta | $1,000+/mes | Precios spot y contrato |
        | Drewry | $2,000+/mes | Análisis completo |
        """)


def obtener_flete_estimado_para_cfr():
    """
    Función auxiliar para integrar con calculadora CFR
    Retorna flete estimado por tonelada
    """
    tendencia = analizar_tendencia_fletes()
    flete = estimar_flete_china_guayaquil(tendencia)
    return flete["flete_ton"]
