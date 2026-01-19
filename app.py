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

# --- TRADUCCIÓN SIMPLE AL ESPAÑOL ---
def traducir_a_espanol_simple(texto, idioma_origen='en'):
    """Traduce títulos de noticias en inglés a español (palabras clave)"""
    if idioma_origen == 'es':
        return texto  # Ya está en español
    
    # Diccionario de traducción de palabras clave
    traducciones = {
        'steel': 'acero',
        'tariff': 'arancel',
        'tariffs': 'aranceles',
        'trade': 'comercio',
        'war': 'guerra',
        'china': 'China',
        'shipping': 'envío',
        'export': 'exportación',
        'import': 'importación',
        'growth': 'crecimiento',
        'threat': 'amenaza',
        'hits': 'alcanza',
        'boom': 'auge',
        'strikes': 'golpea',
        'says': 'dice',
        'goal': 'meta',
        'after': 'después',
        'defied': 'desafió',
        'currency': 'moneda',
        'weapon': 'arma',
        'never': 'nunca',
        'will': 'usará',
        'going': 'yendo',
        'companies': 'empresas',
        'energy': 'energía',
        'unacceptable': 'inaceptable',
        'leaders': 'líderes',
        'european': 'europeos',
        'over': 'sobre',
        'greenland': 'Groenlandia'
    }
    
    texto_traducido = texto
    for en, es in traducciones.items():
        # Reemplazar palabras completas (case-insensitive)
        import re
        texto_traducido = re.sub(r'\b' + en + r'\b', es, texto_traducido, flags=re.IGNORECASE)
    
    return texto_traducido

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="CEREBRO DE ACERO - Import Aceros S.A. | Sistema de Inteligencia Logística v1.0",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ⚠️ CONFIGURACIÓN SEGURA DE API KEYS ---
# Las claves se cargan desde archivos seguros, NUNCA del código
try:
    # Intenta cargar desde Streamlit Secrets (Cloud)
    NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
except:
    # Si no está en Cloud, busca en secrets.toml local (NO se sube a GitHub)
    NEWSAPI_KEY = ""
    OPENAI_API_KEY = ""
    st.warning("⚠️ Configure las API keys en .streamlit/secrets.toml (local) o en Streamlit Cloud Settings")

# WorldBank API (No requiere key - pública)
WORLDBANK_API_ENABLED = True
# -------------------------------------

client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except:
        pass

# Inicializar NewsAPI
newsapi_client = None
if NEWSAPI_KEY:
    try:
        newsapi_client = NewsApiClient(api_key=NEWSAPI_KEY)
    except:
        pass

# ========================================
# SISTEMA DE NOTICIAS MUNDIALES (APIs REALES)
# ========================================

