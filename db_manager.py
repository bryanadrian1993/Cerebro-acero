"""
GESTOR DE BASE DE DATOS HISTÓRICA
Almacena decisiones, precios, inventarios y noticias para aprendizaje continuo
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

class DatabaseManager:
    def __init__(self, db_path='cerebro_acero.db'):
        self.db_path = db_path
        self.inicializar_base_datos()
    
    def inicializar_base_datos(self):
        """Crea las tablas necesarias si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de decisiones de compra
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisiones_compra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                producto TEXT,
                cantidad INTEGER,
                proveedor TEXT,
                precio_unitario REAL,
                costo_total REAL,
                decision TEXT,
                urgencia TEXT,
                escenario_riesgo TEXT,
                precio_acero_tendencia TEXT,
                resultado_real TEXT,
                ganancia_perdida REAL,
                tiempo_entrega_real INTEGER,
                tiempo_entrega_estimado INTEGER,
                evaluado INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de precios históricos del acero
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS precios_acero (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                precio_internacional REAL,
                fuente TEXT,
                tipo_acero TEXT
            )
        ''')
        
        # Tabla de inventarios históricos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventarios_historicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                producto TEXT,
                stock_actual INTEGER,
                stock_minimo INTEGER,
                demanda_mensual INTEGER,
                rotacion REAL
            )
        ''')
        
        # Tabla de noticias clasificadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS noticias_clasificadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                titulo TEXT,
                descripcion TEXT,
                categoria TEXT,
                impacto TEXT,
                relevancia TEXT,
                escenario TEXT,
                impacto_real_mercado TEXT,
                precio_acero_antes REAL,
                precio_acero_despues REAL
            )
        ''')
        
        # Tabla de rendimiento de proveedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rendimiento_proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor TEXT,
                fecha_entrega TIMESTAMP,
                tiempo_prometido INTEGER,
                tiempo_real INTEGER,
                calidad_recibida TEXT,
                precio_pactado REAL,
                cumplimiento INTEGER
            )
        ''')
        
        # Tabla de rutas logísticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rutas_logisticas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                origen TEXT,
                destino TEXT,
                costo_flete REAL,
                tiempo_dias INTEGER,
                ruta_usada TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def registrar_decision_compra(self, decision_data):
        """Registra una decisión de compra para análisis futuro"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO decisiones_compra 
            (producto, cantidad, proveedor, precio_unitario, costo_total, decision, 
             urgencia, escenario_riesgo, precio_acero_tendencia, tiempo_entrega_estimado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision_data.get('producto'),
            decision_data.get('cantidad'),
            decision_data.get('proveedor'),
            decision_data.get('precio_unitario'),
            decision_data.get('costo_total'),
            decision_data.get('decision'),
            decision_data.get('urgencia'),
            decision_data.get('escenario_riesgo'),
            decision_data.get('precio_acero_tendencia'),
            decision_data.get('tiempo_entrega_estimado')
        ))
        
        conn.commit()
        conn.close()
    
    def registrar_precio_acero(self, precio, fuente='Manual', tipo_acero='Estandar'):
        """Registra precio del acero internacional"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO precios_acero (precio_internacional, fuente, tipo_acero)
            VALUES (?, ?, ?)
        ''', (precio, fuente, tipo_acero))
        
        conn.commit()
        conn.close()
    
    def registrar_inventario(self, inventario_data):
        """Registra snapshot del inventario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for producto in inventario_data:
            cursor.execute('''
                INSERT INTO inventarios_historicos 
                (producto, stock_actual, stock_minimo, demanda_mensual, rotacion)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                producto.get('producto'),
                producto.get('stock_actual'),
                producto.get('stock_minimo'),
                producto.get('demanda_mensual', 0),
                producto.get('rotacion', 0)
            ))
        
        conn.commit()
        conn.close()
    
    def registrar_noticia(self, noticia_data):
        """Registra noticia clasificada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO noticias_clasificadas 
            (titulo, descripcion, categoria, impacto, relevancia, escenario)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            noticia_data.get('titulo'),
            noticia_data.get('descripcion'),
            noticia_data.get('categoria'),
            noticia_data.get('impacto'),
            noticia_data.get('relevancia'),
            noticia_data.get('escenario')
        ))
        
        conn.commit()
        conn.close()
    
    def registrar_rendimiento_proveedor(self, rendimiento_data):
        """Registra rendimiento real de proveedor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rendimiento_proveedores 
            (proveedor, tiempo_prometido, tiempo_real, calidad_recibida, precio_pactado, cumplimiento)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            rendimiento_data.get('proveedor'),
            rendimiento_data.get('tiempo_prometido'),
            rendimiento_data.get('tiempo_real'),
            rendimiento_data.get('calidad_recibida'),
            rendimiento_data.get('precio_pactado'),
            rendimiento_data.get('cumplimiento')
        ))
        
        conn.commit()
        conn.close()
    
    def obtener_precios_historicos(self, dias=90):
        """Obtiene precios históricos para análisis de tendencias"""
        conn = sqlite3.connect(self.db_path)
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        df = pd.read_sql_query('''
            SELECT fecha, precio_internacional, tipo_acero
            FROM precios_acero
            WHERE fecha >= ?
            ORDER BY fecha
        ''', conn, params=(fecha_inicio,))
        
        conn.close()
        return df
    
    def obtener_decisiones_historicas(self, dias=90):
        """Obtiene decisiones pasadas para aprendizaje"""
        conn = sqlite3.connect(self.db_path)
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        df = pd.read_sql_query('''
            SELECT * FROM decisiones_compra
            WHERE fecha >= ?
            ORDER BY fecha DESC
        ''', conn, params=(fecha_inicio,))
        
        conn.close()
        return df
    
    def obtener_rendimiento_proveedores(self):
        """Calcula métricas de rendimiento de proveedores"""
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query('''
            SELECT 
                proveedor,
                COUNT(*) as total_entregas,
                AVG(CASE WHEN cumplimiento = 1 THEN 100 ELSE 0 END) as tasa_cumplimiento,
                AVG(tiempo_real - tiempo_prometido) as retraso_promedio,
                AVG(precio_pactado) as precio_promedio
            FROM rendimiento_proveedores
            GROUP BY proveedor
        ''', conn)
        
        conn.close()
        return df
    
    def obtener_inventarios_historicos(self, producto=None, dias=90):
        """Obtiene histórico de inventarios para análisis de rotación"""
        conn = sqlite3.connect(self.db_path)
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        if producto:
            df = pd.read_sql_query('''
                SELECT * FROM inventarios_historicos
                WHERE producto = ? AND fecha >= ?
                ORDER BY fecha
            ''', conn, params=(producto, fecha_inicio))
        else:
            df = pd.read_sql_query('''
                SELECT * FROM inventarios_historicos
                WHERE fecha >= ?
                ORDER BY fecha
            ''', conn, params=(fecha_inicio,))
        
        conn.close()
        return df
    
    def actualizar_resultado_decision(self, decision_id, resultado, ganancia_perdida, tiempo_real):
        """Actualiza el resultado real de una decisión (para aprendizaje supervisado)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE decisiones_compra 
            SET resultado_real = ?, ganancia_perdida = ?, tiempo_entrega_real = ?, evaluado = 1
            WHERE id = ?
        ''', (resultado, ganancia_perdida, tiempo_real, decision_id))
        
        conn.commit()
        conn.close()
    
    def obtener_estadisticas_generales(self):
        """Obtiene estadísticas generales para el dashboard"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {
            'total_decisiones': pd.read_sql_query('SELECT COUNT(*) as total FROM decisiones_compra', conn).iloc[0]['total'],
            'decisiones_evaluadas': pd.read_sql_query('SELECT COUNT(*) as total FROM decisiones_compra WHERE evaluado = 1', conn).iloc[0]['total'],
            'tasa_exito': 0,
            'ahorro_promedio': 0,
            'total_proveedores': pd.read_sql_query('SELECT COUNT(DISTINCT proveedor) as total FROM rendimiento_proveedores', conn).iloc[0]['total']
        }
        
        # Calcular tasa de éxito
        evaluadas = pd.read_sql_query('SELECT COUNT(*) as total FROM decisiones_compra WHERE evaluado = 1 AND resultado_real = "EXITO"', conn).iloc[0]['total']
        if stats['decisiones_evaluadas'] > 0:
            stats['tasa_exito'] = (evaluadas / stats['decisiones_evaluadas']) * 100
        
        # Calcular ahorro promedio
        ahorro = pd.read_sql_query('SELECT AVG(ganancia_perdida) as promedio FROM decisiones_compra WHERE evaluado = 1', conn).iloc[0]['promedio']
        stats['ahorro_promedio'] = ahorro if ahorro else 0
        
        conn.close()
        return stats
    
    def generar_datos_iniciales_demo(self):
        """Genera datos de demostración para que el sistema tenga históricos"""
        import random
        
        # Generar precios históricos (últimos 90 días)
        precios = []
        fecha_actual = datetime.now()
        precio_base = 1200
        
        for i in range(90, 0, -1):
            fecha = fecha_actual - timedelta(days=i)
            precio = precio_base + random.uniform(-50, 50) + (i * 0.5)  # Tendencia leve alcista
            precios.append((fecha, precio, 'Simulado', 'Estándar'))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO precios_acero (fecha, precio_internacional, fuente, tipo_acero) VALUES (?, ?, ?, ?)', precios)
        
        # Generar decisiones históricas
        productos = ['Varilla 12mm', 'Viga IPE 200', 'Plancha LAC 2mm', 'Ángulo 2x2']
        proveedores = ['Tianjin Steel (China)', 'Posco (Corea)', 'Tosyali (Turquía)', 'ArcelorMittal (India)']
        decisiones_hist = []
        
        for i in range(50):
            fecha = fecha_actual - timedelta(days=random.randint(1, 90))
            producto = random.choice(productos)
            proveedor = random.choice(proveedores)
            cantidad = random.randint(100, 1000)
            precio_unit = random.uniform(1000, 1500)
            decision = random.choice(['COMPRAR', 'ESPERAR'])
            urgencia = random.choice(['ALTA', 'MEDIA', 'BAJA'])
            
            decisiones_hist.append((
                fecha, producto, cantidad, proveedor, precio_unit, precio_unit * cantidad,
                decision, urgencia, 'Normal', 'ESTABLE', 40
            ))
        
        cursor.executemany('''
            INSERT INTO decisiones_compra 
            (fecha, producto, cantidad, proveedor, precio_unitario, costo_total, decision, urgencia, 
             escenario_riesgo, precio_acero_tendencia, tiempo_entrega_estimado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', decisiones_hist)
        
        # Generar rendimiento de proveedores
        rendimientos = []
        for _ in range(30):
            proveedor = random.choice(proveedores)
            tiempo_prom = random.randint(30, 60)
            tiempo_real = tiempo_prom + random.randint(-5, 15)
            cumplimiento = 1 if tiempo_real <= tiempo_prom else 0
            
            rendimientos.append((
                proveedor, fecha_actual - timedelta(days=random.randint(1, 60)),
                tiempo_prom, tiempo_real, random.choice(['A', 'A+', 'B+']), random.uniform(1000, 1300), cumplimiento
            ))
        
        cursor.executemany('''
            INSERT INTO rendimiento_proveedores 
            (proveedor, fecha_entrega, tiempo_prometido, tiempo_real, calidad_recibida, precio_pactado, cumplimiento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', rendimientos)
        
        conn.commit()
        conn.close()
        
        print("✅ Datos históricos de demostración generados")

# Instancia global
db = DatabaseManager()
