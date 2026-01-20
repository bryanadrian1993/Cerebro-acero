"""
AKSHARE - Precios de Acero de China (Shanghai Futures Exchange)
================================================================
API gratuita que NO REQUIERE REGISTRO ni token.

Obtiene precios de futuros de:
- rb: Rebar (Varilla corrugada)
- hc: Hot Rolled Coil (Bobina laminada en caliente)
- ss: Stainless Steel (Acero inoxidable)

Documentación: https://akshare.akfamily.xyz/
GitHub: https://github.com/akfamily/akshare
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ========================================
# OBTENER PRECIOS CON AKSHARE
# ========================================

def obtener_precio_acero_shanghai():
    """
    Obtiene precios de futuros de acero del Shanghai Futures Exchange usando AKShare
    
    Contratos principales:
    - RB (Rebar): Varilla corrugada - el más líquido
    - HC (Hot Rolled Coil): Bobina laminada en caliente
    - SS (Stainless Steel): Acero inoxidable
    
    Returns: dict con precios y análisis
    """
    
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
    
    try:
        import akshare as ak
        
        # =============================================
        # REBAR (RB) - Varilla corrugada
        # =============================================
        try:
            # Obtener datos de futuros de Rebar
            df_rb = ak.futures_zh_spot(symbol="螺纹钢", market="上海期货交易所", indicator="日")
            
            if df_rb is not None and len(df_rb) > 0:
                ultimo = df_rb.iloc[-1] if 'date' in df_rb.columns else df_rb.iloc[0]
                resultado["rebar"] = {
                    "precio": float(ultimo.get('close', ultimo.get('收盘价', 3800))),
                    "cambio_pct": float(ultimo.get('pct_chg', ultimo.get('涨跌幅', 0))),
                    "moneda": "CNY/ton",
                    "nombre": "Rebar (Varilla)"
                }
        except Exception as e1:
            print(f"[AKSHARE] Rebar método 1 falló: {e1}")
            # Método alternativo: usar precio spot
            try:
                df_rb = ak.futures_main_sina(symbol="RB0")
                if df_rb is not None and len(df_rb) > 0:
                    ultimo = df_rb.iloc[-1]
                    precio_hoy = float(ultimo['收盘价']) if '收盘价' in df_rb.columns else float(ultimo['close'])
                    precio_ayer = float(df_rb.iloc[-2]['收盘价']) if len(df_rb) > 1 else precio_hoy
                    cambio = ((precio_hoy - precio_ayer) / precio_ayer) * 100 if precio_ayer else 0
                    
                    resultado["rebar"] = {
                        "precio": precio_hoy,
                        "cambio_pct": round(cambio, 2),
                        "moneda": "CNY/ton",
                        "nombre": "Rebar (Varilla)"
                    }
            except Exception as e2:
                print(f"[AKSHARE] Rebar método 2 falló: {e2}")
        
        # =============================================
        # HOT ROLLED COIL (HC)
        # =============================================
        try:
            df_hc = ak.futures_main_sina(symbol="HC0")
            if df_hc is not None and len(df_hc) > 0:
                ultimo = df_hc.iloc[-1]
                precio_hoy = float(ultimo['收盘价']) if '收盘价' in df_hc.columns else float(ultimo['close'])
                precio_ayer = float(df_hc.iloc[-2]['收盘价']) if len(df_hc) > 1 else precio_hoy
                cambio = ((precio_hoy - precio_ayer) / precio_ayer) * 100 if precio_ayer else 0
                
                resultado["hrc"] = {
                    "precio": precio_hoy,
                    "cambio_pct": round(cambio, 2),
                    "moneda": "CNY/ton",
                    "nombre": "Hot Rolled Coil"
                }
        except Exception as e:
            print(f"[AKSHARE] HRC falló: {e}")
        
        # =============================================
        # STAINLESS STEEL (SS)
        # =============================================
        try:
            df_ss = ak.futures_main_sina(symbol="SS0")
            if df_ss is not None and len(df_ss) > 0:
                ultimo = df_ss.iloc[-1]
                precio_hoy = float(ultimo['收盘价']) if '收盘价' in df_ss.columns else float(ultimo['close'])
                precio_ayer = float(df_ss.iloc[-2]['收盘价']) if len(df_ss) > 1 else precio_hoy
                cambio = ((precio_hoy - precio_ayer) / precio_ayer) * 100 if precio_ayer else 0
                
                resultado["inox"] = {
                    "precio": precio_hoy,
                    "cambio_pct": round(cambio, 2),
                    "moneda": "CNY/ton",
                    "nombre": "Stainless Steel"
                }
        except Exception as e:
            print(f"[AKSHARE] SS falló: {e}")
        
        # Si obtuvimos al menos un precio, estamos conectados
        if resultado["hrc"] or resultado["rebar"]:
            resultado["conectado"] = True
            resultado["modo"] = "REAL - SHFE"
            
            # Análisis de tendencia basado en HRC
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
            
    except ImportError:
        print("[AKSHARE] Librería no instalada. Ejecuta: pip install akshare")
    except Exception as e:
        print(f"[AKSHARE] Error general: {e}")
    
    # Si falla todo, usar datos simulados
    return obtener_datos_simulados_shanghai()


def obtener_datos_simulados_shanghai():
    """Datos simulados basados en precios históricos reales del SHFE"""
    
    import random
    
    # Precios base realistas (enero 2025)
    # Rebar: ~3800 CNY/ton
    # HRC: ~4200 CNY/ton
    # Inox: ~16500 CNY/ton
    
    variacion_rb = random.uniform(-2, 2)
    variacion_hc = random.uniform(-2, 2)
    variacion_ss = random.uniform(-1.5, 1.5)
    
    precio_rb = 3800 * (1 + variacion_rb/100)
    precio_hc = 4200 * (1 + variacion_hc/100)
    precio_ss = 16500 * (1 + variacion_ss/100)
    
    if variacion_hc > 1.5:
        tendencia = "SUBIENDO"
        alerta = "🟡 Precio HRC tendencia alcista - Revisar cotizaciones"
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
        st.success("🔗 Conectado a AKShare")
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
            st.success("✅ Conectado a AKShare - Datos reales del SHFE")
        else:
            st.warning("⚠️ Modo simulado - Verificar conexión a internet")
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
        
        ---
        
        **🆓 AKShare es 100% gratuito** - No requiere registro ni API key.
        """)


# ========================================
# OBTENER DATOS HISTÓRICOS
# ========================================

def obtener_historico_hrc(dias=30):
    """Obtiene datos históricos de HRC"""
    try:
        import akshare as ak
        df = ak.futures_main_sina(symbol="HC0")
        if df is not None and len(df) > 0:
            df = df.tail(dias)
            return df
    except:
        pass
    return None


def obtener_historico_rebar(dias=30):
    """Obtiene datos históricos de Rebar"""
    try:
        import akshare as ak
        df = ak.futures_main_sina(symbol="RB0")
        if df is not None and len(df) > 0:
            df = df.tail(dias)
            return df
    except:
        pass
    return None
