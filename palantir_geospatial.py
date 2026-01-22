"""
PALANTIR-STYLE GEOSPATIAL ANALYSIS
Análisis geoespacial avanzado con mapas en capas
"""

import plotly.graph_objects as go
import pandas as pd

class GeospatialAnalysis:
    """Sistema de análisis geoespacial estilo Palantir"""
    
    def __init__(self, ontology):
        self.ontology = ontology
    
    def generate_supply_chain_map(self, show_risks=True, show_routes=True):
        """Genera mapa global de la cadena de suministro"""
        
        # Obtener proveedores
        suppliers = self.ontology.get_objects_by_type('SUPPLIER')
        
        # Preparar datos de proveedores
        supplier_data = []
        for supplier_id, supplier in suppliers.items():
            props = supplier.properties
            supplier_data.append({
                'lat': props['lat'],
                'lon': props['lon'],
                'nombre': props['nombre'],
                'ciudad': props['ciudad'],
                'pais': props['pais'],
                'calidad': props['calificacion_calidad'],
                'riesgo': props['riesgo_geopolitico'],
                'capacidad': props['capacidad_mensual'],
                'precio': props['precio_promedio']
            })
        
        df_suppliers = pd.DataFrame(supplier_data)
        
        # Ecuador (destino)
        ecuador = {'lat': -2.1894, 'lon': -79.8891, 'ciudad': 'Guayaquil'}
        
        # Crear figura
        fig = go.Figure()
        
        # === CAPA 1: RUTAS (si está activado) ===
        if show_routes:
            for _, supplier in df_suppliers.iterrows():
                # Línea desde proveedor a Ecuador
                fig.add_trace(go.Scattergeo(
                    lon=[supplier['lon'], ecuador['lon']],
                    lat=[supplier['lat'], ecuador['lat']],
                    mode='lines',
                    line=dict(width=1, color='rgba(46, 125, 216, 0.3)'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # === CAPA 2: PROVEEDORES ===
        # Color según riesgo
        df_suppliers['color'] = df_suppliers['riesgo'].apply(
            lambda x: '#4ECDC4' if x < 0.15 else ('#FFA502' if x < 0.25 else '#FF6B6B')
        )
        
        # Tamaño según capacidad
        df_suppliers['size'] = df_suppliers['capacidad'] / 100
        
        fig.add_trace(go.Scattergeo(
            lon=df_suppliers['lon'],
            lat=df_suppliers['lat'],
            text=df_suppliers['nombre'],
            mode='markers+text',
            name='Proveedores',
            marker=dict(
                size=df_suppliers['size'],
                color=df_suppliers['color'],
                line=dict(width=2, color='#FFFFFF'),
                sizemode='diameter'
            ),
            textposition='top center',
            textfont=dict(size=9, color='#E8E8E8', family='Inter'),
            hovertext=[
                f"<b>{row['nombre']}</b><br>" +
                f"Ciudad: {row['ciudad']}, {row['pais']}<br>" +
                f"Calidad: {row['calidad']}/10<br>" +
                f"Riesgo: {row['riesgo']*100:.0f}%<br>" +
                f"Capacidad: {row['capacidad']} ton/mes<br>" +
                f"Precio: ${row['precio']}/ton"
                for _, row in df_suppliers.iterrows()
            ],
            hoverinfo='text'
        ))
        
        # === CAPA 3: DESTINO (Ecuador) ===
        fig.add_trace(go.Scattergeo(
            lon=[ecuador['lon']],
            lat=[ecuador['lat']],
            text=['ECUADOR<br>Destino'],
            mode='markers+text',
            name='Destino',
            marker=dict(
                size=25,
                color='#2E7DD8',
                symbol='star',
                line=dict(width=3, color='#FFFFFF')
            ),
            textposition='bottom center',
            textfont=dict(size=11, color='#2E7DD8', family='Inter', weight='bold'),
            hovertext=f"<b>Guayaquil, Ecuador</b><br>Puerto Principal<br>Destino Final",
            hoverinfo='text'
        ))
        
        # === CAPA 4: ZONAS DE RIESGO (si está activado) ===
        if show_risks:
            # Zonas de alto riesgo geopolítico
            risk_zones = [
                {'name': 'Estrecho de Hormuz', 'lat': 26.5, 'lon': 56.0, 'radius': 5},
                {'name': 'Mar del Sur de China', 'lat': 12.0, 'lon': 115.0, 'radius': 8},
                {'name': 'Canal de Suez', 'lat': 30.0, 'lon': 32.5, 'radius': 4}
            ]
            
            for zone in risk_zones:
                # Círculo de riesgo
                circle_lat = [zone['lat'] + zone['radius']*i for i in [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5, -1]]
                circle_lon = [zone['lon'] + zone['radius']*i for i in [0, 0.7, 1, 0.7, 0, -0.7, -1, -0.7, 0]]
                
                fig.add_trace(go.Scattergeo(
                    lon=circle_lon,
                    lat=circle_lat,
                    mode='lines',
                    line=dict(width=2, color='rgba(255, 107, 107, 0.4)', dash='dot'),
                    fill='toself',
                    fillcolor='rgba(255, 107, 107, 0.1)',
                    name=f'Zona Riesgo: {zone["name"]}',
                    showlegend=False,
                    hovertext=f"<b>⚠️ ZONA DE RIESGO</b><br>{zone['name']}",
                    hoverinfo='text'
                ))
        
        # Layout
        fig.update_layout(
            title=dict(
                text='GLOBAL SUPPLY CHAIN MAP • GEOSPATIAL ANALYSIS',
                font=dict(size=16, color='#FFFFFF', family='Inter')
            ),
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='#1A1A1A',
                coastlinecolor='#1A4D8F',
                showocean=True,
                oceancolor='#0D0D0D',
                showcountries=True,
                countrycolor='#1A4D8F',
                countrywidth=0.5,
                showlakes=False,
                bgcolor='#0D0D0D',
                center=dict(lat=10, lon=20),
                projection_scale=1.2
            ),
            paper_bgcolor='#0D0D0D',
            plot_bgcolor='#0D0D0D',
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(
                font=dict(color='#E8E8E8', size=10),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='#1A4D8F',
                borderwidth=1
            )
        )
        
        return fig
    
    def generate_risk_heatmap(self):
        """Genera mapa de calor de riesgos globales"""
        
        # Puntos de riesgo globales
        risk_points = [
            {'lat': 39.9, 'lon': 116.4, 'risk_level': 0.3, 'reason': 'Tensión comercial China-USA'},
            {'lat': 26.5, 'lon': 56.0, 'risk_level': 0.7, 'reason': 'Inestabilidad Medio Oriente'},
            {'lat': 30.0, 'lon': 32.5, 'risk_level': 0.5, 'reason': 'Congestión Canal Suez'},
            {'lat': 12.0, 'lon': 115.0, 'risk_level': 0.4, 'reason': 'Disputa territorial'},
            {'lat': 36.5, 'lon': 36.2, 'risk_level': 0.2, 'reason': 'Crisis energética Turquía'},
            {'lat': 19.0, 'lon': 72.8, 'risk_level': 0.15, 'reason': 'Estabilidad India'}
        ]
        
        df_risk = pd.DataFrame(risk_points)
        
        fig = go.Figure()
        
        # Heatmap de densidad
        fig.add_trace(go.Densitymapbox(
            lat=df_risk['lat'],
            lon=df_risk['lon'],
            z=df_risk['risk_level'],
            radius=40,
            colorscale=[
                [0, 'rgba(78, 205, 196, 0.3)'],    # Verde (bajo riesgo)
                [0.5, 'rgba(255, 165, 2, 0.5)'],   # Naranja (medio)
                [1, 'rgba(255, 107, 107, 0.7)']    # Rojo (alto)
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text='Risk Level', font=dict(color='#E8E8E8')),
                tickfont=dict(color='#E8E8E8'),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='#1A4D8F',
                borderwidth=1
            ),
            hovertext=[f"<b>⚠️ {row['reason']}</b><br>Risk: {row['risk_level']*100:.0f}%" 
                      for _, row in df_risk.iterrows()],
            hoverinfo='text'
        ))
        
        fig.update_layout(
            title=dict(
                text='GLOBAL RISK HEATMAP',
                font=dict(size=16, color='#FFFFFF', family='Inter')
            ),
            mapbox=dict(
                style='carto-darkmatter',
                center=dict(lat=20, lon=50),
                zoom=1.5
            ),
            paper_bgcolor='#0D0D0D',
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig

# Función helper para integración
def create_geospatial_analysis(ontology):
    return GeospatialAnalysis(ontology)
