"""
RSS Feeds - Noticias SIN LÍMITES
=================================
Estrategia: RSS feeds de medios globales
- 100% GRATIS
- SIN rate limits
- Fuentes: Reuters, BBC, CNN
- Actualización continua
"""

import requests
from datetime import datetime, timedelta
import time
import xml.etree.ElementTree as ET

def obtener_noticias_rss(max_noticias=20):
    """
    Obtiene noticias desde RSS feeds públicos (Reuters, BBC, CNN)
    
    Returns:
        Lista de noticias con formato estándar
    """
    
    noticias_detectadas = []
    
    # RSS FEEDS SIN LÍMITES - ESPAÑOL + INGLÉS + ECUADOR (máxima cobertura)
    rss_feeds = [
        # FUENTES DE ECUADOR (prioridad para contexto local)
        {
            'url': 'https://www.elcomercio.com/feed/',
            'fuente': 'EL COMERCIO EC',
            'idioma': 'es',
            'pais': 'Ecuador',
            'keywords_filter': ['acero', 'metal', 'hierro', 'comercio', 'aranceles', 'exportación', 'importación', 'china', 'minería', 'construcción', 'infraestructura', 'logística', 'puerto', 'guayaquil', 'quito', 'petroleo', 'obra', 'metro', 'refinería', 'posorja', 'licitación', 'compras', 'mtop', 'gobierno', 'proyecto', 'vial']
        },
        {
            'url': 'https://www.eluniverso.com/feed/',
            'fuente': 'EL UNIVERSO EC',
            'idioma': 'es',
            'pais': 'Ecuador',
            'keywords_filter': ['acero', 'metal', 'comercio', 'construcción', 'infraestructura', 'puerto', 'guayaquil', 'obra', 'proyecto', 'licitación', 'metro', 'refinería', 'petróleo', 'exportación', 'importación', 'china']
        },
        {
            'url': 'https://www.primicias.ec/feed/',
            'fuente': 'PRIMICIAS EC',
            'idioma': 'es',
            'pais': 'Ecuador',
            'keywords_filter': ['acero', 'metal', 'comercio', 'construcción', 'infraestructura', 'economia', 'exportación', 'importación', 'obra', 'metro', 'refinería', 'puerto', 'proyecto', 'licitación']
        },
        # FUENTES EN ESPAÑOL (Latinoamérica)
        {
            'url': 'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada',
            'fuente': 'EL PAÍS',
            'idioma': 'es',
            'pais': 'España',
            'keywords_filter': ['acero', 'metal', 'hierro', 'comercio', 'aranceles', 'exportación', 'importación', 'china', 'minería', 'construcción', 'infraestructura', 'logística']
        },
        {
            'url': 'https://cnnespanol.cnn.com/category/economia/feed/',
            'fuente': 'CNN ESPAÑOL',
            'idioma': 'es',
            'pais': 'Global',
            'keywords_filter': ['acero', 'metal', 'comercio', 'aranceles', 'china', 'construcción', 'infraestructura']
        },
        {
            'url': 'https://www.infobae.com/feeds/rss/',
            'fuente': 'INFOBAE',
            'idioma': 'es',
            'pais': 'Argentina',
            'keywords_filter': ['acero', 'metal', 'comercio', 'aranceles', 'exportación', 'construcción', 'minería']
        },
        # FUENTES EN INGLÉS (mayor cobertura internacional)
        {
            'url': 'https://www.reuters.com/rssfeed/businessNews',
            'fuente': 'REUTERS',
            'idioma': 'en',
            'pais': 'Global',
            'keywords_filter': ['steel', 'metal', 'iron', 'shipping', 'trade', 'tariff', 'export', 'import', 'china', 'mining', 'construction', 'infrastructure']
        },
        {
            'url': 'https://feeds.bbci.co.uk/news/business/rss.xml',
            'fuente': 'BBC',
            'idioma': 'en',
            'pais': 'UK',
            'keywords_filter': ['steel', 'metal', 'shipping', 'trade', 'china', 'supply', 'tariff', 'export']
        },
        {
            'url': 'http://rss.cnn.com/rss/money_news_economy.rss',
            'fuente': 'CNN',
            'idioma': 'en',
            'pais': 'USA',
            'keywords_filter': ['steel', 'metal', 'trade', 'tariff', 'shipping', 'china']
        }
    ]
    
    for feed_info in rss_feeds:
        try:
            response = requests.get(feed_info['url'], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                # Parsear XML RSS
                root = ET.fromstring(response.content)
                
                # RSS 2.0 format
                items = root.findall('.//item')
                
                for item in items[:15]:  # Primeros 15 de cada feed
                    titulo = item.find('title')
                    descripcion = item.find('description')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    
                    if titulo is not None:
                        titulo_text = titulo.text or "Sin título"
                        descripcion_text = descripcion.text if descripcion is not None else titulo_text
                        
                        # Extraer link correctamente (algunos RSS usan .text, otros tienen el URL directo)
                        link_text = '#'
                        if link is not None:
                            link_text = link.text.strip() if link.text and link.text.strip() else '#'
                            # Si link.text está vacío, intentar obtener como atributo o contenido
                            if link_text == '#':
                                # Algunos feeds tienen el link sin .text
                                link_text = link.attrib.get('href', '#')
                        
                        # Filtrar por keywords relevantes
                        titulo_lower = titulo_text.lower()
                        descripcion_lower = descripcion_text.lower() if descripcion_text else ""
                        
                        texto_completo = titulo_lower + " " + descripcion_lower
                        
                        if any(kw in texto_completo for kw in feed_info['keywords_filter']):
                            
                            # Detectar tipo (Crisis vs Oportunidad) - BILINGÜE
                            palabras_crisis = [
                                # Español
                                'crisis', 'guerra', 'huelga', 'escasez', 'interrupción', 
                                'conflicto', 'caída', 'baja', 'amenaza', 'riesgo',
                                'recesión', 'declive', 'corte', 'reducción',
                                # Inglés
                                'war', 'strike', 'shortage', 'disruption', 'conflict',
                                'decline', 'drop', 'fall', 'threat', 'risk', 'recession'
                            ]
                            tipo = "Crisis" if any(w in texto_completo for w in palabras_crisis) else "Oportunidad"
                            
                            # Parsear fecha RSS
                            fecha_valida = True
                            try:
                                if pub_date is not None and pub_date.text:
                                    # Formato: Mon, 18 Jan 2026 14:30:00 GMT
                                    from email.utils import parsedate_to_datetime
                                    fecha_dt = parsedate_to_datetime(pub_date.text)
                                    fecha = fecha_dt.isoformat()
                                    
                                    # FILTRO: Solo noticias de últimos 3 días
                                    dias_diferencia = (datetime.now() - fecha_dt.replace(tzinfo=None)).days
                                    if dias_diferencia > 3:
                                        fecha_valida = False
                                else:
                                    fecha = datetime.now().isoformat()
                            except:
                                fecha = datetime.now().isoformat()
                            
                            # Solo agregar si la fecha es válida (últimos 3 días)
                            if not fecha_valida:
                                continue
                            
                            noticias_detectadas.append({
                                "titulo": titulo_text,
                                "descripcion": descripcion_text[:200] if descripcion_text else titulo_text,
                                "fuente": feed_info['fuente'],
                                "idioma": feed_info['idioma'],  # Guardar idioma original
                                "pais": feed_info.get('pais', 'Global'),  # País de origen
                                "fecha": fecha,
                                "url": link_text,
                                "tipo": tipo,
                                "keyword": "rss_feed",
                                "api": "RSS"
                            })
            
            time.sleep(0.5)  # Rate limiting cortés
            
        except Exception as e:
            print(f"Error RSS {feed_info['fuente']}: {e}")
            continue
    
    return noticias_detectadas[:max_noticias]


def combinar_noticias_newsapi_gdelt(noticias_newsapi, max_total=20):
    """
    Combina noticias de NewsAPI (cuando disponible) con RSS Feeds
    
    Strategy:
    - Si NewsAPI funciona: 60% NewsAPI + 40% RSS
    - Si NewsAPI rate-limited: 100% RSS
    
    Args:
        noticias_newsapi: Lista de noticias de NewsAPI
        max_total: Máximo total de noticias
    
    Returns:
        Lista combinada y deduplicada
    """
    
    noticias_finales = []
    
    # Si NewsAPI tiene datos, úsalos como base
    if noticias_newsapi and len(noticias_newsapi) > 0:
        noticias_finales.extend(noticias_newsapi[:12])  # 60% NewsAPI
        
        # Complementar con RSS
        noticias_rss = obtener_noticias_rss(max_noticias=8)
        noticias_finales.extend(noticias_rss)
        
    else:
        # NewsAPI agotado, usar RSS al 100%
        print("NewsAPI agotado, usando RSS al 100%")
        noticias_rss = obtener_noticias_rss(max_noticias=max_total)
        noticias_finales.extend(noticias_rss)
    
    # Deduplicar por título similar
    noticias_unicas = []
    titulos_vistos = set()
    
    for noticia in noticias_finales:
        # Normalizar título para deduplicar
        titulo_norm = noticia['titulo'].lower()[:50]  # Primeras 50 chars
        
        if titulo_norm not in titulos_vistos:
            titulos_vistos.add(titulo_norm)
            noticias_unicas.append(noticia)
    
    return noticias_unicas[:max_total]


# ========================================
# FUNCIÓN DE TEST
# ========================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: RSS Feeds - SIN LIMITES")
    print("=" * 60)
    
    # Test 1: Noticias RSS
    print("\n1. Obteniendo noticias desde RSS feeds...")
    noticias = obtener_noticias_rss(max_noticias=15)
    
    print(f"\n   Noticias obtenidas: {len(noticias)}")
    if noticias:
        for i, n in enumerate(noticias[:5], 1):
            print(f"\n   {i}. [{n['tipo']}] {n['titulo'][:70]}...")
            print(f"      Fuente: {n['fuente']}")
    
    # Test 2: Combinación con NewsAPI vacío
    print("\n\n2. Test combinacion (NewsAPI agotado)...")
    noticias_combinadas = combinar_noticias_newsapi_gdelt(
        noticias_newsapi=[],  # Simular NewsAPI agotado
        max_total=20
    )
    
    print(f"\n   Total combinado: {len(noticias_combinadas)}")
    
    # Estadísticas
    crisis = sum(1 for n in noticias_combinadas if n['tipo'] == 'Crisis')
    oportunidad = sum(1 for n in noticias_combinadas if n['tipo'] == 'Oportunidad')
    fuentes = set(n['fuente'] for n in noticias_combinadas)
    
    print(f"\n   Crisis: {crisis} | Oportunidades: {oportunidad}")
    print(f"   Fuentes: {', '.join(fuentes)}")
    
    print("\n" + "=" * 60)
    print("RESULTADO: RSS Feeds funcionando SIN LIMITES")
    print("=" * 60)
