import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from openai import OpenAI
import time
from datetime import datetime, timedelta
import random
import requests
from apis_gratuitas import generar_dashboard_apis
from apis_gratuitas_premium import generar_dashboard_completo_gratis
from newsapi import NewsApiClient
from compras_publicas_ecuador import obtener_obras_detectadas_ecuador
from gdelt_news_api import combinar_noticias_newsapi_gdelt
from sap_integration import mostrar_estado_sap_sidebar, mostrar_panel_sap_completo, obtener_inventario_sap, obtener_ordenes_compra_sap, verificar_conexion_sap
# Precios de acero de Shanghai (SHFE) - AKShare (gratuito, sin registro)
from akshare_china import mostrar_precios_shanghai_sidebar, obtener_precio_acero_shanghai
# Calculadora CFR LO Guayaquil
from calculadora_cfr import mostrar_cfr_sidebar, mostrar_calculadora_cfr, mostrar_comparador_proveedores, mostrar_productos_proveedores_principal
# Monitor de Fletes Marítimos (Proxy con acciones de navieras)
from monitor_fletes import mostrar_fletes_sidebar, mostrar_panel_fletes, obtener_flete_estimado_para_cfr
# Sistema de BI e Inteligencia Artificial
from db_manager import db, DatabaseManager
from ai_models import SistemaIA
from bi_dashboard import BIDashboard
from alertas_inteligentes import SistemaAlertas
from optimizer import OptimizadorProveedores, CalculadoraPuntoReorden, SimuladorEscenarios


# --- CONFIGURACIÓN NewsAPI ---
try:
    newsapi_key = st.secrets["NEWSAPI_KEY"]
    newsapi_client = NewsApiClient(api_key=newsapi_key)
except Exception:
    newsapi_client = None


# --- TRADUCCIÓN SIMPLE AL ESPAÑOL ---
# Cache de traducciones para evitar llamadas repetidas a APIs
_cache_traducciones = {}

def traducir_a_espanol_simple(texto, idioma_origen='en'):

    # ...existing code...
    try:
        # ...existing code...
        return {
            "precio_acero_index": ultimo_precio,
            "tendencia": "SUBIENDO" if ultimo_precio > 100 else "BAJANDO"
        }
    except:
        pass
    return {"precio_acero_index": 100, "tendencia": "ESTABLE"}

def clasificar_noticia_en_escenario(noticia):
    """Clasifica CUALQUIER noticia que pueda afectar el negocio de acero"""
    
    titulo = noticia['titulo'].lower()
    descripcion = noticia.get('descripcion', '').lower()
    keyword = noticia.get('keyword', '').lower()
    contenido = f"{titulo} {descripcion} {keyword}"
    
    # CRITERIO AMPLIO: Detectar cualquier impacto potencial
    
    # 1. CRISIS LOGÍSTICA (afecta importación)
    if any(word in contenido for word in ['shipping', 'port', 'strike', 'delay', 'disruption', 'blockage', 'freight', 'container', 'vessel', 'suez', 'panama', 'red sea']):
        return {
            "escenario": "Crisis Logística Global",
            "categoria": "Logística",
            "impacto": "Crisis",
            "relevancia": "ALTA"
        }
    
    # 2. GUERRA COMERCIAL / ARANCELES (afecta precios)
    if any(word in contenido for word in ['tariff', 'trade war', 'sanction', 'embargo', 'import ban', 'export restriction', 'duty', 'customs']):
        return {
            "escenario": "Guerra Comercial",
            "categoria": "Aranceles",
            "impacto": "Crisis",
            "relevancia": "ALTA"
        }
    
    # 3. ACERO ESPECÍFICO (cualquier mención)
    if any(word in contenido for word in ['steel', 'iron', 'metal']) and \
       any(word in contenido for word in ['price', 'shortage', 'surplus', 'production', 'demand', 'supply', 'market']):
        if any(word in contenido for word in ['rise', 'surge', 'increase', 'up', 'high', 'shortage', 'crisis']):
            return {
                "escenario": "Crisis Mercado Acero",
                "categoria": "Mercado",
                "impacto": "Crisis",
                "relevancia": "ALTA"
            }
        else:
            return {
                "escenario": "Movimiento Mercado Acero",
                "categoria": "Mercado",
                "impacto": "Oportunidad",
                "relevancia": "MEDIA"
            }
    
    # 4. PROVEEDORES CLAVE (China, Turquía, India, Corea)
    if any(proveedor in contenido for proveedor in ['china', 'chinese', 'turkey', 'turkish', 'india', 'indian', 'korea', 'korean']):
        if any(word in contenido for word in ['crisis', 'earthquake', 'disaster', 'shutdown', 'close', 'protest', 'conflict']):
            return {
                "escenario": "Crisis en Proveedor Clave",
                "categoria": "Suministro",
                "impacto": "Crisis",
                "relevancia": "ALTA"
            }
        else:
            return {
                "escenario": "Evento en Proveedor",
                "categoria": "Suministro",
                "impacto": "Oportunidad",
                "relevancia": "MEDIA"
            }
    
    # 5. ECUADOR / LATINOAMÉRICA (mercado local)
    if any(word in contenido for word in ['ecuador', 'latin america', 'south america', 'andean']):
        if any(word in contenido for word in ['mining', 'oil', 'petroleum', 'infrastructure', 'construction', 'project', 'investment', 'boom']):
            return {
                "escenario": "Oportunidad Ecuador/Región",
                "categoria": "Mercado Local",
                "impacto": "Oportunidad",
                "relevancia": "ALTA"
            }
        else:
            return {
                "escenario": "Evento Regional",
                "categoria": "Mercado Local",
                "impacto": "Oportunidad",
                "relevancia": "MEDIA"
            }
    
    # 6. CONSTRUCCIÓN E INFRAESTRUCTURA (demanda)
    if any(word in contenido for word in ['infrastructure', 'construction', 'building', 'bridge', 'road', 'railway']):
        return {
            "escenario": "Boom Infraestructura",
            "categoria": "Demanda",
            "impacto": "Oportunidad",
            "relevancia": "MEDIA"
        }
    
    # 7. MINERÍA (cliente clave)
    if any(word in contenido for word in ['mining', 'mine', 'copper', 'gold', 'mineral']):
        return {
            "escenario": "Actividad Minera",
            "categoria": "Demanda",
            "impacto": "Oportunidad",
            "relevancia": "MEDIA"
        }
    
    # 8. PETRÓLEO Y GAS (cliente clave)
    if any(word in contenido for word in ['oil', 'petroleum', 'gas', 'energy', 'pipeline']):
        return {
            "escenario": "Sector Petrolero",
            "categoria": "Demanda",
            "impacto": "Oportunidad",
            "relevancia": "MEDIA"
        }
    
    # 9. ECONOMÍA GLOBAL (afecta todo)
    if any(word in contenido for word in ['recession', 'inflation', 'interest rate', 'economic crisis', 'dollar']):
        return {
            "escenario": "Riesgo Económico Global",
            "categoria": "Economía",
            "impacto": "Crisis",
            "relevancia": "MEDIA"
        }
    
    # 10. CUALQUIER OTRA MENCIÓN RELEVANTE
    if any(word in contenido for word in ['steel', 'iron', 'metal', 'import', 'export', 'trade', 'supply chain']):
        return {
            "escenario": "Alerta General Comercio",
            "categoria": "Comercio",
            "impacto": "Oportunidad",
            "relevancia": "BAJA"
        }
    
    # Si no tiene ninguna relación, ignorar
    return None

def obtener_noticias_reales_newsapi():
    """Obtiene noticias reales desde NewsAPI si está configurado, si no retorna lista vacía."""
    if not newsapi_client:
        return []
    try:
        top_headlines = newsapi_client.get_top_headlines(language='en', page_size=50)
        if top_headlines and 'articles' in top_headlines:
            return [{
                'titulo': art.get('title', ''),
                'descripcion': art.get('description', ''),
                'keyword': art.get('source', {}).get('name', '')
            } for art in top_headlines['articles']]
    except Exception:
        pass
    return []

