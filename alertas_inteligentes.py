"""
SISTEMA DE ALERTAS INTELIGENTES
Genera alertas automáticas basadas en análisis de datos históricos
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class SistemaAlertas:
    def __init__(self, db_manager, ai_system):
        self.db = db_manager
        self.ai = ai_system
        self.alertas = []
    
    def generar_alertas(self):
        """Genera todas las alertas basadas en análisis de datos"""
        self.alertas = []
        
        # Alerta 1: Precio bajo promedio histórico
        self._alerta_precio_bajo()
        
        # Alerta 2: Proveedores con entregas tardías
        self._alerta_proveedores_tardios()
        
        # Alerta 3: Rutas con costo elevado
        self._alerta_rutas_costosas()
        
        # Alerta 4: Stock crítico con demanda alta
        self._alerta_stock_critico()
        
        # Alerta 5: Tendencia alcista de precios
        self._alerta_tendencia_precios()
        
        return self.alertas
    
    def _alerta_precio_bajo(self):
        """Detecta si precio actual está bajo promedio histórico"""
        df_precios = self.db.obtener_precios_historicos(dias=90)
        
        if df_precios.empty:
            return
        
        precio_promedio = df_precios['precio_internacional'].mean()
        precio_actual = df_precios['precio_internacional'].iloc[-1]
        
        diferencia_pct = ((precio_actual - precio_promedio) / precio_promedio) * 100
        
        if diferencia_pct < -15:  # 15% bajo promedio
            self.alertas.append({
                'tipo': 'OPORTUNIDAD',
                'titulo': f'💰 Precio del Acero {abs(diferencia_pct):.1f}% bajo promedio histórico',
                'descripcion': f'Precio actual: ${precio_actual:,.2f} vs Promedio 90 días: ${precio_promedio:,.2f}',
                'accion': '→ COMPRAR YA - Aprovechar precio bajo',
                'prioridad': 'ALTA',
                'icono': '🟢'
            })
        elif diferencia_pct > 15:  # 15% sobre promedio
            self.alertas.append({
                'tipo': 'ADVERTENCIA',
                'titulo': f'⚠️ Precio del Acero {diferencia_pct:.1f}% sobre promedio histórico',
                'descripcion': f'Precio actual: ${precio_actual:,.2f} vs Promedio 90 días: ${precio_promedio:,.2f}',
                'accion': '→ ESPERAR - Precio elevado, posible corrección',
                'prioridad': 'MEDIA',
                'icono': '🟡'
            })
    
    def _alerta_proveedores_tardios(self):
        """Detecta proveedores con alta tasa de retrasos"""
        df_proveedores = self.db.obtener_rendimiento_proveedores()
        
        if df_proveedores.empty:
            return
        
        # Identificar proveedores con cumplimiento < 70%
        proveedores_problematicos = df_proveedores[df_proveedores['tasa_cumplimiento'] < 70]
        
        for _, prov in proveedores_problematicos.iterrows():
            self.alertas.append({
                'tipo': 'RIESGO',
                'titulo': f'🚨 Proveedor {prov["proveedor"]} con {100-prov["tasa_cumplimiento"]:.0f}% entregas tardías',
                'descripcion': f'Retraso promedio: {prov["retraso_promedio"]:.1f} días. Total entregas: {prov["total_entregas"]:.0f}',
                'accion': '→ CAMBIAR PROVEEDOR - Buscar alternativa más confiable',
                'prioridad': 'ALTA',
                'icono': '🔴'
            })
    
    def _alerta_rutas_costosas(self):
        """Detecta rutas con costo 30% superior al promedio"""
        # Obtener datos de rutas logísticas
        conn = self.db.db_path
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        
        df_rutas = pd.read_sql_query('''
            SELECT origen, destino, AVG(costo_flete) as costo_promedio, COUNT(*) as total_usos
            FROM rutas_logisticas
            WHERE fecha >= date('now', '-90 days')
            GROUP BY origen, destino
        ''', conn)
        conn.close()
        
        if df_rutas.empty:
            return
        
        costo_global_promedio = df_rutas['costo_promedio'].mean()
        
        # Detectar rutas con costo > 30% sobre promedio
        rutas_costosas = df_rutas[df_rutas['costo_promedio'] > costo_global_promedio * 1.3]
        
        for _, ruta in rutas_costosas.iterrows():
            diferencia_pct = ((ruta['costo_promedio'] - costo_global_promedio) / costo_global_promedio) * 100
            
            self.alertas.append({
                'tipo': 'ADVERTENCIA',
                'titulo': f'📦 Ruta {ruta["origen"]}-{ruta["destino"]} +{diferencia_pct:.0f}% costo',
                'descripcion': f'Costo promedio: ${ruta["costo_promedio"]:,.2f} vs Promedio global: ${costo_global_promedio:,.2f}',
                'accion': '→ EVALUAR ALTERNATIVAS - Buscar rutas más económicas',
                'prioridad': 'MEDIA',
                'icono': '🟡'
            })
    
    def _alerta_stock_critico(self):
        """Detecta productos con stock bajo y demanda alta"""
        df_inv = self.db.obtener_inventarios_historicos(dias=7)
        
        if df_inv.empty:
            return
        
        # Obtener último snapshot por producto
        ultimo_inv = df_inv.sort_values('fecha').groupby('producto').last().reset_index()
        
        # Detectar productos con stock < stock_minimo
        productos_criticos = ultimo_inv[ultimo_inv['stock_actual'] < ultimo_inv['stock_minimo']]
        
        for _, prod in productos_criticos.iterrows():
            deficit = prod['stock_minimo'] - prod['stock_actual']
            
            self.alertas.append({
                'tipo': 'URGENTE',
                'titulo': f'⚡ {prod["producto"]} - Stock Crítico',
                'descripcion': f'Stock actual: {prod["stock_actual"]:.0f} | Mínimo: {prod["stock_minimo"]:.0f} | Déficit: {deficit:.0f}',
                'accion': '→ COMPRA URGENTE - Reponer stock inmediatamente',
                'prioridad': 'CRITICA',
                'icono': '🔴'
            })
    
    def _alerta_tendencia_precios(self):
        """Alerta sobre tendencia alcista de precios"""
        try:
            tendencia, cambio_pct = self.ai.predictor_precios.analizar_tendencia()
            
            if tendencia == "SUBIENDO" and cambio_pct > 5:
                self.alertas.append({
                    'tipo': 'PREDICCION',
                    'titulo': f'📈 Predicción: Precio subirá {cambio_pct:.1f}% en 30 días',
                    'descripcion': 'Modelo de IA detecta tendencia alcista en precio del acero',
                    'accion': '→ ANTICIPAR COMPRA - Comprar antes de la subida',
                    'prioridad': 'ALTA',
                    'icono': '🟡'
                })
            elif tendencia == "BAJANDO" and abs(cambio_pct) > 5:
                self.alertas.append({
                    'tipo': 'PREDICCION',
                    'titulo': f'📉 Predicción: Precio bajará {abs(cambio_pct):.1f}% en 30 días',
                    'descripcion': 'Modelo de IA detecta tendencia bajista en precio del acero',
                    'accion': '→ ESPERAR - Precio bajará, conviene esperar',
                    'prioridad': 'MEDIA',
                    'icono': '🟢'
                })
        except Exception as e:
            print(f"Error en alerta de tendencia: {e}")
    
    def mostrar_alertas(self):
        """Renderiza alertas en Streamlit"""
        if not self.alertas:
            st.success("✅ No hay alertas críticas - Todo funcionando correctamente")
            return
        
        # Ordenar por prioridad
        prioridades = {'CRITICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}
        self.alertas.sort(key=lambda x: prioridades.get(x['prioridad'], 99))
        
        st.markdown("### 🚨 Alertas Inteligentes Activas")
        st.markdown(f"**{len(self.alertas)} alertas detectadas**")
        st.markdown("---")
        
        for alerta in self.alertas:
            # Determinar color según tipo
            if alerta['tipo'] == 'URGENTE' or alerta['prioridad'] == 'CRITICA':
                st.error(f"{alerta['icono']} **{alerta['titulo']}**")
            elif alerta['tipo'] == 'ADVERTENCIA' or alerta['prioridad'] == 'ALTA':
                st.warning(f"{alerta['icono']} **{alerta['titulo']}**")
            elif alerta['tipo'] == 'OPORTUNIDAD':
                st.success(f"{alerta['icono']} **{alerta['titulo']}**")
            else:
                st.info(f"{alerta['icono']} **{alerta['titulo']}**")
            
            st.write(alerta['descripcion'])
            st.write(alerta['accion'])
            st.markdown("---")
    
    def obtener_resumen_alertas(self):
        """Retorna resumen de alertas para métricas"""
        if not self.alertas:
            return {
                'total': 0,
                'criticas': 0,
                'altas': 0,
                'medias': 0
            }
        
        return {
            'total': len(self.alertas),
            'criticas': sum(1 for a in self.alertas if a['prioridad'] == 'CRITICA'),
            'altas': sum(1 for a in self.alertas if a['prioridad'] == 'ALTA'),
            'medias': sum(1 for a in self.alertas if a['prioridad'] == 'MEDIA')
        }
