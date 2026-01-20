"""
TUSHARE - Precios de Acero de China (Shanghai Futures Exchange)
================================================================
Obtiene precios de futuros de:
- rb: Rebar (Varilla corrugada)
- hc: Hot Rolled Coil (Bobina laminada en caliente)

Registro gratuito: https://tushare.pro/register?reg=123456
Después de registrarte, obtienes un token en: https://tushare.pro/user/token
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests

# ========================================
# CONFIGURACIÓN TUSHARE
# ========================================

def get_tushare_token():
    """Obtiene el token de TuShare desde secrets"""
    try:
        return st.secrets.get("TUSHARE_TOKEN", "")
    except:
        return ""

def inicializar_tushare():
    """Inicializa TuShare con el token"""
    token = get_tushare_token()
    if token:
        try:
            import tushare as ts
            ts.set_token(token)
            pro = ts.pro_api()
            return pro
        except Exception as e:
            print(f"[TUSHARE] Error: {e}")
            return None
    return None


# ========================================
# OBTENER PRECIOS DE FUTUROS DE ACERO
# ========================================

def obtener_precio_acero_shanghai():
    """
    Obtiene precios de futuros de acero del Shanghai Futures Exchange
    
    Contratos principales:
    - rb (Rebar): Varilla corrugada - el más líquido
    - hc (Hot Rolled Coil): Bobina laminada en caliente
    - ss (Stainless Steel): Acero inoxidable
    
    Returns: dict con precios y análisis
    """
    
    pro = inicializar_tushare()
    
    resultado = {
        "conectado": False,
        "modo": "SIMULADO",
        "rebar": None,
        "hrc": None,
        "inox": None,
        "tendencia": None,
        "alerta": None,
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    if pro:
        try:
            # Obtener datos del contrato principal de Rebar
            # El formato es: rb2501 (rb = rebar, 25 = año, 01 = mes)
            fecha_hoy = datetime.now().strftime("%Y%m%d")
            fecha_ayer = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            
            # Futuros de Rebar (rb)
            df_rb = pro.fut_daily(ts_code='RB.SHF', start_date=fecha_ayer, end_date=fecha_hoy)
            
            if df_rb is not None and len(df_rb) > 0:
                ultimo_rb = df_rb.iloc[0]
                resultado["rebar"] = {
                    "precio": float(ultimo_rb['close']),
                    "apertura": float(ultimo_rb['open']),
                    "maximo": float(ultimo_rb['high']),
                    "minimo": float(ultimo_rb['low']),
                    "cambio_pct": float(ultimo_rb.get('pct_chg', 0)),
                    "volumen": int(ultimo_rb.get('vol', 0)),
                    "fecha": str(ultimo_rb['trade_date']),
                    "moneda": "CNY/ton"
                }
            
            # Futuros de Hot Rolled Coil (hc)
            df_hc = pro.fut_daily(ts_code='HC.SHF', start_date=fecha_ayer, end_date=fecha_hoy)
            
            if df_hc is not None and len(df_hc) > 0:
                ultimo_hc = df_hc.iloc[0]
                resultado["hrc"] = {
                    "precio": float(ultimo_hc['close']),
                    "apertura": float(ultimo_hc['open']),
                    "maximo": float(ultimo_hc['high']),
                    "minimo": float(ultimo_hc['low']),
                    "cambio_pct": float(ultimo_hc.get('pct_chg', 0)),
                    "volumen": int(ultimo_hc.get('vol', 0)),
                    "fecha": str(ultimo_hc['trade_date']),
                    "moneda": "CNY/ton"
                }
            
            # Futuros de Acero Inoxidable (ss)
            df_ss = pro.fut_daily(ts_code='SS.SHF', start_date=fecha_ayer, end_date=fecha_hoy)
            
            if df_ss is not None and len(df_ss) > 0:
                ultimo_ss = df_ss.iloc[0]
                resultado["inox"] = {
                    "precio": float(ultimo_ss['close']),
                    "cambio_pct": float(ultimo_ss.get('pct_chg', 0)),
                    "moneda": "CNY/ton"
                }
            
            resultado["conectado"] = True
            resultado["modo"] = "REAL - SHFE"
            
            # Análisis de tendencia
            if resultado["hrc"]:
                cambio = resultado["hrc"]["cambio_pct"]
                if cambio > 3:
                    resultado["tendencia"] = "SUBIENDO FUERTE"
                    resultado["alerta"] = "🔴 Precio HRC subiendo >3% - Esperar subida de Benxi/Manuchar"
                elif cambio > 1:
                    resultado["tendencia"] = "SUBIENDO"
                    resultado["alerta"] = "🟡 Tendencia alcista - Monitorear cotizaciones"
                elif cambio < -3:
                    resultado["tendencia"] = "BAJANDO FUERTE"
                    resultado["alerta"] = "🟢 Oportunidad de negociación - Precios cayendo"
                elif cambio < -1:
                    resultado["tendencia"] = "BAJANDO"
                    resultado["alerta"] = "🟢 Precio a la baja - Buen momento para comprar"
                else:
                    resultado["tendencia"] = "ESTABLE"
                    resultado["alerta"] = "⚪ Mercado estable"
            
            return resultado
            
        except Exception as e:
            print(f"[TUSHARE] Error obteniendo datos: {e}")
    
    # Si no hay conexión, usar datos simulados pero realistas
    return obtener_datos_simulados_shanghai()


def obtener_datos_simulados_shanghai():
    """Datos simulados basados en precios históricos reales del SHFE"""
    
    # Precios base realistas (enero 2026)
    # Rebar: ~3800 CNY/ton
    # HRC: ~4200 CNY/ton
    # Inox: ~16500 CNY/ton
    
    import random
    
    # Simular variación diaria realista (-2% a +2%)
    variacion_rb = random.uniform(-2, 2)
    variacion_hc = random.uniform(-2, 2)
    variacion_ss = random.uniform(-1.5, 1.5)
    
    precio_rb = 3800 * (1 + variacion_rb/100)
    precio_hc = 4200 * (1 + variacion_hc/100)
    precio_ss = 16500 * (1 + variacion_ss/100)
    
    # Determinar tendencia
    if variacion_hc > 1.5:
        tendencia = "SUBIENDO"
        alerta = "🟡 Precio HRC tendencia alcista - Revisar cotizaciones de proveedores"
    elif variacion_hc < -1.5:
        tendencia = "BAJANDO"
        alerta = "🟢 Precio HRC a la baja - Buen momento para negociar"
    else:
        tendencia = "ESTABLE"
        alerta = "⚪ Mercado estable"
    
    return {
        "conectado": False,
        "modo": "SIMULADO",
        "rebar": {
            "precio": round(precio_rb, 2),
            "cambio_pct": round(variacion_rb, 2),
            "moneda": "CNY/ton",
            "nombre": "Rebar (Varilla)"
        },
        "hrc": {
            "precio": round(precio_hc, 2),
            "cambio_pct": round(variacion_hc, 2),
            "moneda": "CNY/ton",
            "nombre": "Hot Rolled Coil"
        },
        "inox": {
            "precio": round(precio_ss, 2),
            "cambio_pct": round(variacion_ss, 2),
            "moneda": "CNY/ton",
            "nombre": "Stainless Steel"
        },
        "tendencia": tendencia,
        "alerta": alerta,
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M")
    }


def convertir_cny_a_usd(precio_cny, tasa_cambio=7.25):
    """Convierte precio de CNY a USD"""
    return round(precio_cny / tasa_cambio, 2)


# ========================================
# COMPONENTE UI PARA SIDEBAR
# ========================================

def mostrar_precios_shanghai_sidebar():
    """Muestra los precios de Shanghai en el sidebar"""
    
    st.markdown("---")
    st.markdown("### 🇨🇳 **Precios Shanghai (SHFE)**")
    
    datos = obtener_precio_acero_shanghai()
    
    # Indicador de conexión
    if datos["modo"] == "REAL - SHFE":
        st.success("🔗 Conectado a TuShare")
    else:
        st.caption("📊 Datos estimados")
    
    # Hot Rolled Coil (el más relevante para Import Aceros)
    if datos["hrc"]:
        hrc = datos["hrc"]
        precio_usd = convertir_cny_a_usd(hrc["precio"])
        
        st.metric(
            "🔥 HRC (Bobina)",
            f"¥{hrc['precio']:,.0f}",
            delta=f"{hrc['cambio_pct']:+.1f}%",
            delta_color="inverse"
        )
        st.caption(f"≈ ${precio_usd:,.0f} USD/ton")
    
    # Rebar
    if datos["rebar"]:
        rb = datos["rebar"]
        st.metric(
            "🔩 Rebar (Varilla)",
            f"¥{rb['precio']:,.0f}",
            delta=f"{rb['cambio_pct']:+.1f}%",
            delta_color="inverse"
        )
    
    # Alerta de tendencia
    if datos["alerta"]:
        if "🔴" in datos["alerta"]:
            st.error(datos["alerta"])
        elif "🟢" in datos["alerta"]:
            st.success(datos["alerta"])
        else:
            st.info(datos["alerta"])


def mostrar_panel_china_completo():
    """Panel completo de precios de China para la sección principal"""
    
    st.subheader("🇨🇳 Precios de Acero - Shanghai Futures Exchange")
    
    datos = obtener_precio_acero_shanghai()
    
    # Estado de conexión
    col1, col2 = st.columns([2, 1])
    with col1:
        if datos["modo"] == "REAL - SHFE":
            st.success("✅ Conectado a TuShare - Datos en tiempo real")
        else:
            st.warning("⚠️ Modo demo - Registrarse en tushare.pro para datos reales")
    with col2:
        st.caption(f"Actualizado: {datos['ultima_actualizacion']}")
    
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if datos["hrc"]:
            hrc = datos["hrc"]
            precio_usd = convertir_cny_a_usd(hrc["precio"])
            st.metric(
                "🔥 Hot Rolled Coil",
                f"¥{hrc['precio']:,.0f}/ton",
                delta=f"{hrc['cambio_pct']:+.2f}%",
                delta_color="inverse"
            )
            st.caption(f"≈ ${precio_usd:,.0f} USD/ton")
    
    with col2:
        if datos["rebar"]:
            rb = datos["rebar"]
            precio_usd = convertir_cny_a_usd(rb["precio"])
            st.metric(
                "🔩 Rebar",
                f"¥{rb['precio']:,.0f}/ton",
                delta=f"{rb['cambio_pct']:+.2f}%",
                delta_color="inverse"
            )
            st.caption(f"≈ ${precio_usd:,.0f} USD/ton")
    
    with col3:
        if datos["inox"]:
            ss = datos["inox"]
            precio_usd = convertir_cny_a_usd(ss["precio"])
            st.metric(
                "✨ Acero Inoxidable",
                f"¥{ss['precio']:,.0f}/ton",
                delta=f"{ss['cambio_pct']:+.2f}%",
                delta_color="inverse"
            )
            st.caption(f"≈ ${precio_usd:,.0f} USD/ton")
    
    with col4:
        st.metric(
            "📈 Tendencia",
            datos["tendencia"],
            delta="SHFE"
        )
    
    # Alerta importante
    if datos["alerta"]:
        st.markdown("---")
        if "🔴" in datos["alerta"]:
            st.error(f"**ALERTA:** {datos['alerta']}")
        elif "🟢" in datos["alerta"]:
            st.success(f"**OPORTUNIDAD:** {datos['alerta']}")
        else:
            st.info(datos["alerta"])
    
    # Explicación
    with st.expander("ℹ️ ¿Por qué importan estos precios?"):
        st.markdown("""
        **Los precios del Shanghai Futures Exchange (SHFE) son el indicador líder del mercado de acero en China.**
        
        - **HRC (Hot Rolled Coil)**: Si sube >3%, espera que Benxi/Tianjin suban precios en 1-2 semanas
        - **Rebar**: Indicador de demanda de construcción en China
        - **Inox**: Precio base para tubería de acero inoxidable
        
        **Tu ventaja**: Ver estos precios ANTES de que lleguen las cotizaciones de Manuchar te da poder de negociación.
        """)


# ========================================
# FUNCIÓN PARA OBTENER TOKEN DE TUSHARE
# ========================================

def mostrar_instrucciones_tushare():
    """Muestra instrucciones para obtener token de TuShare"""
    
    st.markdown("""
    ### 🔑 Cómo obtener acceso a TuShare (Gratis)
    
    1. **Registrarse**: Ve a [tushare.pro/register](https://tushare.pro/register)
    2. **Verificar email**: Confirma tu cuenta
    3. **Obtener token**: Ve a [tushare.pro/user/token](https://tushare.pro/user/token)
    4. **Agregar a secrets.toml**:
    
    ```toml
    TUSHARE_TOKEN = "tu_token_aqui"
    ```
    
    **Nota**: El plan gratuito tiene límites pero es suficiente para consultas diarias.
    """)