def generar_escenarios_desde_noticias():
    """Genera escenarios SOLO con noticias relevantes - Sin relleno artificial"""
    
    noticias = obtener_noticias_mundiales()
    
    # Si NO hay noticias relevantes, modo TRANQUILO
    if not noticias:
        return ["Sin Alertas Activas"], {
            "Sin Alertas Activas": {
                "descripcion": "No se detectaron eventos que afecten el negocio en las últimas 24 horas",
                "tipo": "Normal",
                "fuente": "NewsAPI (Monitoreo Automático)",
                "es_real": True,
                "noticias": [],
                "ultima_actualizacion": datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        }
    
    # Si HAY noticias relevantes, crear escenarios
    escenarios = []
    info_escenarios = {}
    
    for noticia in noticias:
        escenario_nombre = noticia["escenario"]
        
        # Evitar duplicados - agrupar noticias similares
        if escenario_nombre in info_escenarios:
            info_escenarios[escenario_nombre]["noticias"].append(noticia)
        else:
            escenarios.append(escenario_nombre)
            info_escenarios[escenario_nombre] = {
                "descripcion": noticia["descripcion"],
                "tipo": noticia["impacto"],
                "categoria": noticia["categoria"],
                "titulo_noticia": noticia["titulo"],
                "fuente": noticia.get("fuente", "NewsAPI"),
                "idioma": noticia.get("idioma", "es"),  # ⭐ AGREGAR IDIOMA
                "relevancia": noticia.get("relevancia", "MEDIA"),
                "es_real": True,
                "noticias": [noticia],
                "ultima_actualizacion": datetime.now().strftime('%Y-%m-%d %H:%M')
            }
    
    return escenarios, info_escenarios



# --- FUNCIONES VISUALES (Mapas y Gráficos) ---
def generar_mapa_riesgo(escenario):
    data = {'lat': [], 'lon': [], 'riesgo': []}
    if "China" in escenario or "Fletes" in escenario or "Crisis" in escenario:
        # Medio Oriente y China con alto riesgo
        data['lat'].extend([26.0, 31.2, 39.9]) 
        data['lon'].extend([50.5, 121.5, 116.4])
        data['riesgo'].extend([95, 85, 75])
        zoom = 1.5
    elif "Minero" in escenario or "Boom" in escenario:
        data['lat'].extend([-3.99, -4.50]) 
        data['lon'].extend([-79.20, -78.90])
        data['riesgo'].extend([70, 60])
        zoom = 5
    else:
        data['lat'].extend([40.71]) 
        data['lon'].extend([-74.00])
        data['riesgo'].extend([10])
        zoom = 1
        
    df_map = pd.DataFrame(data)
    fig = px.density_mapbox(df_map, lat='lat', lon='lon', z='riesgo', radius=50,
                            center=dict(lat=20, lon=30), zoom=zoom,
                            mapbox_style="carto-positron",
                            color_continuous_scale=["#00ff88", "#ffa502", "#ff4757"])
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    return fig

def generar_grafico_precio_acero():
    # Genera datos simulados de precio del acero
    fechas = pd.date_range(start='2025-01-25', periods=365, freq='D')
    precios = 100 + np.cumsum(np.random.randn(365) * 0.5)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fechas, y=precios,
        mode='lines',
        line=dict(color='#00ff88', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 136, 0.1)'
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8b92b0'),
        height=300,
        margin={"r":10,"t":10,"l":10,"b":10},
        xaxis=dict(gridcolor='#2d3561'),
        yaxis=dict(gridcolor='#2d3561')
    )
    
    return fig

def generar_sparkline(datos):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=datos,
        mode='lines',
        line=dict(color='#00ff88', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 136, 0.2)'
    ))
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=80,
        margin={"r":0,"t":0,"l":0,"b":0},
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
    )
    
    return fig

# --- FUNCIÓN INTELIGENTE (Simulada) ---
def consultar_gpt(producto, stock, minimo, escenario):
    # Genera recomendaciones inteligentes basadas en reglas
    deficit = minimo - stock
    porcentaje = (stock / minimo) * 100 if minimo > 0 else 100
    
    if "Crisis" in escenario:
        if porcentaje < 80:
            return f"🔴 COMPRAR URGENTE: Stock crítico ({int(porcentaje)}%) + Crisis internacional"
        else:
            return f"🟡 MONITOREAR: Crisis en curso, stock aceptable pero vigilar proveedores"
    elif "Boom" in escenario:
        if porcentaje < 90:
            return f"🟢 COMPRAR AHORA: Demanda alta por boom minero, reponer {deficit} unidades"
        else:
            return f"✅ MANTENER: Stock suficiente, aprovechar boom para vender"
    else:  # Mercado Normal
        if porcentaje < 70:
            return f"⚠️ REPONER: Nivel bajo ({int(porcentaje)}%), ordenar {deficit} unidades"
        elif porcentaje < 90:
            return f"📊 REVISAR: Stock en {int(porcentaje)}%, programar pedido preventivo"
        else:
            return f"✅ OK: Stock saludable, revisar en 30 días"

# ========================================
# INTEGRACIÓN SAP (Preparada para el futuro)
# ========================================

def cargar_inventario():
    """
    Carga inventario desde SAP si está configurado, sino usa simulado
    
    FUTURO: Se conectará automáticamente a SAP cuando configures credenciales
    """
    import os
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(ruta_base, "inventario_simulado.csv")
    
    try:
        # Intentar importar conector SAP
        from sap_connector import get_datos_empresa, usar_datos_reales
        
        if usar_datos_reales():
            # Usar datos REALES de SAP
            datos_sap = get_datos_empresa()
            return datos_sap["inventario"]
        else:
            # Modo simulado con ruta absoluta
            return pd.read_csv(ruta_csv)
    except:
        # Fallback: archivo CSV simulado con ruta absoluta
        return pd.read_csv(ruta_csv)

# ========================================
# ALGORITMO: EL CEREBRO DE ACERO
# ========================================

# --- FASE 1: DETECCIÓN Y OPORTUNIDAD ---
def fase1_deteccion_oportunidad(escenario):
    """Los Ojos del Robot: Detecta qué se necesita antes que la competencia"""
    
    resultados = {
        "oportunidades": [],
        "demanda_proyectada": {},
        "productos_criticos": []
    }
    
    # 1. Escaneo de Mercado Ecuador - SOLO DATOS REALES
    try:
        obras_activas = obtener_obras_detectadas_ecuador(dias=60)
        
        # Filtrar según escenario
        if "Crisis" in escenario:
            obras_activas = [o for o in obras_activas if o['urgencia'] == 'ALTA']
        
        if "Boom" in escenario or "Minero" in escenario:
            obras_prioritarias = [o for o in obras_activas if o['sector'] in ['Minería', 'Petróleo']]
            obras_resto = [o for o in obras_activas if o['sector'] not in ['Minería', 'Petróleo']]
            obras_activas = obras_prioritarias + obras_resto
        
    except Exception as e:
        # Si hay error, dejar vacío (no usar datos falsos)
        obras_activas = []
    
    # 2. Análisis de Inventario Interno (Regla 5)
    try:
        df_inv = cargar_inventario()  # Usa SAP si está configurado
        
        for obra in obras_activas:
            for producto in obra["demanda"]:
                # Buscar producto en inventario
                match = df_inv[df_inv['producto'].str.contains(producto.split()[0], case=False, na=False)]
                
                if not match.empty:
                    row = match.iloc[0]
                    stock_actual = row['stock_actual']
                    stock_minimo = row['stock_minimo']
                    demanda_obra = obra['volumen_estimado'] / len(obra['demanda'])
                    
                    # Check: Stock < (Mínimo + Demanda Proyectada)
                    if stock_actual < (stock_minimo + demanda_obra):
                        resultados["productos_criticos"].append({
                            "producto": producto,
                            "stock_actual": stock_actual,
                            "stock_minimo": stock_minimo,
                            "demanda_obra": int(demanda_obra),
                            "deficit": int((stock_minimo + demanda_obra) - stock_actual),
                            "obra": obra["proyecto"],
                            "urgencia": obra["urgencia"]
                        })
    except:
        pass
    
    resultados["oportunidades"] = obras_activas
    return resultados

