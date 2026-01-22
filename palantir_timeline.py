"""
PALANTIR-STYLE TIMELINE & EVENT SYSTEM
Sistema de línea temporal interactiva con eventos conectados
"""

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

class TimelineEvent:
    """Evento en la línea temporal"""
    def __init__(self, event_id, timestamp, event_type, title, description, severity, related_objects=None):
        self.id = event_id
        self.timestamp = timestamp
        self.type = event_type
        self.title = title
        self.description = description
        self.severity = severity  # LOW, MEDIUM, HIGH, CRITICAL
        self.related_objects = related_objects or []
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'related_objects': self.related_objects
        }

class PalantirTimeline:
    """Sistema de timeline estilo Palantir"""
    
    def __init__(self):
        self.events = []
        self._initialize_demo_events()
    
    def _initialize_demo_events(self):
        """Crea eventos demo de los últimos 30 días"""
        now = datetime.now()
        
        # Eventos de compras
        for i in range(8):
            days_ago = random.randint(1, 30)
            timestamp = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            proveedores = ['Tianjin Steel', 'Posco', 'Tosyali', 'ArcelorMittal']
            productos = ['Varilla 12mm', 'Viga IPE 200', 'Plancha LAC 2mm']
            
            proveedor = random.choice(proveedores)
            producto = random.choice(productos)
            cantidad = random.randint(100, 500)
            precio = random.randint(1100, 1400)
            
            self.add_event(
                event_type='PURCHASE',
                title=f'Compra: {cantidad}T {producto}',
                description=f'Proveedor: {proveedor} | Precio: ${precio:,}/T | Total: ${cantidad*precio:,}',
                severity='MEDIUM',
                timestamp=timestamp,
                related_objects=[f'PROV_{random.randint(1,4):03d}', f'PROD_{random.randint(1,4):03d}']
            )
        
        # Eventos de alertas geopolíticas
        alertas = [
            {
                'title': 'Tensión Comercial China-USA',
                'description': 'Posibles aranceles adicionales del 25% a acero chino',
                'severity': 'HIGH',
                'days_ago': 5
            },
            {
                'title': 'Huelga Puerto de Shanghai',
                'description': 'Trabajadores portuarios en paro por 48 horas. Retrasos esperados.',
                'severity': 'CRITICAL',
                'days_ago': 12
            },
            {
                'title': 'Precio Acero HRC +15%',
                'description': 'Subida en Bolsa de Shanghai por alta demanda en construcción',
                'severity': 'HIGH',
                'days_ago': 8
            },
            {
                'title': 'Crisis Energética Turquía',
                'description': 'Cortes de electricidad afectan producción siderúrgica',
                'severity': 'MEDIUM',
                'days_ago': 18
            }
        ]
        
        for alerta in alertas:
            timestamp = now - timedelta(days=alerta['days_ago'], hours=random.randint(8, 18))
            self.add_event(
                event_type='ALERT',
                title=alerta['title'],
                description=alerta['description'],
                severity=alerta['severity'],
                timestamp=timestamp,
                related_objects=[]
            )
        
        # Eventos de entregas
        for i in range(5):
            days_ago = random.randint(1, 25)
            timestamp = now - timedelta(days=days_ago)
            
            on_time = random.choice([True, True, True, False])
            
            self.add_event(
                event_type='DELIVERY',
                title=f'Entrega Contenedor #{1000+i}',
                description=f'Status: {"A tiempo" if on_time else "Retrasado 5 días"} | Puerto: Guayaquil',
                severity='LOW' if on_time else 'MEDIUM',
                timestamp=timestamp,
                related_objects=[f'ROUTE_{random.randint(1,4):03d}']
            )
    
    def add_event(self, event_type, title, description, severity, timestamp=None, related_objects=None):
        """Agrega un evento al timeline"""
        if timestamp is None:
            timestamp = datetime.now()
        
        event_id = f'EVT_{len(self.events)+1:04d}'
        event = TimelineEvent(event_id, timestamp, event_type, title, description, severity, related_objects)
        self.events.append(event)
    
    def get_events(self, days=30, event_type=None, severity=None):
        """Obtiene eventos filtrados"""
        cutoff = datetime.now() - timedelta(days=days)
        
        filtered = [e for e in self.events if e.timestamp >= cutoff]
        
        if event_type:
            filtered = [e for e in filtered if e.type == event_type]
        
        if severity:
            filtered = [e for e in filtered if e.severity == severity]
        
        return sorted(filtered, key=lambda x: x.timestamp, reverse=True)
    
    def generate_timeline_viz(self, days=30):
        """Genera visualización de timeline estilo Palantir"""
        events = self.get_events(days=days)
        
        if not events:
            return None
        
        # Colores por tipo de evento
        type_colors = {
            'PURCHASE': '#4ECDC4',
            'ALERT': '#FF6B6B',
            'DELIVERY': '#2E7DD8',
            'RISK': '#FFA502'
        }
        
        # Colores por severidad
        severity_colors = {
            'LOW': '#4ECDC4',
            'MEDIUM': '#FFA502',
            'HIGH': '#FF6B6B',
            'CRITICAL': '#D63031'
        }
        
        # Preparar datos
        df = pd.DataFrame([e.to_dict() for e in events])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['color'] = df['severity'].map(severity_colors)
        df['y_pos'] = [i % 3 for i in range(len(df))]  # Alternar posiciones
        
        # Crear figura
        fig = go.Figure()
        
        # Línea de tiempo
        fig.add_trace(go.Scatter(
            x=[df['timestamp'].min(), df['timestamp'].max()],
            y=[1, 1],
            mode='lines',
            line=dict(color='#1A4D8F', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Eventos
        for event_type in df['type'].unique():
            df_type = df[df['type'] == event_type]
            
            fig.add_trace(go.Scatter(
                x=df_type['timestamp'],
                y=df_type['y_pos'],
                mode='markers+text',
                name=event_type,
                marker=dict(
                    size=15,
                    color=df_type['color'],
                    line=dict(width=2, color='#FFFFFF'),
                    symbol='diamond'
                ),
                text=df_type['title'],
                textposition='top center',
                textfont=dict(size=8, color='#E8E8E8'),
                hovertext=[f"<b>{row['title']}</b><br>{row['description']}<br>Severity: {row['severity']}" 
                          for _, row in df_type.iterrows()],
                hoverinfo='text'
            ))
        
        fig.update_layout(
            title=dict(
                text='EVENT TIMELINE • LAST 30 DAYS',
                font=dict(size=16, color='#FFFFFF', family='Inter')
            ),
            xaxis=dict(
                title='',
                showgrid=True,
                gridcolor='#1A4D8F',
                gridwidth=0.5,
                color='#8B8B8B',
                tickfont=dict(size=10, family='JetBrains Mono')
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            paper_bgcolor='#0D0D0D',
            plot_bgcolor='#0D0D0D',
            hovermode='closest',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            legend=dict(
                font=dict(color='#E8E8E8', size=10),
                bgcolor='rgba(0,0,0,0.5)',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        return fig
    
    def get_recent_alerts(self, limit=5):
        """Obtiene alertas recientes"""
        alerts = [e for e in self.events if e.type == 'ALERT']
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return alerts[:limit]
    
    def analyze_patterns(self):
        """Analiza patrones en eventos"""
        df = pd.DataFrame([e.to_dict() for e in self.events])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['day'] = df['timestamp'].dt.date
        
        # Eventos por día
        events_per_day = df.groupby('day').size()
        
        # Eventos por tipo
        events_by_type = df['type'].value_counts()
        
        # Eventos críticos
        critical_events = len(df[df['severity'].isin(['HIGH', 'CRITICAL'])])
        
        return {
            'total_events': len(self.events),
            'critical_count': critical_events,
            'events_per_day_avg': events_per_day.mean(),
            'most_common_type': events_by_type.index[0] if len(events_by_type) > 0 else 'N/A',
            'types_distribution': events_by_type.to_dict()
        }

# Instancia global
timeline = PalantirTimeline()