def obtener_noticias_reales_newsapi():
    """Obtiene noticias reales desde NewsAPI + GDELT (híbrido sin límites)"""
    
    noticias_newsapi = []
    
    if not newsapi_client:
        # Si no hay NewsAPI, usar GDELT directo
        return combinar_noticias_newsapi_gdelt([], max_total=20)
    
    try:
        noticias_detectadas = []
        fecha_desde = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        # 1. NOTICIAS TOP GLOBALES (business + technology)
        try:
            top_news = newsapi_client.get_top_headlines(
                category='business',
                language='en',
                page_size=10
            )
            
            if top_news['status'] == 'ok' and top_news['totalResults'] > 0:
                for article in top_news['articles'][:5]:
                    titulo_lower = article['title'].lower()
                    # Filtrar noticias relevantes para acero/logística/comercio
                    if any(word in titulo_lower for word in ['steel', 'metal', 'iron', 'shipping', 'trade', 'export', 'import', 'tariff', 'china', 'supply chain', 'port', 'construction', 'infrastructure', 'mining']):
                        noticias_detectadas.append({
                            "titulo": article['title'],
                            "descripcion": article['description'] or article['title'],
                            "fuente": article['source']['name'],
                            "fecha": article['publishedAt'],
                            "url": article['url'],
                            "tipo": "Crisis" if any(w in titulo_lower for w in ['crisis', 'war', 'strike', 'shortage', 'disruption']) else "Oportunidad",
                            "keyword": "global business"
                        })
        except Exception as e:
            print(f"Error en top headlines: {e}")
        
        # 2. BÚSQUEDAS ESPECÍFICAS - CRISIS
        keywords_crisis = [
            'steel industry crisis',
            'shipping disruption', 
            'trade war tariff',
            'supply chain shortage'
        ]
        
        for keyword in keywords_crisis[:2]:
            try:
                response = newsapi_client.get_everything(
                    q=keyword,
                    from_param=fecha_desde,
                    language='en',
                    sort_by='publishedAt',
                    page_size=3
                )
                
                if response['status'] == 'ok' and response['totalResults'] > 0:
                    for article in response['articles'][:1]:
                        noticias_detectadas.append({
                            "titulo": article['title'],
                            "descripcion": article['description'] or article['title'],
                            "fuente": article['source']['name'],
                            "fecha": article['publishedAt'],
                            "url": article['url'],
                            "tipo": "Crisis",
                            "keyword": keyword
                        })
            except Exception as e:
                print(f"Error en keyword {keyword}: {e}")
                continue
        
        # 3. BÚSQUEDAS ESPECÍFICAS - OPORTUNIDADES
        keywords_oportunidad = [
            'infrastructure project',
            'mining boom',
            'construction growth'
        ]
        
        for keyword in keywords_oportunidad[:2]:
            try:
                response = newsapi_client.get_everything(
                    q=keyword,
                    from_param=fecha_desde,
                    language='en',
                    sort_by='publishedAt',
                    page_size=3
                )
                
                if response['status'] == 'ok' and response['totalResults'] > 0:
                    for article in response['articles'][:1]:
                        noticias_detectadas.append({
                            "titulo": article['title'],
                            "descripcion": article['description'] or article['title'],
                            "fuente": article['source']['name'],
                            "fecha": article['publishedAt'],
                            "url": article['url'],
                            "tipo": "Oportunidad",
                            "keyword": keyword
                        })
            except Exception as e:
                print(f"Error en keyword {keyword}: {e}")
                continue
        
        # print(f"NewsAPI: {len(noticias_detectadas)} noticias obtenidas")
        noticias_newsapi = noticias_detectadas[:15]
        
    except Exception as e:
        # print(f"Error NewsAPI: {str(e)}")
        noticias_newsapi = []
    
    # COMBINACIÓN HÍBRIDA: NewsAPI + GDELT
    # Si NewsAPI agotado, GDELT toma el 100%
    return combinar_noticias_newsapi_gdelt(noticias_newsapi, max_total=20)

def obtener_datos_economicos_worldbank():
    """Obtiene indicadores económicos desde World Bank API"""
    
    if not WORLDBANK_API_ENABLED:
        return {}
    
    try:
        # Obtener precio de commodities (acero aproximado)
        url = "https://api.worldbank.org/v2/country/all/indicator/PMACP.IRON?format=json&date=2024:2026"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and data[1]:
                ultimo_precio = data[1][0]['value'] if data[1][0]['value'] else 100
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

def obtener_noticias_mundiales():
    """Función principal: obtiene SOLO noticias RELEVANTES desde NewsAPI"""
    
    # Verificar que NewsAPI esté configurada
    if not newsapi_client:
        st.error("⚠️ ERROR: NewsAPI no está configurada. Configure NEWSAPI_KEY en .streamlit/secrets.toml")
        st.stop()
    
    # Obtener noticias reales
    noticias_reales = obtener_noticias_reales_newsapi()
    
    if not noticias_reales:
        # Sin noticias = Sin alertas
        return []
    
    # Procesar y capturar TODAS las noticias relevantes (ALTA, MEDIA, BAJA)
    noticias_relevantes = []
    for noticia in noticias_reales:
        clasificacion = clasificar_noticia_en_escenario(noticia)
        
        # Agregar si tiene alguna clasificación (incluye ALTA, MEDIA, BAJA)
        if clasificacion:
            noticias_relevantes.append({
                "titulo": noticia['titulo'][:100],
                "categoria": clasificacion['categoria'],
                "impacto": clasificacion['impacto'],
                "escenario": clasificacion['escenario'],
                "descripcion": noticia['descripcion'][:150] if noticia['descripcion'] else noticia['titulo'][:150],
                "fuente": noticia.get('fuente', 'NewsAPI'),
                "url": noticia.get('url', '#'),  # ⭐ AGREGAR URL AQUÍ
                "idioma": noticia.get('idioma', 'en'),  # ⭐ Y EL IDIOMA
                "relevancia": clasificacion['relevancia'],
                "es_real": True
            })
    
    return noticias_relevantes

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