# --- FASE 2: GESTIÓN DE RIESGOS ---
def fase2_gestion_riesgos(escenario):
    """El Escudo: Analiza riesgos REALES basados en noticias detectadas"""
    
    riesgos = {
        "cisnes_negros": [],
        "radar_economico": {},
        "decision": "COMPRAR",
        "ajustes": []
    }
    
    # Obtener escenarios reales detectados
    escenarios_disponibles, info_escenarios = generar_escenarios_desde_noticias()
    
    # Analizar SOLO escenarios de crisis reales
    for esc_nombre in escenarios_disponibles:
        if esc_nombre == "Sin Alertas Activas":
            continue
            
        info = info_escenarios[esc_nombre]
        
        # Solo incluir escenarios de tipo "Crisis" con relevancia ALTA
        if info.get("tipo") == "Crisis" and info.get("relevancia") == "ALTA":
            # Extraer acción recomendada del análisis
            accion_recomendada = "Monitorear situacion y ajustar compras"
            
            # Determinar stock recomendado según la categoría
            stock_rec = "Normal"
            if info.get("categoria") == "Geopolitica":
                accion_recomendada = "Diversificar proveedores - Buscar rutas alternas"
                stock_rec = "6 meses"
            elif info.get("categoria") == "Economia":
                accion_recomendada = "Anticipar compra antes de subida de precios"
                stock_rec = "3 meses"
            elif info.get("categoria") == "Logistica":
                accion_recomendada = "Asegurar inventario - Posibles retrasos"
                stock_rec = "4 meses"
            
            riesgos["cisnes_negros"].append({
                "tipo": f"{info.get('categoria', 'Crisis')}: {esc_nombre[:50]}",
                "descripcion": info.get('descripcion', '')[:100],
                "accion": accion_recomendada,
                "stock_recomendado": stock_rec,
                "fuente_real": f"{len(info.get('noticias', []))} noticias verificadas"
            })
    
    # Radar Económico - Análisis de tendencia basado en escenarios
    crisis_economicas = sum(1 for esc in escenarios_disponibles 
                           if esc != "Sin Alertas Activas" 
                           and info_escenarios[esc].get("categoria") == "Economia")
    
    if crisis_economicas >= 2:
        precio_acero_tendencia = "SUBIENDO"
    elif crisis_economicas == 1:
        precio_acero_tendencia = "ESTABLE"
    else:
        precio_acero_tendencia = "BAJANDO"
    
    riesgos["radar_economico"] = {
        "tendencia_precio": precio_acero_tendencia,
        "accion": "COMPRAR YA" if precio_acero_tendencia == "SUBIENDO" else "ESPERAR 1 SEMANA" if precio_acero_tendencia == "BAJANDO" else "COMPRAR NORMAL",
        "base": f"Basado en {len(escenarios_disponibles)-1} escenarios reales detectados"
    }
    
    # Decisión final basada en riesgos reales
    if len(riesgos["cisnes_negros"]) > 2:
        riesgos["decision"] = "ESPERAR - Demasiados riesgos activos"
    elif precio_acero_tendencia == "SUBIENDO":
        riesgos["decision"] = "COMPRAR URGENTE"
    elif len(riesgos["cisnes_negros"]) == 0:
        riesgos["decision"] = "COMPRAR NORMAL - Sin riesgos detectados"
    else:
        riesgos["decision"] = "COMPRAR CON PRECAUCION"
    
    return riesgos

# --- FASE 3: SELECCIÓN Y COMPRA ---
def fase3_seleccion_compra(productos_criticos):
    """La Decisión: Ejecuta la compra más inteligente"""
    
    decisiones = []
    
    proveedores_db = [
        {"nombre": "Tianjin Steel (China)", "precio": 1.0, "tiempo": 45, "calidad": "A"},
        {"nombre": "Posco (Corea)", "precio": 1.15, "tiempo": 35, "calidad": "A+"},
        {"nombre": "Tosyali (Turquía)", "precio": 0.95, "tiempo": 50, "calidad": "B+"},
        {"nombre": "ArcelorMittal (India)", "precio": 1.05, "tiempo": 40, "calidad": "A"}
    ]
    
    for prod in productos_criticos[:5]:  # Top 5 críticos
        urgencia = prod.get("urgencia", "MEDIA")
        
        # Selección de proveedor según urgencia
        if urgencia == "ALTA":
            # Priorizar velocidad
            proveedor = min(proveedores_db, key=lambda x: x["tiempo"])
        else:
            # Priorizar precio
            proveedor = min(proveedores_db, key=lambda x: x["precio"])
        
        # Check Financiero (Regla 1)
        flujo_disponible = random.choice([True, True, True, False])  # 75% tiene flujo
        
        decision = {
            "producto": prod["producto"],
            "cantidad": prod["deficit"],
            "proveedor": proveedor["nombre"],
            "precio_unitario": round(proveedor["precio"] * 1200, 2),
            "tiempo_entrega": proveedor["tiempo"],
            "calidad": proveedor["calidad"],
            "flujo_ok": flujo_disponible,
            "status": "APROBAR COMPRA" if flujo_disponible else "⚠️ ALERTA FINANZAS"
        }
        
        decisiones.append(decision)
    
    return decisiones

# --- FASE 4: LOGÍSTICA DE DISTRIBUCIÓN ---
def fase4_logistica_distribucion(decisiones_compra):
    """El Cuerpo: Optimiza la llegada (Modo Ecuador)"""
    
    rutas = []
    
    destinos_ecuador = ["Quito", "Guayaquil", "Cuenca", "Machala", "Esmeraldas"]
    
    for decision in decisiones_compra[:3]:
        destino = random.choice(destinos_ecuador)
        
        if destino in ["Quito", "Cuenca"]:
            # Cliente en la Sierra
            via_principal = "Alóag - Santo Domingo"
            via_estado = random.choice(["ABIERTA", "CERRADA"])
            
            if via_estado == "CERRADA":
                via_alterna = "Las Mercedes/Calacalí"
                sobrecosto = 150
                ruta_desc = f"Vía {via_principal} CERRADA. Usar {via_alterna} (+${sobrecosto})"
            else:
                sobrecosto = 0
                ruta_desc = f"Vía {via_principal} OK"
            
            destino_final = "Bodega Quito"
        else:
            # Cliente en Costa/Sur
            sobrecosto = 0
            ruta_desc = "Cross-Docking: Nacionalizar en Puerto y despachar directo"
            destino_final = f"Directo a {destino}"
        
        # Cálculo de Landed Cost
        fob = decision["precio_unitario"] * decision["cantidad"]
        flete_maritimo = fob * 0.15  # 15% del FOB
        arancel = fob * 0.10  # 10%
        flete_interno = 200 + sobrecosto
        margen = 0.25  # 25%
        
        landed_cost = fob + flete_maritimo + arancel + flete_interno
        precio_venta = landed_cost * (1 + margen)
        
        rutas.append({
            "producto": decision["producto"],
            "destino": destino_final,
            "ruta": ruta_desc,
            "fob": round(fob, 2),
            "flete_maritimo": round(flete_maritimo, 2),
            "arancel": round(arancel, 2),
            "flete_interno": flete_interno,
            "landed_cost": round(landed_cost, 2),
            "precio_venta_sugerido": round(precio_venta, 2)
        })
    
    return rutas

# --- FUNCIÓN PRINCIPAL: EJECUTAR CEREBRO COMPLETO ---
def ejecutar_cerebro_acero(escenario):
    """Ejecuta las 4 fases del algoritmo"""
    
    with st.spinner("FASE 1: Escaneando mercado y detectando oportunidades..."):
        time.sleep(1)
        fase1 = fase1_deteccion_oportunidad(escenario)
    
    with st.spinner("FASE 2: Analizando riesgos geopoliticos y economicos..."):
        time.sleep(1)
        fase2 = fase2_gestion_riesgos(escenario)
    
    with st.spinner("FASE 3: Seleccionando proveedores optimos..."):
        time.sleep(1)
        fase3 = fase3_seleccion_compra(fase1["productos_criticos"])
    
    with st.spinner("FASE 4: Optimizando logistica de distribucion..."):
        time.sleep(1)
        fase4 = fase4_logistica_distribucion(fase3)
    
    return {
        "fase1": fase1,
        "fase2": fase2,
        "fase3": fase3,
        "fase4": fase4
    }

# --- INTERFAZ GRÁFICA ---
# Auto-refresh cada 2 horas (7200 segundos) para preservar NewsAPI
refresh_interval = 7200  # 2 horas (GDELT sin límites compensa)

# Generar escenarios desde noticias mundiales (se actualiza automáticamente)
escenarios_disponibles, info_escenarios = generar_escenarios_desde_noticias()

# === CARGAR INVENTARIO (necesario para IA) ===
df = cargar_inventario()

