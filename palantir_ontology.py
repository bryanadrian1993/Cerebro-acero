"""
PALANTIR-STYLE ONTOLOGY SYSTEM
Sistema de objetos interconectados con grafos de conocimiento
"""

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

class OntologyObject:
    """Clase base para todos los objetos de la ontología"""
    def __init__(self, obj_id, obj_type, properties):
        self.id = obj_id
        self.type = obj_type
        self.properties = properties
        self.links = []  # Relaciones con otros objetos
    
    def add_link(self, target_id, relationship_type):
        self.links.append({
            'target': target_id,
            'type': relationship_type
        })

class SupplyChainOntology:
    """Ontología completa de la cadena de suministro estilo Palantir"""
    
    def __init__(self):
        self.objects = {}
        self.graph = nx.DiGraph()
        self._initialize_ontology()
    
    def _initialize_ontology(self):
        """Inicializa la ontología con objetos base"""
        
        # === PROVEEDORES ===
        proveedores = [
            {
                'id': 'PROV_001',
                'nombre': 'Tianjin Steel Group',
                'pais': 'China',
                'ciudad': 'Tianjin',
                'lat': 39.0842,
                'lon': 117.2010,
                'capacidad_mensual': 5000,
                'calificacion_calidad': 8.5,
                'precio_promedio': 1200,
                'tiempo_entrega_promedio': 45,
                'riesgo_geopolitico': 0.3,
                'certificaciones': ['ISO 9001', 'API 5L'],
                'contacto': 'sales@tianjiinsteel.cn'
            },
            {
                'id': 'PROV_002',
                'nombre': 'Posco Steel',
                'pais': 'Corea del Sur',
                'ciudad': 'Pohang',
                'lat': 36.0190,
                'lon': 129.3435,
                'capacidad_mensual': 4000,
                'calificacion_calidad': 9.5,
                'precio_promedio': 1380,
                'tiempo_entrega_promedio': 35,
                'riesgo_geopolitico': 0.1,
                'certificaciones': ['ISO 9001', 'API 5L', 'JIS G3101'],
                'contacto': 'export@posco.kr'
            },
            {
                'id': 'PROV_003',
                'nombre': 'Tosyali Holding',
                'pais': 'Turquía',
                'ciudad': 'Iskenderun',
                'lat': 36.5875,
                'lon': 36.1778,
                'capacidad_mensual': 3500,
                'calificacion_calidad': 7.8,
                'precio_promedio': 1140,
                'tiempo_entrega_promedio': 50,
                'riesgo_geopolitico': 0.2,
                'certificaciones': ['ISO 9001', 'CE'],
                'contacto': 'info@tosyali.com'
            },
            {
                'id': 'PROV_004',
                'nombre': 'ArcelorMittal India',
                'pais': 'India',
                'ciudad': 'Mumbai',
                'lat': 19.0760,
                'lon': 72.8777,
                'capacidad_mensual': 4500,
                'calificacion_calidad': 8.2,
                'precio_promedio': 1260,
                'tiempo_entrega_promedio': 40,
                'riesgo_geopolitico': 0.15,
                'certificaciones': ['ISO 9001', 'API 5L', 'BIS'],
                'contacto': 'export@arcelormittal.in'
            }
        ]
        
        for prov in proveedores:
            self.add_object(prov['id'], 'SUPPLIER', prov)
        
        # === PRODUCTOS ===
        productos = [
            {
                'id': 'PROD_001',
                'nombre': 'Varilla de Construcción 12mm',
                'categoria': 'Productos Largos',
                'especificacion': 'ASTM A615 Grade 60',
                'precio_referencia': 1200,
                'demanda_mensual_promedio': 800,
                'stock_minimo': 200,
                'unidad': 'toneladas'
            },
            {
                'id': 'PROD_002',
                'nombre': 'Viga IPE 200',
                'categoria': 'Perfiles Estructurales',
                'especificacion': 'EN 10025-2 S275JR',
                'precio_referencia': 1350,
                'demanda_mensual_promedio': 500,
                'stock_minimo': 150,
                'unidad': 'toneladas'
            },
            {
                'id': 'PROD_003',
                'nombre': 'Plancha LAC 2mm',
                'categoria': 'Productos Planos',
                'especificacion': 'ASTM A36',
                'precio_referencia': 1180,
                'demanda_mensual_promedio': 600,
                'stock_minimo': 180,
                'unidad': 'toneladas'
            },
            {
                'id': 'PROD_004',
                'nombre': 'Ángulo Estructural 2x2',
                'categoria': 'Perfiles',
                'especificacion': 'ASTM A36',
                'precio_referencia': 1220,
                'demanda_mensual_promedio': 400,
                'stock_minimo': 120,
                'unidad': 'toneladas'
            }
        ]
        
        for prod in productos:
            self.add_object(prod['id'], 'PRODUCT', prod)
        
        # === RUTAS LOGÍSTICAS ===
        rutas = [
            {
                'id': 'ROUTE_001',
                'origen': 'Tianjin, China',
                'destino': 'Guayaquil, Ecuador',
                'distancia_nautica': 11500,
                'tiempo_transito_dias': 45,
                'puertos_intermedios': ['Singapore', 'Panama Canal'],
                'costo_flete_promedio': 3200,
                'navieras': ['COSCO', 'Maersk', 'MSC']
            },
            {
                'id': 'ROUTE_002',
                'origen': 'Pohang, Corea del Sur',
                'destino': 'Guayaquil, Ecuador',
                'distancia_nautica': 10800,
                'tiempo_transito_dias': 35,
                'puertos_intermedios': ['Los Angeles', 'Panama Canal'],
                'costo_flete_promedio': 3500,
                'navieras': ['Hyundai', 'Maersk']
            },
            {
                'id': 'ROUTE_003',
                'origen': 'Iskenderun, Turquía',
                'destino': 'Guayaquil, Ecuador',
                'distancia_nautica': 7200,
                'tiempo_transito_dias': 50,
                'puertos_intermedios': ['Gibraltar', 'Panama Canal'],
                'costo_flete_promedio': 2800,
                'navieras': ['MSC', 'CMA CGM']
            },
            {
                'id': 'ROUTE_004',
                'origen': 'Mumbai, India',
                'destino': 'Guayaquil, Ecuador',
                'distancia_nautica': 9500,
                'tiempo_transito_dias': 40,
                'puertos_intermedios': ['Suez Canal', 'Panama Canal'],
                'costo_flete_promedio': 3100,
                'navieras': ['Maersk', 'MSC']
            }
        ]
        
        for ruta in rutas:
            self.add_object(ruta['id'], 'ROUTE', ruta)
        
        # === CREAR RELACIONES ===
        # Proveedores -> Productos (SUPPLIES)
        self.add_link('PROV_001', 'PROD_001', 'SUPPLIES', {'precio': 1200, 'lead_time': 45})
        self.add_link('PROV_001', 'PROD_002', 'SUPPLIES', {'precio': 1350, 'lead_time': 45})
        self.add_link('PROV_002', 'PROD_002', 'SUPPLIES', {'precio': 1550, 'lead_time': 35})
        self.add_link('PROV_002', 'PROD_003', 'SUPPLIES', {'precio': 1360, 'lead_time': 35})
        self.add_link('PROV_003', 'PROD_001', 'SUPPLIES', {'precio': 1140, 'lead_time': 50})
        self.add_link('PROV_003', 'PROD_004', 'SUPPLIES', {'precio': 1160, 'lead_time': 50})
        self.add_link('PROV_004', 'PROD_001', 'SUPPLIES', {'precio': 1260, 'lead_time': 40})
        self.add_link('PROV_004', 'PROD_003', 'SUPPLIES', {'precio': 1240, 'lead_time': 40})
        
        # Proveedores -> Rutas (USES_ROUTE)
        self.add_link('PROV_001', 'ROUTE_001', 'USES_ROUTE', {})
        self.add_link('PROV_002', 'ROUTE_002', 'USES_ROUTE', {})
        self.add_link('PROV_003', 'ROUTE_003', 'USES_ROUTE', {})
        self.add_link('PROV_004', 'ROUTE_004', 'USES_ROUTE', {})
    
    def add_object(self, obj_id, obj_type, properties):
        """Agrega un objeto a la ontología"""
        obj = OntologyObject(obj_id, obj_type, properties)
        self.objects[obj_id] = obj
        self.graph.add_node(obj_id, type=obj_type, **properties)
    
    def add_link(self, source_id, target_id, relationship_type, properties=None):
        """Crea una relación entre dos objetos"""
        if source_id in self.objects:
            self.objects[source_id].add_link(target_id, relationship_type)
        
        props = properties or {}
        self.graph.add_edge(source_id, target_id, relationship=relationship_type, **props)
    
    def get_object(self, obj_id):
        """Obtiene un objeto por ID"""
        return self.objects.get(obj_id)
    
    def get_objects_by_type(self, obj_type):
        """Obtiene todos los objetos de un tipo"""
        return {k: v for k, v in self.objects.items() if v.type == obj_type}
    
    def get_connections(self, obj_id):
        """Obtiene todas las conexiones de un objeto"""
        if obj_id not in self.graph:
            return []
        
        connections = []
        # Conexiones salientes
        for target in self.graph.successors(obj_id):
            edge_data = self.graph.edges[obj_id, target]
            connections.append({
                'direction': 'out',
                'target': target,
                'relationship': edge_data.get('relationship'),
                'properties': {k: v for k, v in edge_data.items() if k != 'relationship'}
            })
        
        # Conexiones entrantes
        for source in self.graph.predecessors(obj_id):
            edge_data = self.graph.edges[source, obj_id]
            connections.append({
                'direction': 'in',
                'source': source,
                'relationship': edge_data.get('relationship'),
                'properties': {k: v for k, v in edge_data.items() if k != 'relationship'}
            })
        
        return connections
    
    def find_path(self, source_id, target_id):
        """Encuentra el camino más corto entre dos objetos"""
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except:
            return None
    
    def analyze_supplier_network(self):
        """Analiza la red de proveedores"""
        suppliers = self.get_objects_by_type('SUPPLIER')
        
        analysis = []
        for supplier_id, supplier in suppliers.items():
            connections = self.get_connections(supplier_id)
            products_supplied = [c for c in connections if c['relationship'] == 'SUPPLIES']
            
            analysis.append({
                'id': supplier_id,
                'nombre': supplier.properties['nombre'],
                'productos_ofrecidos': len(products_supplied),
                'precio_promedio': supplier.properties['precio_promedio'],
                'calidad': supplier.properties['calificacion_calidad'],
                'riesgo': supplier.properties['riesgo_geopolitico'],
                'score': self._calculate_supplier_score(supplier)
            })
        
        return pd.DataFrame(analysis)
    
    def _calculate_supplier_score(self, supplier):
        """Calcula score de proveedor (0-100)"""
        calidad_norm = (supplier.properties['calificacion_calidad'] / 10) * 40
        precio_norm = ((2000 - supplier.properties['precio_promedio']) / 2000) * 30
        riesgo_norm = (1 - supplier.properties['riesgo_geopolitico']) * 30
        
        return round(calidad_norm + precio_norm + riesgo_norm, 1)
    
    def generate_knowledge_graph_viz(self):
        """Genera visualización del grafo de conocimiento estilo Palantir"""
        
        # Posiciones de los nodos usando layout spring
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Preparar datos para Plotly
        edge_trace = []
        node_trace = []
        
        # Colores por tipo de objeto
        type_colors = {
            'SUPPLIER': '#2E7DD8',
            'PRODUCT': '#4ECDC4',
            'ROUTE': '#FF6B6B',
            'EVENT': '#FFA502'
        }
        
        # Crear edges
        for edge in self.graph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color='rgba(46, 125, 216, 0.3)'),
                hoverinfo='none',
                showlegend=False
            ))
        
        # Crear nodes agrupados por tipo, pero solo mostrar nodos con al menos una conexión
        for node_type in ['PRODUCT', 'ROUTE']:
            nodes_of_type = [n for n, d in self.graph.nodes(data=True) if d.get('type') == node_type]
            # Filtrar nodos con al menos una conexión (entrante o saliente)
            nodes_with_edges = [n for n in nodes_of_type if self.graph.degree(n) > 0]
            if not nodes_with_edges:
                continue
            node_x = [pos[node][0] for node in nodes_with_edges]
            node_y = [pos[node][1] for node in nodes_with_edges]
            node_text = []
            for node in nodes_with_edges:
                obj = self.objects[node]
                if node_type == 'PRODUCT':
                    text = f"<b>{obj.properties['nombre']}</b><br>Demanda: {obj.properties['demanda_mensual_promedio']} ton/mes"
                else:
                    text = f"<b>{obj.properties['origen']} → {obj.properties['destino']}</b><br>Tiempo: {obj.properties['tiempo_transito_dias']} días"
                node_text.append(text)
            node_trace.append(go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                name=node_type,
                marker=dict(
                    size=20,
                    color=type_colors[node_type],
                    line=dict(width=2, color='#FFFFFF')
                ),
                text=[self.objects[n].properties.get('nombre', n)[:15] for n in nodes_with_edges],
                textposition="top center",
                textfont=dict(size=8, color='#E8E8E8'),
                hovertext=node_text,
                hoverinfo='text'
            ))
        
        # Crear figura
        fig = go.Figure(data=edge_trace + node_trace)
        
        fig.update_layout(
            showlegend=True,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            paper_bgcolor='#0D0D0D',
            plot_bgcolor='#0D0D0D',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            legend=dict(
                font=dict(color='#E8E8E8'),
                bgcolor='rgba(0,0,0,0.5)'
            ),
            height=600
        )
        
        return fig

# Instancia global
ontology = SupplyChainOntology()
