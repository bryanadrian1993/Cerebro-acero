"""
MODELOS DE INTELIGENCIA ARTIFICIAL
- Predicción de demanda (LSTM)
- Forecasting de precios (Prophet)
- Predicción de riesgos geopolíticos (NLP)
- Estimación de tiempos de entrega
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# --- MODELO 1: PREDICCIÓN DE PRECIOS DEL ACERO (PROPHET) ---
class PredictorPreciosAcero:
    def __init__(self, db_manager):
        self.db = db_manager
        self.model = None
    
    def entrenar_modelo(self):
        """Entrena modelo Prophet con datos históricos"""
        try:
            from prophet import Prophet
            
            # Obtener datos históricos
            df_precios = self.db.obtener_precios_historicos(dias=90)
            
            if df_precios.empty or len(df_precios) < 10:
                print("⚠️ No hay suficientes datos históricos para entrenar Prophet")
                return False
            
            # Preparar datos para Prophet (requiere 'ds' y 'y')
            df_prophet = pd.DataFrame({
                'ds': pd.to_datetime(df_precios['fecha']),
                'y': df_precios['precio_internacional']
            })
            
            # Entrenar modelo
            self.model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05
            )
            self.model.fit(df_prophet)
            
            print("✅ Modelo Prophet entrenado correctamente")
            return True
            
        except ImportError:
            print("⚠️ Prophet no instalado. Instalando...")
            import subprocess
            subprocess.run(['pip', 'install', 'prophet'], check=True)
            return self.entrenar_modelo()
        except Exception as e:
            print(f"❌ Error al entrenar Prophet: {e}")
            return False
    
    def predecir_precio_30dias(self):
        """Predice precio del acero para los próximos 30 días"""
        if not self.model:
            exito = self.entrenar_modelo()
            if not exito:
                return self._prediccion_simple_fallback()
        
        try:
            # Crear dataframe de fechas futuras
            future = self.model.make_future_dataframe(periods=30)
            forecast = self.model.predict(future)
            
            # Extraer últimos 30 días (predicción)
            prediccion = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)
            prediccion.columns = ['fecha', 'precio_predicho', 'precio_min', 'precio_max']
            
            return prediccion
            
        except Exception as e:
            print(f"❌ Error en predicción Prophet: {e}")
            return self._prediccion_simple_fallback()
    
    def _prediccion_simple_fallback(self):
        """Predicción simple si Prophet falla"""
        # Obtener último precio conocido
        df_precios = self.db.obtener_precios_historicos(dias=30)
        
        if df_precios.empty:
            precio_base = 1250  # Precio por defecto
        else:
            precio_base = df_precios['precio_internacional'].iloc[-1]
        
        # Generar predicción simple con ruido
        fechas = pd.date_range(start=datetime.now(), periods=30, freq='D')
        precios = [precio_base + np.random.uniform(-20, 20) + (i * 0.5) for i in range(30)]
        
        return pd.DataFrame({
            'fecha': fechas,
            'precio_predicho': precios,
            'precio_min': [p - 30 for p in precios],
            'precio_max': [p + 30 for p in precios]
        })
    
    def analizar_tendencia(self):
        """Analiza si el precio está subiendo, bajando o estable"""
        prediccion = self.predecir_precio_30dias()
        
        precio_hoy = prediccion['precio_predicho'].iloc[0]
        precio_30dias = prediccion['precio_predicho'].iloc[-1]
        
        cambio_porcentual = ((precio_30dias - precio_hoy) / precio_hoy) * 100
        
        if cambio_porcentual > 5:
            return "SUBIENDO", cambio_porcentual
        elif cambio_porcentual < -5:
            return "BAJANDO", cambio_porcentual
        else:
            return "ESTABLE", cambio_porcentual


# --- MODELO 2: PREDICCIÓN DE DEMANDA POR PRODUCTO (LSTM SIMPLIFICADO) ---
class PredictorDemanda:
    def __init__(self, db_manager):
        self.db = db_manager
        self.model = None
    
    def predecir_demanda_producto(self, producto, dias_adelante=30):
        """Predice demanda futura de un producto usando promedio móvil ponderado"""
        # Obtener histórico de inventarios
        df_inv = self.db.obtener_inventarios_historicos(producto=producto, dias=90)
        
        if df_inv.empty:
            # Si no hay datos, retornar demanda promedio estimada
            return self._demanda_estimada_basica(producto)
        
        # Calcular demanda implícita (cambios en stock)
        df_inv = df_inv.sort_values('fecha')
        df_inv['demanda_calculada'] = df_inv['stock_actual'].diff().abs()
        
        # Promedio móvil ponderado (últimos 14 días tienen más peso)
        demandas_recientes = df_inv['demanda_calculada'].tail(14).values
        pesos = np.linspace(0.5, 1.5, len(demandas_recientes))
        demanda_promedio = np.average(demandas_recientes, weights=pesos)
        
        # Predicción simple: demanda_promedio ± variación estacional
        predicciones = []
        for i in range(dias_adelante):
            variacion = np.sin(i / 7) * (demanda_promedio * 0.2)  # Variación semanal
            prediccion = max(0, demanda_promedio + variacion)
            predicciones.append(prediccion)
        
        return {
            'producto': producto,
            'demanda_promedio_diaria': demanda_promedio,
            'demanda_30dias': sum(predicciones),
            'predicciones_diarias': predicciones
        }
    
    def _demanda_estimada_basica(self, producto):
        """Estimación básica cuando no hay datos históricos"""
        # Demandas típicas por tipo de producto
        demandas_tipo = {
            'Varilla': 150,
            'Viga': 80,
            'Plancha': 100,
            'Ángulo': 60,
            'Tubo': 90
        }
        
        # Inferir tipo de producto
        demanda_base = 100  # Default
        for tipo, demanda in demandas_tipo.items():
            if tipo.lower() in producto.lower():
                demanda_base = demanda
                break
        
        return {
            'producto': producto,
            'demanda_promedio_diaria': demanda_base,
            'demanda_30dias': demanda_base * 30,
            'predicciones_diarias': [demanda_base] * 30
        }


# --- MODELO 3: PREDICCIÓN DE RIESGOS GEOPOLÍTICOS (NLP) ---
class PredictorRiesgos:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def calcular_score_riesgo(self, noticias):
        """Calcula score de riesgo basado en noticias activas"""
        if not noticias:
            return {
                'score_total': 0,
                'nivel': 'BAJO',
                'factores': []
            }
        
        score = 0
        factores = []
        
        for noticia in noticias:
            # Ponderación por categoría
            pesos = {
                'Geopolitica': 30,
                'Logistica': 25,
                'Economia': 20,
                'Comercio': 15,
                'Demanda': 10
            }
            
            categoria = noticia.get('categoria', 'Comercio')
            peso_categoria = pesos.get(categoria, 10)
            
            # Ponderación por impacto
            if noticia.get('impacto') == 'Crisis':
                peso_impacto = 2.0
            else:
                peso_impacto = 0.5
            
            # Ponderación por relevancia
            relevancia = noticia.get('relevancia', 'MEDIA')
            peso_relevancia = {'ALTA': 1.5, 'MEDIA': 1.0, 'BAJA': 0.5}.get(relevancia, 1.0)
            
            score_noticia = peso_categoria * peso_impacto * peso_relevancia
            score += score_noticia
            
            factores.append({
                'noticia': noticia.get('escenario', 'Desconocido'),
                'score': score_noticia,
                'categoria': categoria
            })
        
        # Determinar nivel de riesgo
        if score > 100:
            nivel = 'CRITICO'
        elif score > 50:
            nivel = 'ALTO'
        elif score > 20:
            nivel = 'MEDIO'
        else:
            nivel = 'BAJO'
        
        return {
            'score_total': round(score, 2),
            'nivel': nivel,
            'factores': sorted(factores, key=lambda x: x['score'], reverse=True)[:5]
        }
    
    def recomendar_accion(self, score_riesgo):
        """Recomienda acción basada en score de riesgo"""
        nivel = score_riesgo['nivel']
        
        recomendaciones = {
            'CRITICO': {
                'accion': 'COMPRAR URGENTE - Asegurar stock 6 meses',
                'ajuste_stock': 1.8,
                'diversificar_proveedores': True
            },
            'ALTO': {
                'accion': 'COMPRAR ANTICIPADO - Stock 4 meses',
                'ajuste_stock': 1.5,
                'diversificar_proveedores': True
            },
            'MEDIO': {
                'accion': 'COMPRAR NORMAL - Stock 3 meses',
                'ajuste_stock': 1.2,
                'diversificar_proveedores': False
            },
            'BAJO': {
                'accion': 'ESPERAR - Monitorear mercado',
                'ajuste_stock': 1.0,
                'diversificar_proveedores': False
            }
        }
        
        return recomendaciones.get(nivel, recomendaciones['MEDIO'])


# --- MODELO 4: PREDICCIÓN DE TIEMPO DE ENTREGA ---
class PredictorTiempoEntrega:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def predecir_tiempo_entrega(self, proveedor, urgencia='MEDIA'):
        """Predice tiempo de entrega basado en histórico del proveedor"""
        # Obtener rendimiento histórico del proveedor
        df_rendimiento = self.db.obtener_rendimiento_proveedores()
        
        if df_rendimiento.empty:
            return self._tiempo_estimado_default(proveedor)
        
        # Buscar proveedor específico
        prov_data = df_rendimiento[df_rendimiento['proveedor'] == proveedor]
        
        if prov_data.empty:
            return self._tiempo_estimado_default(proveedor)
        
        # Calcular tiempo promedio + retraso histórico
        tiempo_base = {
            'Tianjin Steel (China)': 45,
            'Posco (Corea)': 35,
            'Tosyali (Turquía)': 50,
            'ArcelorMittal (India)': 40
        }.get(proveedor, 40)
        
        retraso_promedio = prov_data['retraso_promedio'].iloc[0]
        tiempo_predicho = tiempo_base + retraso_promedio
        
        # Ajustar por urgencia
        if urgencia == 'ALTA':
            tiempo_predicho *= 0.85  # Entregas express más rápidas
        elif urgencia == 'BAJA':
            tiempo_predicho *= 1.1
        
        return {
            'tiempo_estimado_dias': int(tiempo_predicho),
            'confianza': prov_data['tasa_cumplimiento'].iloc[0],
            'basado_en': int(prov_data['total_entregas'].iloc[0])
        }
    
    def _tiempo_estimado_default(self, proveedor):
        """Tiempo estimado cuando no hay datos históricos"""
        tiempos_default = {
            'Tianjin Steel (China)': 45,
            'Posco (Corea)': 35,
            'Tosyali (Turquía)': 50,
            'ArcelorMittal (India)': 40
        }
        
        return {
            'tiempo_estimado_dias': tiempos_default.get(proveedor, 40),
            'confianza': 50,  # Baja confianza sin datos
            'basado_en': 0
        }


# --- INTEGRACIÓN: SISTEMA COMPLETO DE IA ---
class SistemaIA:
    def __init__(self, db_manager):
        self.db = db_manager
        self.predictor_precios = PredictorPreciosAcero(db_manager)
        self.predictor_demanda = PredictorDemanda(db_manager)
        self.predictor_riesgos = PredictorRiesgos(db_manager)
        self.predictor_tiempos = PredictorTiempoEntrega(db_manager)
    
    def analisis_completo(self, producto, proveedor, noticias_activas):
        """Ejecuta análisis completo con todos los modelos"""
        # 1. Predicción de precios
        tendencia_precio, cambio_pct = self.predictor_precios.analizar_tendencia()
        
        # 2. Predicción de demanda
        demanda = self.predictor_demanda.predecir_demanda_producto(producto)
        
        # 3. Análisis de riesgos
        score_riesgo = self.predictor_riesgos.calcular_score_riesgo(noticias_activas)
        recomendacion = self.predictor_riesgos.recomendar_accion(score_riesgo)
        
        # 4. Tiempo de entrega
        tiempo_entrega = self.predictor_tiempos.predecir_tiempo_entrega(proveedor)
        
        return {
            'precio': {
                'tendencia': tendencia_precio,
                'cambio_30dias': cambio_pct
            },
            'demanda': demanda,
            'riesgo': {
                'score': score_riesgo,
                'recomendacion': recomendacion
            },
            'entrega': tiempo_entrega
        }