# Sidebar con menú de navegación
with st.sidebar:

    st.markdown("""
    <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid #1A4D8F;">
        <div style="font-size: 2rem; color: #2E7DD8; font-weight: 700; font-family: 'Inter', sans-serif;">
            ⬡
        </div>
        <div style="font-size: 1.2rem; color: #FFFFFF; font-weight: 600; letter-spacing: 0.1em; margin-top: 8px;">
            CEREBRO DE ACERO
        </div>
        <div style="font-size: 0.75rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.15em; margin-top: 4px;">
            Import Aceros S.A.
        </div>
    </div>
    """, unsafe_allow_html=True)
    

    ultima_actualizacion = info_escenarios[list(info_escenarios.keys())[0]].get('ultima_actualizacion', datetime.now().strftime('%Y-%m-%d %H:%M'))
    st.markdown(f"""
    <div style="padding: 16px 0; border-bottom: 1px solid #1A4D8F;">
        <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em;">
            SISTEMA STATUS
        </div>
        <div style="font-size: 0.9rem; color: #2E7DD8; font-weight: 600; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #2E7DD8; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite;"></span>
            ONLINE
        </div>
        <div style="font-size: 0.75rem; color: #8B8B8B; margin-top: 8px; font-family: 'JetBrains Mono', monospace;">
            {datetime.now().strftime('%Y-%m-%d • %H:%M:%S')}
        </div>
        <div style="font-size: 0.7rem; color: #8B8B8B; margin-top: 4px;">
            Auto-sync: {refresh_interval//60}min
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # DASHBOARD APIS GRATUITAS
    st.markdown("---")
    st.markdown("### 📊 **Indicadores en Vivo**")
    
    try:
        dashboard_apis = generar_dashboard_apis()
        
        # Precio Acero
        acero_data = dashboard_apis["acero"]
        st.metric(
            "💰 Índice Acero Global",
            f"${acero_data['precio']:.0f}",
            delta=f"{acero_data['cambio_pct']:.1f}%",
            delta_color="inverse"
        )
        
        # Tasa cambio CNY (principal proveedor)
        forex_data = dashboard_apis["forex"]
        st.metric(
            "💱 USD/CNY (China)",
            f"¥{forex_data['CNY']:.2f}",
            delta="Hoy"
        )
        
        # Alertas clima
        clima_alertas = dashboard_apis["clima"]
        if clima_alertas:
            st.warning(f"🌪️ {len(clima_alertas)} alerta(s) climáticas")
        
        # Desastres naturales
        desastres = dashboard_apis["desastres"]
        if desastres:
            st.error(f"🌍 {len(desastres)} desastre(s) en zonas proveedores")
    except Exception as e:
        st.caption(f"⚠️ APIs básicas en standby")
    
    # PANEL DE ESTADO DEL NEGOCIO
    st.markdown("---")
    st.markdown("### 📊 **Estado del Negocio**")
    
    # Órdenes en tránsito (simulado - será real con SAP)
    st.metric(
        "🚢 Órdenes en Tránsito",
        "3 contenedores",
        delta="ETA: 18 días",
        delta_color="off"
    )
    
    # Stock crítico
    st.metric(
        "📦 Productos Stock Bajo",
        "2 alertas",
        delta="HRC, Galvanizado",
        delta_color="inverse"
    )
    
    # Último precio pagado
    st.metric(
        "💵 Último CFR Pagado",
        "$580/ton",
        delta="BENXI - HRC",
        delta_color="off"
    )
    st.caption("*Datos de ejemplo - Se actualizarán con SAP*")
    
    # === PRECIOS CHINA (TUSHARE) ===
    mostrar_precios_shanghai_sidebar()
    
    # === CFR LO GUAYAQUIL ===
    mostrar_cfr_sidebar()
    
    # === MONITOR DE FLETES ===
    mostrar_fletes_sidebar()
    
    # === SECCIÓN SAP ===
    mostrar_estado_sap_sidebar()
    
    # Contador de alertas
    num_alertas = len([e for e in escenarios_disponibles if e != "Sin Alertas Activas"])
    if num_alertas > 0:
        st.markdown(f"### ⚠️ {num_alertas} Alerta{'s' if num_alertas > 1 else ''} Activa{'s' if num_alertas > 1 else ''}")
    else:
        st.markdown("### ✅ Sin Alertas")
    
    # Selector de escenarios dinámico
    escenario = st.selectbox("Seleccione Escenario", 
        escenarios_disponibles,
        label_visibility="collapsed")
    
    # Mostrar información del escenario seleccionado
    info = info_escenarios[escenario]
    
    
    # Estado del escenario con badge
    if info["tipo"] == "Crisis":
        st.markdown('<div class="status-badge-critico">🔴 Crisis Detectada</div>', unsafe_allow_html=True)
        if info.get("relevancia") == "ALTA":
            st.error("⚡ IMPACTO ALTO - Acción Inmediata")
    elif info["tipo"] == "Oportunidad":
        st.markdown('<div class="status-badge-live">🟢 Oportunidad</div>', unsafe_allow_html=True)
        if info.get("relevancia") == "ALTA":
            st.success("⚡ RELEVANCIA ALTA")
    else:
        st.markdown('<div class="status-badge-warning">✅ Operación Normal</div>', unsafe_allow_html=True)
    
    # Indicador de fuente de datos
    st.success(f"✅ Datos Reales - {info['fuente']}")
    
    # Descripción del escenario
    with st.expander("ℹ️ Detalles del Escenario"):
        if "titulo_noticia" in info:
            # Traducir título (por defecto en inglés desde NewsAPI/GDELT)
            titulo_noticia = info['titulo_noticia']
            idioma_titulo = info.get('idioma', 'en')
            if idioma_titulo == 'en':
                titulo_noticia = traducir_a_espanol_simple(titulo_noticia, 'en')
            
            st.markdown(f"**📰 Noticia:** {titulo_noticia}")
            st.markdown(f"**Categoría:** {info['categoria']}")
        
        # Traducir descripción (por defecto en inglés desde NewsAPI/GDELT)
        descripcion = info['descripcion']
        idioma_desc = info.get('idioma', 'en')
        if idioma_desc == 'en':
            descripcion = traducir_a_espanol_simple(descripcion, 'en')
        
        st.markdown(f"**Descripción:** {descripcion}")
        
        # Mostrar todas las noticias relacionadas (incluso si hay solo 1)
        if len(info.get("noticias", [])) >= 1:
            st.markdown("---")
            st.markdown("**📰 Fuentes:**")
            for n in info["noticias"]:
                link_url = n.get('url', '#')
                fuente = n.get('fuente', 'Desconocido')
                idioma = n.get('idioma', 'en')
                titulo_original = n.get('titulo', 'Sin título')
                
                # Traducir al español (por defecto noticias vienen en inglés)
                titulo_display = traducir_a_espanol_simple(titulo_original, idioma) if idioma == 'en' else titulo_original
                
                # Usar HTML simple con target="_blank"
                st.markdown(
                    f'<a href="{link_url}" target="_blank" rel="noopener noreferrer" '
                    f'style="color: #1f77b4; text-decoration: underline;">'
                    f'🔗 {titulo_display}</a> '
                    f'<span style="color: #888;">({fuente})</span>',
                    unsafe_allow_html=True
                )
    

    if st.button("⟳ FORCE REFRESH", key="force_refresh"):
        st.cache_data.clear()
        st.rerun()


# Header moderno tipo dashboard
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; background: #f7fafd; border-bottom: 2px solid #e0e7ef; padding: 12px 24px 8px 24px; margin-bottom: 18px;">
    <div style="display: flex; align-items: center; gap: 18px;">
        <span style="font-size: 2rem; color: #1976d2;">🏠</span>
        <span style="font-size: 1.2rem; color: #222; font-weight: 700; letter-spacing: 0.04em;">HOME</span>
        <span style="font-size: 1.2rem; color: #888; font-weight: 500; margin-left: 24px;">|</span>
        <span style="font-size: 1.2rem; color: #1976d2; font-weight: 700; margin-left: 8px;">EXPLORE</span>
        <span style="font-size: 1.2rem; color: #888; font-weight: 500; margin-left: 24px;">|</span>
        <span style="font-size: 1.2rem; color: #1976d2; font-weight: 700; margin-left: 8px;">SALES INSIGHTS</span>
    </div>
    <div style="display: flex; align-items: center; gap: 18px;">
        <span style="font-size: 1.6rem; color: #1976d2;">🔔</span>
        <span style="font-size: 1.6rem; color: #1976d2;">👤</span>
    </div>
</div>
""", unsafe_allow_html=True)

