"""
CALCULADORA CFR LO GUAYAQUIL
============================
Calcula el precio de acero puesto en puerto de Guayaquil

Fórmula:
CFR LO Guayaquil = Precio FOB China + Flete Marítimo + Descarga (LO)

Términos:
- FOB (Free On Board): Precio del acero puesto en barco en China
- CFR (Cost and Freight): Incluye flete marítimo
- LO (Liner Out): Descarga del barco al muelle incluida
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import yfinance as yf

# Importar precios de Shanghai
try:
    from akshare_china import obtener_precio_acero_shanghai, convertir_cny_a_usd
except:
    def obtener_precio_acero_shanghai():
        return {"hrc": {"precio": 4200}, "rebar": {"precio": 3800}, "inox": {"precio": 16500}}
    def convertir_cny_a_usd(precio, tasa=7.25):
        return precio / tasa


# ========================================
# COSTOS DE FLETE CHINA → GUAYAQUIL
# ========================================

# Rutas principales desde China a Guayaquil
RUTAS_FLETE = {
    "Shanghai → Guayaquil": {
        "puerto_origen": "Shanghai",
        "puerto_destino": "Guayaquil",
        "dias_transito": 35,
        "flete_20ft": 2800,  # USD por contenedor 20'
        "flete_40ft": 4500,  # USD por contenedor 40'
        "flete_ton": 85,     # USD por tonelada (bulk/breakbulk)
        "lo_descarga": 12,   # USD por tonelada (Liner Out)
    },
    "Tianjin → Guayaquil": {
        "puerto_origen": "Tianjin (Benxi Steel)",
        "puerto_destino": "Guayaquil",
        "dias_transito": 38,
        "flete_20ft": 2900,
        "flete_40ft": 4700,
        "flete_ton": 90,
        "lo_descarga": 12,
    },
    "Qingdao → Guayaquil": {
        "puerto_origen": "Qingdao",
        "puerto_destino": "Guayaquil",
        "dias_transito": 36,
        "flete_20ft": 2850,
        "flete_40ft": 4600,
        "flete_ton": 88,
        "lo_descarga": 12,
    },
    "Ningbo → Guayaquil": {
        "puerto_origen": "Ningbo",
        "puerto_destino": "Guayaquil",
        "dias_transito": 34,
        "flete_20ft": 2750,
        "flete_40ft": 4400,
        "flete_ton": 82,
        "lo_descarga": 12,
    }
}

# Proveedores REALES de Import Aceros S.A.
PROVEEDORES_CHINA = {
    "BENXI (Benxi Steel Group)": {
        "puerto": "Tianjin → Guayaquil",
        "productos": ["HRC (Laminado Caliente)", "CRC (Laminado Frío)", "Galvanizado"],
        "ubicacion": "Liaoning",
        "principal": True
    },
    "ANGANG (Ansteel Group)": {
        "puerto": "Tianjin → Guayaquil",
        "productos": ["Planchas Navales", "Planchas Estructurales", "CRC (Laminado Frío)"],
        "ubicacion": "Liaoning",
        "principal": True
    },
    "TIANTIE (Tianjin Tiantie)": {
        "puerto": "Tianjin → Guayaquil",
        "productos": ["Aluzinc", "CRC (Laminado Frío)"],
        "ubicacion": "Tianjin",
        "principal": True
    },
    "FWD (Shandong FWD Steel)": {
        "puerto": "Qingdao → Guayaquil",
        "productos": ["Galvanizado (espesores delgados)"],
        "ubicacion": "Shandong",
        "principal": False
    },
    "SHUIXIN (Tangshan Shuixin)": {
        "puerto": "Tianjin → Guayaquil",
        "productos": ["Planchas Estructurales ASTM A572"],
        "ubicacion": "Tangshan",
        "principal": False
    },
    "HBIS (Hebei Iron and Steel)": {
        "puerto": "Tianjin → Guayaquil",
        "productos": ["Galvanizado (Flejes)"],
        "ubicacion": "Hebei",
        "principal": False
    },
}


def obtener_tipo_cambio_usd_cny():
    """Obtiene tipo de cambio USD/CNY en tiempo real"""
    try:
        ticker = yf.Ticker("CNY=X")
        data = ticker.history(period="1d")
        if len(data) > 0:
            return round(data['Close'].iloc[-1], 4)
    except:
        pass
    return 7.25  # Fallback


def calcular_cfr_lo_guayaquil(precio_fob_usd, toneladas, ruta="Shanghai → Guayaquil"):
    """
    Calcula el precio CFR LO Guayaquil
    
    Args:
        precio_fob_usd: Precio FOB en USD/ton
        toneladas: Cantidad de toneladas
        ruta: Ruta de envío
    
    Returns:
        dict con desglose de costos
    """
    
    datos_ruta = RUTAS_FLETE.get(ruta, RUTAS_FLETE["Shanghai → Guayaquil"])
    
    # Costos por tonelada
    flete_ton = datos_ruta["flete_ton"]
    lo_descarga = datos_ruta["lo_descarga"]
    
    # Cálculo
    costo_fob_total = precio_fob_usd * toneladas
    costo_flete = flete_ton * toneladas
    costo_lo = lo_descarga * toneladas
    
    cfr_lo_total = costo_fob_total + costo_flete + costo_lo
    cfr_lo_ton = cfr_lo_total / toneladas if toneladas > 0 else 0
    
    return {
        "precio_fob_ton": precio_fob_usd,
        "flete_ton": flete_ton,
        "lo_descarga_ton": lo_descarga,
        "cfr_lo_ton": round(cfr_lo_ton, 2),
        "costo_fob_total": round(costo_fob_total, 2),
        "costo_flete_total": round(costo_flete, 2),
        "costo_lo_total": round(costo_lo, 2),
        "cfr_lo_total": round(cfr_lo_total, 2),
        "dias_transito": datos_ruta["dias_transito"],
        "puerto_origen": datos_ruta["puerto_origen"],
        "puerto_destino": datos_ruta["puerto_destino"],
    }


# ========================================
# COMPONENTE UI SIDEBAR
# ========================================

def mostrar_cfr_sidebar():
    """Muestra resumen CFR en el sidebar"""
    
    st.markdown("---")
    st.markdown("### 🚢 **CFR LO Guayaquil**")
    
    # Obtener precios de Shanghai
    precios = obtener_precio_acero_shanghai()
    tipo_cambio = obtener_tipo_cambio_usd_cny()
    
    if precios.get("hrc"):
        hrc_cny = precios["hrc"]["precio"]
        hrc_usd = convertir_cny_a_usd(hrc_cny, tipo_cambio)
        
        # Calcular CFR LO
        cfr = calcular_cfr_lo_guayaquil(hrc_usd, 1)
        
        st.metric(
            "🔥 HRC CFR LO GYE",
            f"${cfr['cfr_lo_ton']:,.0f}/ton",
            delta=f"+${cfr['flete_ton'] + cfr['lo_descarga_ton']} flete",
            delta_color="off"
        )
        
        st.caption(f"FOB: ${hrc_usd:,.0f} + Flete: ${cfr['flete_ton']} + LO: ${cfr['lo_descarga_ton']}")
    
    if precios.get("rebar"):
        rb_cny = precios["rebar"]["precio"]
        rb_usd = convertir_cny_a_usd(rb_cny, tipo_cambio)
        cfr_rb = calcular_cfr_lo_guayaquil(rb_usd, 1)
        
        st.metric(
            "🔩 Rebar CFR LO GYE",
            f"${cfr_rb['cfr_lo_ton']:,.0f}/ton",
            delta=f"+${cfr_rb['flete_ton'] + cfr_rb['lo_descarga_ton']} flete",
            delta_color="off"
        )
    
    st.caption(f"💱 USD/CNY: {tipo_cambio}")


# ========================================
# PANEL PRINCIPAL CALCULADORA
# ========================================

def mostrar_calculadora_cfr():
    """Panel completo de calculadora CFR LO"""
    
    st.subheader("🚢 Calculadora CFR LO Guayaquil")
    st.markdown("*Calcula el costo real de acero puesto en puerto de Guayaquil*")
    
    # Obtener datos actuales
    precios = obtener_precio_acero_shanghai()
    tipo_cambio = obtener_tipo_cambio_usd_cny()
    
    st.markdown("---")
    
    # Selector de producto y proveedor
    col1, col2, col3 = st.columns(3)
    
    with col1:
        producto = st.selectbox(
            "📦 Producto",
            ["Hot Rolled Coil (HRC)", "Rebar (Varilla)", "Acero Inoxidable", "Otro"]
        )
    
    with col2:
        proveedor = st.selectbox(
            "🏭 Proveedor",
            list(PROVEEDORES_CHINA.keys())
        )
    
    with col3:
        toneladas = st.number_input(
            "⚖️ Toneladas",
            min_value=1,
            max_value=10000,
            value=100,
            step=10
        )
    
    # Obtener ruta según proveedor
    ruta = PROVEEDORES_CHINA[proveedor]["puerto"]
    
    # Precio FOB
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Precio sugerido de Shanghai
        if "HRC" in producto and precios.get("hrc"):
            precio_sugerido = convertir_cny_a_usd(precios["hrc"]["precio"], tipo_cambio)
        elif "Rebar" in producto and precios.get("rebar"):
            precio_sugerido = convertir_cny_a_usd(precios["rebar"]["precio"], tipo_cambio)
        elif "Inox" in producto and precios.get("inox"):
            precio_sugerido = convertir_cny_a_usd(precios["inox"]["precio"], tipo_cambio)
        else:
            precio_sugerido = 500
        
        precio_fob = st.number_input(
            "💵 Precio FOB China (USD/ton)",
            min_value=100.0,
            max_value=5000.0,
            value=float(round(precio_sugerido, 0)),
            step=10.0,
            help="Precio del acero puesto en barco en China"
        )
    
    with col2:
        st.info(f"""
        **Precio referencia SHFE:**  
        • HRC: ${convertir_cny_a_usd(precios.get('hrc', {}).get('precio', 4200), tipo_cambio):,.0f}/ton  
        • Rebar: ${convertir_cny_a_usd(precios.get('rebar', {}).get('precio', 3800), tipo_cambio):,.0f}/ton  
        • Tipo cambio: {tipo_cambio} CNY/USD
        """)
    
    # Calcular CFR LO
    cfr = calcular_cfr_lo_guayaquil(precio_fob, toneladas, ruta)
    
    st.markdown("---")
    st.markdown("### 📊 Desglose de Costos")
    
    # Mostrar desglose
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📦 FOB China",
            f"${cfr['precio_fob_ton']:,.0f}/ton",
            delta=f"Total: ${cfr['costo_fob_total']:,.0f}"
        )
    
    with col2:
        st.metric(
            "🚢 Flete Marítimo",
            f"${cfr['flete_ton']:,.0f}/ton",
            delta=f"Total: ${cfr['costo_flete_total']:,.0f}"
        )
    
    with col3:
        st.metric(
            "⚓ Descarga (LO)",
            f"${cfr['lo_descarga_ton']:,.0f}/ton",
            delta=f"Total: ${cfr['costo_lo_total']:,.0f}"
        )
    
    with col4:
        st.metric(
            "✅ CFR LO Guayaquil",
            f"${cfr['cfr_lo_ton']:,.0f}/ton",
            delta=f"Total: ${cfr['cfr_lo_total']:,.0f}",
            delta_color="off"
        )
    
    # Resumen visual
    st.markdown("---")
    
    # Tabla de costos
    datos_tabla = pd.DataFrame({
        "Concepto": ["FOB China", "Flete Marítimo", "Descarga (LO)", "**CFR LO Guayaquil**"],
        "USD/ton": [f"${cfr['precio_fob_ton']:,.2f}", f"${cfr['flete_ton']:,.2f}", 
                    f"${cfr['lo_descarga_ton']:,.2f}", f"**${cfr['cfr_lo_ton']:,.2f}**"],
        "Total USD": [f"${cfr['costo_fob_total']:,.2f}", f"${cfr['costo_flete_total']:,.2f}",
                      f"${cfr['costo_lo_total']:,.2f}", f"**${cfr['cfr_lo_total']:,.2f}**"]
    })
    
    st.dataframe(datos_tabla, hide_index=True, use_container_width=True)
    
    # Info de la ruta
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"""
        **🚢 Ruta de Envío:**  
        {cfr['puerto_origen']} → {cfr['puerto_destino']}  
        ⏱️ Tiempo de tránsito: **{cfr['dias_transito']} días**
        """)
    
    with col2:
        st.info(f"""
        **📋 Incoterm: CFR LO**  
        • CFR: Costo + Flete (vendedor paga)  
        • LO: Liner Out - Descarga incluida  
        • Tú pagas: Desaduanización + transporte interno
        """)
    
    # Explicación
    with st.expander("ℹ️ ¿Qué significa CFR LO?"):
        st.markdown("""
        ## CFR LO Guayaquil - Explicación
        
        ### CFR (Cost and Freight)
        - **El vendedor (China)** paga:
          - ✅ El acero (costo del producto)
          - ✅ El flete marítimo hasta Guayaquil
        - **Tú pagas**:
          - 📦 Descarga (pero con LO está incluida)
          - 🛃 Desaduanización
          - 🚚 Transporte interno Ecuador
        
        ### LO (Liner Out / Landed Out)
        - La descarga del barco al muelle **está incluida** en el flete
        - Importante: Sin LO, la descarga la pagas tú (~$8-15/ton extra)
        
        ### ¿Qué te falta pagar después del CFR LO?
        
        | Concepto | Costo Estimado |
        |----------|----------------|
        | Arancel ad-valorem | 5-15% del CIF |
        | IVA (FODINFA) | 0.5% del CIF |
        | Agente aduanas | $150-300 |
        | Transporte GYE→Quito | $35-50/ton |
        | Almacenaje puerto | Variable |
        """)


# ========================================
# COMPARADOR DE PROVEEDORES
# ========================================

def mostrar_comparador_proveedores():
    """Compara CFR LO entre diferentes proveedores REALES de Import Aceros"""
    
    st.subheader("🏭 Tus Proveedores Reales - Import Aceros S.A.")
    st.caption("*Proveedores con los que trabajas actualmente*")
    
    precios = obtener_precio_acero_shanghai()
    tipo_cambio = obtener_tipo_cambio_usd_cny()
    
    # Precio base HRC
    hrc_usd = convertir_cny_a_usd(precios.get("hrc", {}).get("precio", 4200), tipo_cambio)
    
    comparativa = []
    
    for proveedor, datos in PROVEEDORES_CHINA.items():
        ruta = datos["puerto"]
        cfr = calcular_cfr_lo_guayaquil(hrc_usd, 100, ruta)
        
        # Marcar proveedores principales
        es_principal = "⭐" if datos.get("principal", False) else ""
        
        comparativa.append({
            "": es_principal,
            "Proveedor": proveedor,
            "Ubicación": datos.get("ubicacion", "China"),
            "Puerto": RUTAS_FLETE[ruta]["puerto_origen"],
            "FOB USD/ton": f"${hrc_usd:,.0f}",
            "Flete": f"${cfr['flete_ton']:,.0f}",
            "CFR LO GYE": f"${cfr['cfr_lo_ton']:,.0f}",
            "Días": cfr["dias_transito"],
            "Productos": ", ".join(datos["productos"][:2]) + ("..." if len(datos["productos"]) > 2 else "")
        })
    
    df = pd.DataFrame(comparativa)
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.caption("⭐ = Proveedor principal")
    
    # Info de proveedores
    with st.expander("📋 Detalle de Proveedores"):
        for proveedor, datos in PROVEEDORES_CHINA.items():
            principal = "⭐ **PRINCIPAL**" if datos.get("principal") else ""
            st.markdown(f"""
            **{proveedor}** {principal}
            - 📍 Ubicación: {datos.get('ubicacion', 'China')}
            - 🚢 Puerto: {datos['puerto'].split(' → ')[0]}
            - 📦 Productos: {', '.join(datos['productos'])}
            ---
            """)


# ========================================
# PANEL PRODUCTOS CFR LO PARA DASHBOARD PRINCIPAL
# ========================================

def obtener_productos_cfr_lo_principal():
    """
    Devuelve los productos principales de los proveedores con precios CFR LO
    Para mostrar en el dashboard principal
    """
    precios = obtener_precio_acero_shanghai()
    tipo_cambio = obtener_tipo_cambio_usd_cny()
    
    # Precios base de Shanghai en USD
    hrc_usd = convertir_cny_a_usd(precios.get("hrc", {}).get("precio", 4200), tipo_cambio)
    rebar_usd = convertir_cny_a_usd(precios.get("rebar", {}).get("precio", 3800), tipo_cambio)
    inox_usd = convertir_cny_a_usd(precios.get("inox", {}).get("precio", 16500), tipo_cambio)
    
    productos = []
    
    # Productos principales por proveedor
    productos_por_proveedor = {
        "BENXI": {"producto": "HRC (Laminado Caliente)", "fob": hrc_usd, "ruta": "Tianjin → Guayaquil", "icono": "🔥"},
        "ANGANG": {"producto": "Planchas Navales", "fob": hrc_usd + 50, "ruta": "Tianjin → Guayaquil", "icono": "🚢"},
        "TIANTIE": {"producto": "Aluzinc", "fob": hrc_usd + 80, "ruta": "Tianjin → Guayaquil", "icono": "✨"},
        "FWD": {"producto": "Galvanizado", "fob": hrc_usd + 60, "ruta": "Qingdao → Guayaquil", "icono": "🛡️"},
        "SHUIXIN": {"producto": "Planchas A572", "fob": hrc_usd + 30, "ruta": "Tianjin → Guayaquil", "icono": "🏗️"},
        "HBIS": {"producto": "Galv. Flejes", "fob": hrc_usd + 40, "ruta": "Tianjin → Guayaquil", "icono": "📦"},
    }
    
    for proveedor, datos in productos_por_proveedor.items():
        cfr = calcular_cfr_lo_guayaquil(datos["fob"], 1, datos["ruta"])
        productos.append({
            "proveedor": proveedor,
            "producto": datos["producto"],
            "fob_usd": round(datos["fob"], 0),
            "flete": cfr["flete_ton"],
            "lo": cfr["lo_descarga_ton"],
            "cfr_lo": cfr["cfr_lo_ton"],
            "dias": cfr["dias_transito"],
            "icono": datos["icono"],
            "ruta": datos["ruta"]
        })
    
    return productos, tipo_cambio


def mostrar_productos_proveedores_principal():
    """
    Muestra los productos de proveedores con CFR LO en el dashboard principal
    Diseñado para ocupar la posición de 'Datos de Mercado en Tiempo Real'
    """
    import streamlit as st
    
    st.markdown("### 🏭 Productos CFR LO Guayaquil - Tus Proveedores")
    
    productos, tipo_cambio = obtener_productos_cfr_lo_principal()
    
    # Mostrar 6 productos en 2 filas de 3
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    # Primera fila: Proveedores principales
    principales = [p for p in productos if p["proveedor"] in ["BENXI", "ANGANG", "TIANTIE"]]
    for i, prod in enumerate(principales):
        with cols[i]:
            st.metric(
                f"{prod['icono']} {prod['proveedor']}",
                f"${prod['cfr_lo']:,.0f}/ton",
                delta=f"FOB ${prod['fob_usd']:,.0f} + flete",
                delta_color="off"
            )
            st.caption(f"{prod['producto']} • {prod['dias']} días")
    
    # Segunda fila: Proveedores secundarios
    col4, col5, col6 = st.columns(3)
    cols2 = [col4, col5, col6]
    
    secundarios = [p for p in productos if p["proveedor"] in ["FWD", "SHUIXIN", "HBIS"]]
    for i, prod in enumerate(secundarios):
        with cols2[i]:
            st.metric(
                f"{prod['icono']} {prod['proveedor']}",
                f"${prod['cfr_lo']:,.0f}/ton",
                delta=f"FOB ${prod['fob_usd']:,.0f} + flete",
                delta_color="off"
            )
            st.caption(f"{prod['producto']} • {prod['dias']} días")
    
    st.caption(f"💱 Tipo de cambio: {tipo_cambio} CNY/USD | Precios FOB referencia Shanghai SHFE")