# --- CSS PERSONALIZADO TEMA OSCURO ---
st.markdown("""
<style>
    /* Fondo oscuro global */
    .stApp {
        background-color: #0a0e27;
        color: #ffffff;
    }
    
    /* Sidebar oscuro */
    [data-testid="stSidebar"] {
        background-color: #14182b;
    }
    
    /* Tarjetas de métricas mejoradas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #00ff88;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Botones */
    .stButton>button {
        background: linear-gradient(90deg, #ff4757 0%, #ff6348 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
    }
    
    /* Tablas */
    .stTable {
        background-color: #1a1f3a;
    }
    
    /* Tarjetas personalizadas */
    .metric-card {
        background: linear-gradient(135deg, #1e2847 0%, #14182b 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3561;
        margin: 10px 0;
    }
    
    .metric-title {
        color: #8b92b0;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Badge de status */
    .status-badge-critico {
        background-color: #ff4757;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-badge-live {
        background-color: #00ff88;
        color: #0a0e27;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-badge-warning {
        background-color: #ffa502;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
    try:
        # Intentar importar conector SAP
        from sap_connector import get_datos_empresa, usar_datos_reales
        
        if usar_datos_reales():
            # Usar datos REALES de SAP
            datos_sap = get_datos_empresa()
            return datos_sap["inventario"]
        else:
            # Modo simulado
            return pd.read_csv("inventario_simulado.csv")
    except:
        # Fallback: archivo CSV simulado
        return pd.read_csv("inventario_simulado.csv")

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
    
    # 1. Escaneo de Mercado Ecuador - DATOS REALES
    try:
        obras_activas = obtener_obras_detectadas_ecuador(dias=60)
        
        # Filtrar según escenario (opcional)
        if "Crisis" in escenario:
            # En crisis, filtrar solo urgencia ALTA
            obras_activas = [o for o in obras_activas if o['urgencia'] == 'ALTA']
        
        if "Boom" in escenario or "Minero" in escenario:
            # En boom, priorizar minería y petróleo
            obras_prioritarias = [o for o in obras_activas if o['sector'] in ['Minería', 'Petróleo']]
            obras_resto = [o for o in obras_activas if o['sector'] not in ['Minería', 'Petróleo']]
            obras_activas = obras_prioritarias + obras_resto
        
    except Exception as e:
        print(f"⚠️ Error obteniendo obras: {str(e)}")
        # Fallback a datos básicos
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
    """El Escudo: Decide si es seguro comprar ahora"""
    
    riesgos = {
        "cisnes_negros": [],
        "radar_economico": {},
        "decision": "COMPRAR",
        "ajustes": []
    }
    
    # Radar de Cisnes Negros
    if "Crisis" in escenario:
        riesgos["cisnes_negros"].append({
            "tipo": "Geopolítica - Guerra",
            "descripcion": "Conflicto afecta ruta Mar Rojo",
            "accion": "Recargar flete +20%",
            "stock_recomendado": "6 meses"
        })
        riesgos["ajustes"].append("Aumentar stock de seguridad a 6 meses")
        riesgos["ajustes"].append("Buscar rutas alternas (Cabo Buena Esperanza)")
    
    # Simular otros riesgos aleatorios
    eventos_posibles = [
        {"tipo": "Pandemia", "prob": 0.05, "accion": "Stock para 6 meses - Pánico controlado"},
        {"tipo": "Terremoto en Turquía", "prob": 0.1, "accion": "Proveedor alternativo en India"},
        {"tipo": "Huelga Portuaria Guayaquil", "prob": 0.15, "accion": "Nacionalizar en Esmeraldas"},
        {"tipo": "Salvaguardia Arancelaria", "prob": 0.2, "accion": "Importar INMEDIATO antes de decreto"}
    ]
    
    for evento in eventos_posibles:
        if random.random() < evento["prob"]:
            riesgos["cisnes_negros"].append({
                "tipo": evento["tipo"],
                "descripcion": f"Riesgo detectado: {evento['tipo']}",
                "accion": evento["accion"],
                "stock_recomendado": "Normal"
            })
    
    # Radar Económico
    precio_acero_tendencia = random.choice(["SUBIENDO", "BAJANDO", "ESTABLE"])
    
    riesgos["radar_economico"] = {
        "tendencia_precio": precio_acero_tendencia,
        "accion": "COMPRAR YA" if precio_acero_tendencia == "SUBIENDO" else "ESPERAR 1 SEMANA" if precio_acero_tendencia == "BAJANDO" else "COMPRAR NORMAL"
    }
    
    # Decisión final
    if len(riesgos["cisnes_negros"]) > 2:
        riesgos["decision"] = "ESPERAR - Demasiados riesgos"
    elif precio_acero_tendencia == "SUBIENDO" or "Crisis" in escenario:
        riesgos["decision"] = "COMPRAR URGENTE"
    
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
    
    with st.spinner("🧠 FASE 1: Escaneando mercado y detectando oportunidades..."):
        time.sleep(1)
        fase1 = fase1_deteccion_oportunidad(escenario)
    
    with st.spinner("🛡️ FASE 2: Analizando riesgos geopolíticos y económicos..."):
        time.sleep(1)
        fase2 = fase2_gestion_riesgos(escenario)
    
    with st.spinner("💰 FASE 3: Seleccionando proveedores óptimos..."):
        time.sleep(1)
        fase3 = fase3_seleccion_compra(fase1["productos_criticos"])
    
    with st.spinner("🚚 FASE 4: Optimizando logística de distribución..."):
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

# Sidebar con menú de navegación
with st.sidebar:
    st.markdown("### 🧠 CEREBRO DE ACERO")
    st.markdown("**Import Aceros S.A.**")
    ultima_actualizacion = info_escenarios[list(info_escenarios.keys())[0]].get('ultima_actualizacion', datetime.now().strftime('%Y-%m-%d %H:%M'))
    st.markdown(f"🌐 **Última Actualización:** {datetime.now().strftime('%H:%M')}")
    st.caption(f"🔄 Auto-refresh en {refresh_interval//60} min")
    
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
    
    # DASHBOARD PREMIUM GRATUITO (Yahoo Finance, BDRY, etc.)
    st.markdown("---")
    st.markdown("### 💰 **Datos Premium**")
    
    try:
        dashboard_premium = generar_dashboard_completo_gratis()
        
        # Precio Acero Real (Yahoo Finance)
        acero_premium = dashboard_premium['acero']
        st.metric(
            "🔥 Precio Acero HRC (Real)",
            f"${acero_premium['precio']:.2f}/ton",
            delta=f"{acero_premium['cambio_pct']:.1f}%",
            delta_color="inverse"
        )
        st.caption(f"Fuente: {acero_premium['fuente']}")
        
        # Costo de Fletes (BDRY ETF)
        fletes_premium = dashboard_premium['fletes']
        st.metric(
            "🚢 Container 40' (Estimado)",
            f"${fletes_premium['costo_estimado_40ft']:.0f}",
            delta=fletes_premium['tendencia']
        )
        st.caption(f"Recomendación: {fletes_premium['recomendacion']}")
        
        # Tasa CNY detallada
        forex_premium = dashboard_premium['forex']
        if 'Yuan Chino' in forex_premium:
            yuan_data = forex_premium['Yuan Chino']
            st.metric(
                "💵 CNY/USD (Detallado)",
                f"¥{yuan_data['tasa']:.4f}",
                delta=f"{yuan_data['cambio_mes']:.2f}% (mes)"
            )
            st.caption(yuan_data['alerta'])
        
    except Exception as e:
        st.caption(f"⚠️ APIs premium en standby: {str(e)}")
    
    st.markdown("---")
    
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
            # Traducir título si está en inglés
            titulo_noticia = info['titulo_noticia']
            idioma_titulo = info.get('idioma', 'es')
            if idioma_titulo == 'en':
                titulo_noticia = traducir_a_espanol_simple(titulo_noticia, 'en')
            
            st.markdown(f"**📰 Noticia:** {titulo_noticia}")
            st.markdown(f"**Categoría:** {info['categoria']}")
        
        # Traducir descripción si está en inglés
        descripcion = info['descripcion']
        idioma_desc = info.get('idioma', 'es')
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
                idioma = n.get('idioma', 'es')
                titulo_original = n.get('titulo', 'Sin título')
                
                # Traducir al español si está en inglés
                titulo_display = traducir_a_espanol_simple(titulo_original, idioma) if idioma == 'en' else titulo_original
                
                # Usar HTML simple con target="_blank"
                st.markdown(
                    f'<a href="{link_url}" target="_blank" rel="noopener noreferrer" '
                    f'style="color: #1f77b4; text-decoration: underline;">'
                    f'🔗 {titulo_display}</a> '
                    f'<span style="color: #888;">({fuente})</span>',
                    unsafe_allow_html=True
                )
    
    # Botón para forzar actualización inmediata
    if st.button("🔄 Forzar Actualización de Noticias"):
        st.cache_data.clear()
        st.rerun()

# Header principal
st.markdown("# Tablero")
st.markdown("---")

# SECCIÓN NUEVA: Datos Premium en Tiempo Real
try:
    dashboard_premium = generar_dashboard_completo_gratis()
    
    st.markdown("### 💰 Datos de Mercado en Tiempo Real")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        acero_premium = dashboard_premium['acero']
        st.metric(
            "Precio Acero HRC",
            f"${acero_premium['precio']:.2f}/ton",
            delta=f"{acero_premium['cambio_pct']:.1f}%",
            delta_color="inverse"
        )
        st.caption(acero_premium['tendencia'])
    
    with col_b:
        fletes_premium = dashboard_premium['fletes']
        st.metric(
            "Flete Container 40'",
            f"${fletes_premium['costo_estimado_40ft']:.0f}",
            delta=f"{fletes_premium['cambio_pct']:.1f}%"
        )
        st.caption(fletes_premium['recomendacion'])
    
    with col_c:
        forex_premium = dashboard_premium['forex']
        if 'Yuan Chino' in forex_premium:
            yuan_data = forex_premium['Yuan Chino']
            st.metric(
                "CNY/USD",
                f"¥{yuan_data['tasa']:.4f}",
                delta=f"{yuan_data['cambio_mes']:.2f}%"
            )
            st.caption(yuan_data['alerta'])
    
    with col_d:
        # Mostrar commodities relacionados
        commodities = dashboard_premium['commodities']
        if 'Cobre' in commodities:
            cobre_data = commodities['Cobre']
            st.metric(
                "Cobre (Indicador)",
                f"${cobre_data['precio']:.2f}",
                delta=f"{cobre_data['cambio_pct']:.1f}%"
            )
            st.caption("Proxy de mercado")
    
    st.markdown("---")
except:
    pass

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
            st.markdown("### 🏗️ Obras Detectadas en Ecuador")
            for obra in resultado["fase1"]["oportunidades"]:
                with st.expander(f"**{obra['proyecto']}** ({obra['sector']})"):
                    st.write(f"**Productos Demandados:** {', '.join(obra['demanda'])}")
                    st.write(f"**Volumen Estimado:** {obra['volumen_estimado']} unidades")
                    st.write(f"**Urgencia:** {obra['urgencia']}")
        
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
            st.markdown("### ⚡ Cisnes Negros Detectados")
            if resultado["fase2"]["cisnes_negros"]:
                for riesgo in resultado["fase2"]["cisnes_negros"]:
                    st.warning(f"**{riesgo['tipo']}**")
                    st.write(f"→ Acción: {riesgo['accion']}")
                    st.write(f"→ Stock Recomendado: {riesgo['stock_recomendado']}")
                    st.markdown("---")
            else:
                st.success("✅ No se detectaron riesgos críticos")
        
        with col_f2_2:
            st.markdown("### 📈 Radar Económico")
            tendencia = resultado["fase2"]["radar_economico"]["tendencia_precio"]
            accion = resultado["fase2"]["radar_economico"]["accion"]
            
            if tendencia == "SUBIENDO":
                st.error(f"🔴 Precio del Acero: **{tendencia}**")
            elif tendencia == "BAJANDO":
                st.success(f"🟢 Precio del Acero: **{tendencia}**")
            else:
                st.info(f"🟡 Precio del Acero: **{tendencia}**")
            
            st.write(f"**Acción Recomendada:** {accion}")
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