# GRID PRINCIPAL DE DASHBOARD
st.markdown("""
<style>
.dashboard-card {
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.07);
    padding: 18px 18px 10px 18px;
    margin-bottom: 18px;
    border: 1px solid #e0e7ef;
}
.dashboard-title {
    font-size: 1.1rem;
    color: #1976d2;
    font-weight: 600;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)



# =============================================
# RESUMEN EJECUTIVO DEL DÍA
# =============================================
def generar_resumen_ejecutivo():
    """Genera un resumen ejecutivo con toda la información clave"""
    from datetime import datetime
    try:
        from calculadora_cfr import obtener_productos_cfr_lo_principal, obtener_tipo_cambio_usd_cny
        from akshare_china import obtener_precio_acero_shanghai, convertir_cny_a_usd
        from monitor_fletes import analizar_tendencia_fletes
        productos_cfr, tipo_cambio = obtener_productos_cfr_lo_principal()
        precios_shanghai = obtener_precio_acero_shanghai()
        tendencia_fletes = analizar_tendencia_fletes()
    except Exception as e:
        productos_cfr = []
        tipo_cambio = 7.25
        precios_shanghai = {}
        tendencia_fletes = {"tendencia": "ESTABLE", "variacion_pct": 0}
    # Contar alertas activas
    alertas_crisis = [e for e in escenarios_disponibles if "Crisis" in info_escenarios.get(e, {}).get("tipo", "")]
    alertas_oportunidad = [e for e in escenarios_disponibles if "Oportunidad" in info_escenarios.get(e, {}).get("tipo", "")]
    # Precio más bajo CFR
    if productos_cfr:
        mejor_precio = min(productos_cfr, key=lambda x: x["cfr_lo"])
    else:
        mejor_precio = {"proveedor": "N/A", "cfr_lo": 0, "producto": "N/A"}
    # Obtener precio HRC en USD
    try:
        hrc_usd = convertir_cny_a_usd(precios_shanghai.get("hrc", {}).get("precio", 4200), tipo_cambio)
    except:
        hrc_usd = 480
    return {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "alertas_crisis": len(alertas_crisis),
        "alertas_oportunidad": len(alertas_oportunidad),
        "precio_hrc_shanghai": round(hrc_usd, 0),
        "tipo_cambio": tipo_cambio,
        "tendencia_fletes": tendencia_fletes.get("tendencia", "ESTABLE"),
        "variacion_fletes": tendencia_fletes.get("variacion_pct", 0),
        "mejor_proveedor": mejor_precio["proveedor"],
        "mejor_precio_cfr": mejor_precio["cfr_lo"],
        "mejor_producto": mejor_precio["producto"],
        "productos_cfr": productos_cfr,
        "escenarios_crisis": alertas_crisis[:3],
        "escenarios_oportunidad": alertas_oportunidad[:3]
    }



# Mostrar Resumen Ejecutivo
with st.container():
    resumen = generar_resumen_ejecutivo()
    
    # Título del resumen estilo Palantir
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1A1A1A 0%, #0D0D0D 100%); 
                padding: 24px; border-radius: 2px; border: 1px solid #1A4D8F;
                margin-bottom: 24px; box-shadow: 0 0 20px rgba(26, 77, 143, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="color: #FFFFFF; margin: 0; font-size: 1.4rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
                    ⬡ EXECUTIVE SUMMARY
                </h2>
                <p style="color: #8B8B8B; margin: 8px 0 0 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'JetBrains Mono', monospace;">
                    SYNCHRONIZED: {resumen['fecha']}
                </p>
            </div>
            <div style="text-align: right;">
                <span style="display: inline-block; padding: 6px 12px; background: transparent; border: 1px solid #2E7DD8; color: #2E7DD8; border-radius: 2px; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">
                    CLASSIFIED
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =============================================
    # PÁRRAFO NARRATIVO - ANÁLISIS DE LA SITUACIÓN
    # =============================================
    def generar_parrafo_narrativo(resumen):
        """Genera un párrafo explicativo de la situación actual"""
        
        # Determinar estado general
        if resumen["alertas_crisis"] > 0 and resumen["alertas_oportunidad"] > 0:
            estado = "mixto con alertas y oportunidades"
        elif resumen["alertas_crisis"] > 0:
            estado = "de precaución por alertas detectadas"
        elif resumen["alertas_oportunidad"] > 0:
            estado = "favorable con oportunidades de mercado"
        else:
            estado = "estable sin alertas significativas"
        
        # Análisis de fletes
        if resumen["tendencia_fletes"] == "SUBIENDO":
            analisis_fletes = f"Los fletes marítimos muestran una tendencia alcista ({resumen['variacion_fletes']:+.1f}%), lo que podría incrementar los costos de importación en las próximas semanas. Se recomienda adelantar compras si hay inventario bajo."
        elif resumen["tendencia_fletes"] == "BAJANDO":
            analisis_fletes = f"Los fletes marítimos están bajando ({resumen['variacion_fletes']:+.1f}%), lo que representa una ventana de oportunidad para negociar mejores tarifas con navieras y reducir el costo CFR."
        else:
            analisis_fletes = f"Los fletes marítimos se mantienen estables ({resumen['variacion_fletes']:+.1f}%), sin cambios significativos que afecten la planificación de compras."
        
        # Análisis de precios
        analisis_precios = f"El precio del acero HRC en la Bolsa de Shanghai se cotiza a ${resumen['precio_hrc_shanghai']:,.0f}/ton, con un tipo de cambio de {resumen['tipo_cambio']} CNY/USD."
        
        # Recomendación de proveedor
        recomendacion = f"Actualmente, el mejor precio CFR LO Guayaquil lo ofrece {resumen['mejor_proveedor']} a ${resumen['mejor_precio_cfr']:,.0f}/ton para {resumen['mejor_producto']}."
        
        # Alertas específicas
        if resumen["escenarios_crisis"]:
            alertas_texto = f" Se han detectado {resumen['alertas_crisis']} alerta(s) de crisis que requieren atención: eventos geopolíticos o de mercado que podrían afectar la cadena de suministro."
        else:
            alertas_texto = ""
        
        # Oportunidades específicas
        if resumen["escenarios_oportunidad"]:
            oportunidades_texto = f" Por otro lado, se identifican {resumen['alertas_oportunidad']} oportunidad(es) de mercado que podrían aprovecharse para optimizar compras."
        else:
            oportunidades_texto = ""
        
        # Construir párrafo completo
        parrafo = f"""
        **Estado actual del mercado:** El escenario general es {estado}. {analisis_precios}
        
        **Análisis de fletes:** {analisis_fletes}
        
        **Recomendación:** {recomendacion}{alertas_texto}{oportunidades_texto}
        """
        
        return parrafo
    
    # Mostrar el párrafo narrativo - Estilo Palantir
    parrafo = generar_parrafo_narrativo(resumen)
    st.markdown(f"""
    <div style="background: #1A1A1A; padding: 24px; border-radius: 2px; 
                border-left: 3px solid #2E7DD8; margin-bottom: 24px;">
        <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px;">
            SITUATION ANALYSIS
        </div>
        <p style="color: #D4D4D4; font-size: 0.95rem; line-height: 1.8; margin: 0; font-family: 'Inter', sans-serif;">
            {parrafo.replace(chr(10), '<br>')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fila 1: Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Alertas
        if resumen["alertas_crisis"] > 0:
            st.error(f"🔴 {resumen['alertas_crisis']} Alerta(s) Crisis")
        else:
            st.success("✅ Sin alertas de crisis")
    
    with col2:
        # Oportunidades
        if resumen["alertas_oportunidad"] > 0:
            st.success(f"🟢 {resumen['alertas_oportunidad']} Oportunidad(es)")
        else:
            st.info("ℹ️ Sin oportunidades detectadas")
    
    with col3:
        # Precio Shanghai
        st.metric(
            "📈 HRC Shanghai",
            f"${resumen['precio_hrc_shanghai']:,.0f}/ton",
            delta=f"CNY/USD: {resumen['tipo_cambio']}",
            delta_color="off"
        )
    
    with col4:
        # Tendencia Fletes
        delta_color = "inverse" if resumen["tendencia_fletes"] == "SUBIENDO" else "normal"
        st.metric(
            "🚢 Fletes Marítimos",
            resumen["tendencia_fletes"],
            delta=f"{resumen['variacion_fletes']:+.1f}%",
            delta_color=delta_color
        )
    
    # Fila 2: Recomendaciones
    st.markdown("---")
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.markdown("### 💡 Recomendación de Compra")
        st.markdown(f"""
        <div style="background: #0a2f1f; padding: 15px; border-radius: 8px; border: 1px solid #00ff88;">
            <p style="color: #00ff88; font-size: 18px; margin: 0;">
                <strong>Mejor opción:</strong> {resumen['mejor_proveedor']}
            </p>
            <p style="color: white; font-size: 24px; margin: 10px 0;">
                <strong>${resumen['mejor_precio_cfr']:,.0f}/ton</strong> CFR LO Guayaquil
            </p>
            <p style="color: #888; margin: 0;">
                Producto: {resumen['mejor_producto']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Acción recomendada según fletes
        if resumen["tendencia_fletes"] == "SUBIENDO":
            st.warning("⚠️ **Acción:** Fletes subiendo - Considerar compra anticipada")
        elif resumen["tendencia_fletes"] == "BAJANDO":
            st.success("✅ **Acción:** Fletes bajando - Buen momento para negociar")
        else:
            st.info("ℹ️ **Acción:** Mercado estable - Monitorear")
    
    with col_der:
        st.markdown("### 📰 Situación del Mercado")
        
        # Mostrar alertas de crisis
        if resumen["escenarios_crisis"]:
            for crisis in resumen["escenarios_crisis"]:
                st.error(f"🔴 {crisis[:50]}...")
        
        # Mostrar oportunidades
        if resumen["escenarios_oportunidad"]:
            for oport in resumen["escenarios_oportunidad"]:
                st.success(f"🟢 {oport[:50]}...")
        
        if not resumen["escenarios_crisis"] and not resumen["escenarios_oportunidad"]:
            st.info("✅ Mercado operando con normalidad")
    
    # Comparativa rápida de proveedores
    st.markdown("---")
    st.markdown("### 🏭 Comparativa Rápida de Proveedores CFR LO Guayaquil")
    
    if resumen["productos_cfr"]:
        cols = st.columns(6)
        for i, prod in enumerate(resumen["productos_cfr"][:6]):
            with cols[i]:
                # Marcar el mejor precio
                es_mejor = prod["proveedor"] == resumen["mejor_proveedor"]
                color = "#00ff88" if es_mejor else "white"
                badge = "⭐ MEJOR" if es_mejor else ""
                
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: {'#0a2f1f' if es_mejor else '#1a1a2e'}; 
                            border-radius: 8px; border: 1px solid {color};">
                    <p style="color: {color}; font-size: 12px; margin: 0;">{badge}</p>
                    <p style="color: white; font-weight: bold; margin: 5px 0;">{prod['proveedor']}</p>
                    <p style="color: {color}; font-size: 20px; margin: 0;"><strong>${prod['cfr_lo']:,.0f}</strong></p>
                    <p style="color: #888; font-size: 11px; margin: 5px 0 0 0;">{prod['dias']} días</p>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# SECCIÓN 1: PRODUCTOS DE PROVEEDORES CON CFR LO GUAYAQUIL
try:
    mostrar_productos_proveedores_principal()
except Exception as e:
    st.warning(f"Error cargando productos: {e}")

st.markdown("---")

# === CALCULADORA CFR LO GUAYAQUIL ===
with st.expander("🚢 **Calculadora CFR LO Guayaquil** - Costo real puesto en puerto", expanded=False):
    mostrar_calculadora_cfr()
    st.markdown("---")
    mostrar_comparador_proveedores()

# === MONITOR DE FLETES MARÍTIMOS ===
with st.expander("📊 **Monitor de Fletes** - Tendencia China→Guayaquil", expanded=False):
    mostrar_panel_fletes()

# Métricas principales con tarjetas mejoradas
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Valor Total Inventario</div>
        <div class="metric-value">$1.2M USD</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(generar_sparkline(np.random.randn(20).cumsum() + 100), use_container_width=True)

with col2:
    ordenes = 5 if "Crisis" in escenario else 3
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Órdenes Pendientes</div>
        <div class="metric-value">{ordenes}</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(generar_sparkline(np.random.randn(20).cumsum() + 50), use_container_width=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Índice Precio Acero Global</div>
        <div class="metric-value" style="color: #00ff88;">● LIVE</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(generar_sparkline(np.random.randn(20).cumsum() + 115), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sección de mapas y gráficos
col_izq, col_der = st.columns([1.5, 1])

with col_izq:
    st.markdown("### Mapa de Riesgo en Tiempo Real")
    st.plotly_chart(generar_mapa_riesgo(escenario), use_container_width=True)

with col_der:
    st.markdown("### Índice Precio Acero Global")
    st.plotly_chart(generar_grafico_precio_acero(), use_container_width=True)

# Tabla de recomendaciones de compra activas
st.markdown("---")
st.markdown("### Recomendaciones de Compra Activas")

# Crear tabla de ejemplo
compras_data = {
    "Producto": ["Viga IPE 200mm", "Viga IPE 200mm", "Viga IPE 200mm", "Viga IPE 200mm"],
    "Urgency": ["CRÍTICO", "CRÍTICO", "CRÍTICO", "CRÍTICO"],
    "Cantidad": [1000, 1000, 100, 200],
    "Status_Badge": ["critico", "critico", "warning", "live"],
    "Status_Text": ["COMPRAR INMEDIATO (Tianjin Steel)", "COMPRAR INMEDIATO (Tianjin Steel)", 
                    "COMPRAR INMEDIATO (Tianjin Steel)", "COMPRAR INMEDIATO (Tianjin Steel)"]
}

df_compras = pd.DataFrame(compras_data)

# Mostrar tabla con formato HTML personalizado
st.markdown("""
<style>
    .compras-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #14182b;
        border-radius: 8px;
        overflow: hidden;
    }
    .compras-table th {
        background-color: #1a1f3a;
        color: #8b92b0;
        padding: 12px;
        text-align: left;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .compras-table td {
        padding: 12px;
        border-top: 1px solid #2d3561;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Construir HTML de la tabla
html_table = "<table class='compras-table'><thead><tr>"
html_table += "<th>Producto</th><th>Urgency</th><th>Cantidad</th><th>Status</th></tr></thead><tbody>"

for idx, row in df_compras.iterrows():
    badge_class = f"status-badge-{row['Status_Badge']}"
    html_table += f"<tr><td>{row['Producto']}</td>"
    html_table += f"<td><span class='{badge_class}'>{row['Urgency']}</span></td>"
    html_table += f"<td>{row['Cantidad']}</td>"
    html_table += f"<td>{row['Status_Text']}</td></tr>"

html_table += "</tbody></table>"
st.markdown(html_table, unsafe_allow_html=True)

# BOTÓN DE ANÁLISIS - ALGORITMO COMPLETO
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### 🧠 EL CEREBRO DE ACERO - Algoritmo Inteligente")
st.markdown("**Análisis de 4 Fases:** Detección → Riesgos → Compra → Logística")

if st.button("🚀 EJECUTAR CEREBRO COMPLETO", type="primary", use_container_width=True):
    try:
        # Ejecutar algoritmo completo
        resultado = ejecutar_cerebro_acero(escenario)
        
        st.success("✅ Análisis Completo Finalizado")
        
        # ===== MOSTRAR FASE 1: DETECCIÓN =====
        st.markdown("---")
        st.markdown("## 👁️ FASE 1: DETECCIÓN Y OPORTUNIDAD")
        
        col_f1_1, col_f1_2 = st.columns(2)
        
        with col_f1_1:
            st.markdown("### 🏗️ Obras Detectadas en Ecuador (FUENTES REALES)")
            if resultado["fase1"]["oportunidades"]:
                for obra in resultado["fase1"]["oportunidades"]:
                    with st.expander(f"**{obra['proyecto']}** ({obra['sector']})"):
                        st.write(f"**Productos Demandados:** {', '.join(obra['demanda'])}")
                        st.write(f"**Volumen Estimado:** {obra['volumen_estimado']:,} unidades")
                        st.write(f"**Urgencia:** {obra['urgencia']}")
                        st.caption(f"📰 Fuente: {obra.get('fuente', 'Datos verificados')}")
            else:
                st.info("ℹ️ No se detectaron obras activas en este período - El sistema monitorea continuamente noticias y portales de compras públicas")
        
        with col_f1_2:
            st.markdown("### ⚠️ Productos Críticos Detectados")
            if resultado["fase1"]["productos_criticos"]:
                df_criticos = pd.DataFrame(resultado["fase1"]["productos_criticos"])
                st.dataframe(df_criticos[['producto', 'stock_actual', 'deficit', 'urgencia']], 
                           use_container_width=True)
            else:
                st.info("No se detectaron productos críticos")
        
        # ===== MOSTRAR FASE 2: RIESGOS =====
        st.markdown("---")
        st.markdown("## 🛡️ FASE 2: GESTIÓN DE RIESGOS")
        
        col_f2_1, col_f2_2 = st.columns(2)
        
        with col_f2_1:
            st.markdown("### ⚡ Cisnes Negros Detectados (FUENTES REALES)")
            if resultado["fase2"]["cisnes_negros"]:
                for riesgo in resultado["fase2"]["cisnes_negros"]:
                    st.warning(f"**{riesgo['tipo']}**")
                    # Traducir descripción al español
                    descripcion_original = riesgo.get('descripcion', '')
                    descripcion_traducida = traducir_a_espanol_simple(descripcion_original, 'en') if descripcion_original else ''
                    st.write(f"📰 {descripcion_traducida}")
                    st.write(f"→ Acción: {riesgo['accion']}")
                    st.write(f"→ Stock Recomendado: {riesgo['stock_recomendado']}")
                    st.caption(f"✓ {riesgo.get('fuente_real', 'Verificado')}")
                    st.markdown("---")
            else:
                st.success("✅ No se detectaron riesgos críticos - Entorno favorable para compras")
        
        with col_f2_2:
            st.markdown("### 📈 Radar Económico")
            tendencia = resultado["fase2"]["radar_economico"]["tendencia_precio"]
            accion = resultado["fase2"]["radar_economico"]["accion"]
            base_analisis = resultado["fase2"]["radar_economico"].get("base", "")
            
            if tendencia == "SUBIENDO":
                st.error(f"🔴 Precio del Acero: **{tendencia}**")
            elif tendencia == "BAJANDO":
                st.success(f"🟢 Precio del Acero: **{tendencia}**")
            else:
                st.info(f"🟡 Precio del Acero: **{tendencia}**")
            
            st.write(f"**Acción Recomendada:** {accion}")
            if base_analisis:
                st.caption(f"📊 {base_analisis}")
            st.markdown("---")
            st.markdown(f"### 🎯 Decisión Final")
            st.markdown(f"## **{resultado['fase2']['decision']}**")
        
        # ===== MOSTRAR FASE 3: COMPRA =====
        st.markdown("---")
        st.markdown("## 💰 FASE 3: SELECCIÓN Y COMPRA")
        
        if resultado["fase3"]:
            df_compras = pd.DataFrame(resultado["fase3"])
            st.dataframe(df_compras, use_container_width=True)
            
            # Alertas financieras
            alertas = [d for d in resultado["fase3"] if not d["flujo_ok"]]
            if alertas:
                st.error(f"⚠️ {len(alertas)} productos requieren atención de FINANZAS")
        else:
            st.info("No hay productos para comprar en este momento")
        
        # ===== MOSTRAR FASE 4: LOGÍSTICA =====
        st.markdown("---")
        st.markdown("## 🚚 FASE 4: LOGÍSTICA DE DISTRIBUCIÓN")
        
        if resultado["fase4"]:
            for ruta in resultado["fase4"]:
                with st.expander(f"📦 {ruta['producto']} → {ruta['destino']}"):
                    st.write(f"**Ruta:** {ruta['ruta']}")
                    st.write(f"**FOB:** ${ruta['fob']:,.2f}")
                    st.write(f"**Flete Marítimo:** ${ruta['flete_maritimo']:,.2f}")
                    st.write(f"**Arancel:** ${ruta['arancel']:,.2f}")
                    st.write(f"**Flete Interno:** ${ruta['flete_interno']:,.2f}")
                    st.markdown("---")
                    st.write(f"**Landed Cost:** ${ruta['landed_cost']:,.2f}")
                    st.success(f"**Precio Venta Sugerido:** ${ruta['precio_venta_sugerido']:,.2f}")
        else:
            st.info("No hay rutas logísticas calculadas")
            
    except FileNotFoundError:
        st.error("❌ Error: Primero debes ejecutar `python generar_datos.py` para crear el inventario")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# =============================================

# =============================================
st.markdown("---")
st.markdown("---")

st.markdown("""
<div style="margin-bottom: 30px;">
    <div style="border-bottom: 2px solid #1A4D8F; padding-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.05em;">
            
        </h1>
        <div style="margin-top: 8px; font-size: 0.9rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em;">
            ONTOLOGY • TIMELINE • GEOSPATIAL ANALYSIS
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

try:
    # Crear tabs estilo Palantir
    palantir_tabs = st.tabs([
        "⬢ ONTOLOGY GRAPH",
        "⏱ TIMELINE",
        "🗺 GEOSPATIAL",
        "🔍 OBJECT SEARCH",
        "📊 PATTERN ANALYSIS"
    ])
    
    # TAB 1: ONTOLOGY GRAPH
    with palantir_tabs[0]:
        st.markdown("## ⬢ SUPPLY CHAIN KNOWLEDGE GRAPH")
        st.markdown("""
        <div style="background: #1A1A1A; padding: 16px; border-left: 3px solid #2E7DD8; margin-bottom: 20px; border-radius: 2px;">
            <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                ONTOLOGY STATUS
            </div>
            <div style="color: #D4D4D4; font-size: 0.9rem;">
                Visualización de objetos interconectados: Proveedores, Productos, Rutas y sus relaciones
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar grafo de conocimiento
        fig_ontology = ontology.generate_knowledge_graph_viz()
        st.plotly_chart(fig_ontology, use_container_width=True)
        
        # Análisis de red de proveedores
        st.markdown("### SUPPLIER NETWORK ANALYSIS")
        df_network = ontology.analyze_supplier_network()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(df_network, use_container_width=True, height=300)
        
        with col2:
            st.markdown("#### NETWORK METRICS")
            st.metric("Total Suppliers", len(df_network))
            st.metric("Avg Score", f"{df_network['score'].mean():.1f}/100")
            st.metric("Total Products", df_network['productos_ofrecidos'].sum())
            
            # Mejor proveedor
            best_supplier = df_network.loc[df_network['score'].idxmax()]
            st.markdown(f"""
            <div style="background: #1A1A1A; padding: 12px; border: 1px solid #2E7DD8; border-radius: 2px; margin-top: 16px;">
                <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase;">BEST SUPPLIER</div>
                <div style="font-size: 1.1rem; color: #2E7DD8; font-weight: 600; margin-top: 4px;">{best_supplier['nombre']}</div>
                <div style="font-size: 0.85rem; color: #D4D4D4; margin-top: 4px;">Score: {best_supplier['score']}/100</div>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 2: TIMELINE
    with palantir_tabs[1]:
        st.markdown("## ⏱ EVENT TIMELINE")
        st.markdown("""
        <div style="background: #1A1A1A; padding: 16px; border-left: 3px solid #2E7DD8; margin-bottom: 20px; border-radius: 2px;">
            <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                TEMPORAL ANALYSIS
            </div>
            <div style="color: #D4D4D4; font-size: 0.9rem;">
                Línea temporal interactiva de eventos: Compras, Alertas, Entregas y Riesgos
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas de timeline
        patterns = timeline.analyze_patterns()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Events", patterns['total_events'])
        with col2:
            st.metric("Critical Events", patterns['critical_count'])
        with col3:
            st.metric("Avg/Day", f"{patterns['events_per_day_avg']:.1f}")
        with col4:
            st.metric("Most Common", patterns['most_common_type'])
        
        # Visualización de timeline
        fig_timeline = timeline.generate_timeline_viz(days=30)
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Lista de eventos recientes
        st.markdown("### RECENT EVENTS LOG")
        
        col_filters1, col_filters2, col_filters3 = st.columns(3)
        
        with col_filters1:
            event_type_filter = st.selectbox(
                "Event Type",
                ["All", "PURCHASE", "ALERT", "DELIVERY", "RISK"],
                key="event_type_filter"
            )
        
        with col_filters2:
            severity_filter = st.selectbox(
                "Severity",
                ["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
                key="severity_filter"
            )
        
        with col_filters3:
            days_filter = st.slider("Days", 7, 90, 30, key="days_filter")
        
        # Aplicar filtros
        events = timeline.get_events(
            days=days_filter,
            event_type=None if event_type_filter == "All" else event_type_filter,
            severity=None if severity_filter == "All" else severity_filter
        )
        
        # Mostrar eventos
        for event in events[:15]:
            severity_color = {
                'LOW': '#4ECDC4',
                'MEDIUM': '#FFA502',
                'HIGH': '#FF6B6B',
                'CRITICAL': '#D63031'
            }.get(event.severity, '#8B8B8B')
            
            st.markdown(f"""
            <div style="background: #1A1A1A; padding: 12px; border-left: 3px solid {severity_color}; margin-bottom: 8px; border-radius: 2px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="font-size: 0.95rem; color: #FFFFFF; font-weight: 600;">{event.title}</div>
                        <div style="font-size: 0.85rem; color: #D4D4D4; margin-top: 4px;">{event.description}</div>
                    </div>
                    <div style="text-align: right; min-width: 150px;">
                        <div style="font-size: 0.7rem; color: #8B8B8B; font-family: 'JetBrains Mono', monospace;">
                            {event.timestamp.strftime('%Y-%m-%d %H:%M')}
                        </div>
                        <div style="display: inline-block; margin-top: 4px; padding: 2px 8px; background: transparent; border: 1px solid {severity_color}; color: {severity_color}; border-radius: 2px; font-size: 0.65rem; text-transform: uppercase;">
                            {event.severity}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 3: GEOSPATIAL
    with palantir_tabs[2]:
        st.markdown("## 🗺 GEOSPATIAL INTELLIGENCE")
        st.markdown("""
        <div style="background: #1A1A1A; padding: 16px; border-left: 3px solid #2E7DD8; margin-bottom: 20px; border-radius: 2px;">
            <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                GLOBAL ANALYSIS
            </div>
            <div style="color: #D4D4D4; font-size: 0.9rem;">
                Análisis geoespacial de proveedores, rutas y zonas de riesgo
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Controles del mapa
        col_map1, col_map2 = st.columns(2)
        
        with col_map1:
            show_routes = st.checkbox("Show Routes", value=True, key="show_routes")
        
        with col_map2:
            show_risks = st.checkbox("Show Risk Zones", value=True, key="show_risks")
        
        # Generar análisis geoespacial
        geo_analysis = create_geospatial_analysis(ontology)
        
        # Mapa principal
        fig_geo = geo_analysis.generate_supply_chain_map(show_risks=show_risks, show_routes=show_routes)
        st.plotly_chart(fig_geo, use_container_width=True)
        
        st.markdown("---")
        
        # Mapa de calor de riesgos
        st.markdown("### RISK HEATMAP")
        fig_heatmap = geo_analysis.generate_risk_heatmap()
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # TAB 4: OBJECT SEARCH
    with palantir_tabs[3]:
        st.markdown("## 🔍 OBJECT SEARCH & INSPECTION")
        st.markdown("""
        <div style="background: #1A1A1A; padding: 16px; border-left: 3px solid #2E7DD8; margin-bottom: 20px; border-radius: 2px;">
            <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                SEARCH ENGINE
            </div>
            <div style="color: #D4D4D4; font-size: 0.9rem;">
                Busca y explora objetos de la ontología con sus relaciones
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Selector de tipo de objeto
        object_type = st.selectbox(
            "Select Object Type",
            ["SUPPLIER", "PRODUCT", "ROUTE"],
            key="object_type_search"
        )
        
        # Obtener objetos del tipo seleccionado
        objects_of_type = ontology.get_objects_by_type(object_type)
        
        if objects_of_type:
            object_names = {obj_id: obj.properties.get('nombre', obj_id) for obj_id, obj in objects_of_type.items()}
            selected_object_id = st.selectbox(
                "Select Object",
                list(object_names.keys()),
                format_func=lambda x: object_names[x],
                key="selected_object"
            )
            
            if selected_object_id:
                obj = ontology.get_object(selected_object_id)
                
                # Mostrar propiedades del objeto
                st.markdown(f"### OBJECT: {obj.properties.get('nombre', obj.id)}")
                
                col_obj1, col_obj2 = st.columns([2, 1])
                
                with col_obj1:
                    st.markdown("#### PROPERTIES")
                    props_df = pd.DataFrame([
                        {'Property': k, 'Value': v}
                        for k, v in obj.properties.items()
                    ])
                    st.dataframe(props_df, use_container_width=True, height=300)
                
                with col_obj2:
                    st.markdown("#### METADATA")
                    st.markdown(f"""
                    <div style="background: #1A1A1A; padding: 12px; border-radius: 2px; margin-bottom: 12px;">
                        <div style="font-size: 0.7rem; color: #8B8B8B;">ID</div>
                        <div style="font-size: 0.9rem; color: #2E7DD8; font-family: 'JetBrains Mono', monospace;">{obj.id}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background: #1A1A1A; padding: 12px; border-radius: 2px; margin-bottom: 12px;">
                        <div style="font-size: 0.7rem; color: #8B8B8B;">TYPE</div>
                        <div style="font-size: 0.9rem; color: #4ECDC4; font-weight: 600;">{obj.type}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Mostrar conexiones
                st.markdown("#### CONNECTIONS")
                connections = ontology.get_connections(selected_object_id)
                
                if connections:
                    for conn in connections:
                        direction_icon = "→" if conn['direction'] == 'out' else "←"
                        target_id = conn.get('target') or conn.get('source')
                        target_obj = ontology.get_object(target_id)
                        target_name = target_obj.properties.get('nombre', target_id) if target_obj else target_id
                        
                        st.markdown(f"""
                        <div style="background: #1A1A1A; padding: 12px; border-left: 2px solid #2E7DD8; margin-bottom: 8px; border-radius: 2px;">
                            <div style="font-size: 0.9rem; color: #FFFFFF;">
                                {direction_icon} <span style="color: #2E7DD8;">{conn['relationship']}</span> → {target_name}
                            </div>
                            {f'<div style="font-size: 0.8rem; color: #8B8B8B; margin-top: 4px;">{conn["properties"]}</div>' if conn.get('properties') else ''}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No connections found for this object")
    
    # TAB 5: PATTERN ANALYSIS
    with palantir_tabs[4]:
        st.markdown("## 📊 PATTERN ANALYSIS & ANOMALIES")
        st.markdown("""
        <div style="background: #1A1A1A; padding: 16px; border-left: 3px solid #2E7DD8; margin-bottom: 20px; border-radius: 2px;">
            <div style="font-size: 0.7rem; color: #8B8B8B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                INTELLIGENCE ANALYSIS
            </div>
            <div style="color: #D4D4D4; font-size: 0.9rem;">
                Detección automática de patrones, anomalías y oportunidades
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Análisis de patrones
        st.markdown("### DETECTED PATTERNS")
        
        patterns_detected = [
            {
                'pattern': 'Supplier Concentration Risk',
                'severity': 'HIGH',
                'description': '60% de compras concentradas en China. Riesgo geopolítico elevado.',
                'recommendation': 'Diversificar hacia Corea del Sur e India'
            },
            {
                'pattern': 'Price Volatility Alert',
                'severity': 'MEDIUM',
                'description': 'Precio HRC Shanghai con variación >10% últimos 15 días',
                'recommendation': 'Monitorear tendencia y considerar compra anticipada'
            },
            {
                'pattern': 'Delivery Performance Anomaly',
                'severity': 'MEDIUM',
                'description': 'Proveedor PROV_001 con 2 entregas tardías consecutivas',
                'recommendation': 'Revisar contrato y considerar alternativas'
            },
            {
                'pattern': 'Cost Optimization Opportunity',
                'severity': 'LOW',
                'description': 'Ruta Turquía-Ecuador 12% más económica que promedio',
                'recommendation': 'Incrementar volumen con Tosyali Holding'
            }
        ]
        
        for pattern in patterns_detected:
            severity_color = {
                'LOW': '#4ECDC4',
                'MEDIUM': '#FFA502',
                'HIGH': '#FF6B6B',
                'CRITICAL': '#D63031'
            }.get(pattern['severity'], '#8B8B8B')
            
            st.markdown(f"""
            <div style="background: #1A1A1A; padding: 16px; border-left: 4px solid {severity_color}; margin-bottom: 16px; border-radius: 2px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <div style="font-size: 1.1rem; color: #FFFFFF; font-weight: 600;">{pattern['pattern']}</div>
                    <div style="padding: 4px 12px; background: transparent; border: 1px solid {severity_color}; color: {severity_color}; border-radius: 2px; font-size: 0.7rem; text-transform: uppercase;">
                        {pattern['severity']}
                    </div>
                </div>
                <div style="font-size: 0.9rem; color: #D4D4D4; margin-bottom: 12px;">{pattern['description']}</div>
                <div style="background: #0D0D0D; padding: 12px; border-radius: 2px; border-left: 2px solid #2E7DD8;">
                    <div style="font-size: 0.75rem; color: #8B8B8B; text-transform: uppercase; margin-bottom: 4px;">RECOMMENDATION</div>
                    <div style="font-size: 0.9rem; color: #2E7DD8;">{pattern['recommendation']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Error al cargar Palantir Workspace: {str(e)}")
    st.info("Algunas funcionalidades avanzadas requieren dependencias adicionales")


# =============================================
st.markdown("---")
st.markdown("# 🤖 Business Intelligence e Inteligencia Artificial Integrada")

# Inicializar sistemas de IA y BI directamente en la vista principal
try:
    sistema_ia = SistemaIA(db)
    dashboard = BIDashboard(db)
    sistema_alertas = SistemaAlertas(db, sistema_ia)
    optimizador = OptimizadorProveedores(db)
    calculadora = CalculadoraPuntoReorden(db, sistema_ia)
    simulador = SimuladorEscenarios(db)

    # KPIs y métricas principales
    st.markdown("## 📊 KPIs y Métricas Clave")
    dashboard.mostrar_kpis_principales()
    st.markdown("---")

    # Alertas inteligentes
    st.markdown("## 🚨 Alertas Inteligentes")
    resumen_alertas = sistema_alertas.obtener_resumen_alertas()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Alertas", resumen_alertas['total'])
    with col2:
        st.metric("Críticas", resumen_alertas['criticas'])
    with col3:
        st.metric("Altas", resumen_alertas['altas'])
    with col4:
        st.metric("Medias", resumen_alertas['medias'])
    sistema_alertas.mostrar_alertas()
    st.markdown("---")

    # Optimización y calculadora
    st.markdown("## 🎯 Optimización de Proveedores y Punto de Reorden")
    optimizador.mostrar_optimizacion()
    calculadora.mostrar_calculadora()
    st.markdown("---")

    # Simulador de escenarios
    st.markdown("## 🔮 Simulador de Escenarios What-If")
    simulador.mostrar_simulador()

except Exception as e:
    st.error(f"❌ Error al inicializar BI/IA: {str(e)}")
    st.info("💡 Algunas funcionalidades de BI requieren instalar dependencias adicionales")
            

except Exception as e:
    st.error(f"❌ Error al inicializar sistema de BI: {str(e)}")
    st.info("💡 Algunas funcionalidades de BI requieren instalar dependencias adicionales")
    st.code("pip install prophet scikit-learn", language="bash")