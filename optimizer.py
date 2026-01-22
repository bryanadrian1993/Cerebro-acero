"""
OPTIMIZADOR Y SIMULADOR DE ESCENARIOS
- Optimización de cartera de proveedores
- Calculadora de punto de reorden
- Simulador What-If
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class OptimizadorProveedores:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def optimizar_cartera(self, presupuesto_total, productos_necesarios):
        """
        Optimiza la cartera de proveedores para diversificación inteligente
        Minimiza riesgo y maximiza calidad dentro del presupuesto
        """
        
        # Base de proveedores con características
        proveedores = [
            {
                'nombre': 'Tianjin Steel (China)',
                'precio_factor': 1.0,
                'tiempo_entrega': 45,
                'calidad': 'A',
                'riesgo_geopolitico': 0.3,
                'capacidad_mensual': 5000
            },
            {
                'nombre': 'Posco (Corea)',
                'precio_factor': 1.15,
                'tiempo_entrega': 35,
                'calidad': 'A+',
                'riesgo_geopolitico': 0.1,
                'capacidad_mensual': 4000
            },
            {
                'nombre': 'Tosyali (Turquía)',
                'precio_factor': 0.95,
                'tiempo_entrega': 50,
                'calidad': 'B+',
                'riesgo_geopolitico': 0.2,
                'capacidad_mensual': 3500
            },
            {
                'nombre': 'ArcelorMittal (India)',
                'precio_factor': 1.05,
                'tiempo_entrega': 40,
                'calidad': 'A',
                'riesgo_geopolitico': 0.15,
                'capacidad_mensual': 4500
            }
        ]
        
        # Obtener rendimiento histórico
        df_rendimiento = self.db.obtener_rendimiento_proveedores()
        
        # Ajustar scores con datos reales si existen
        for prov in proveedores:
            if not df_rendimiento.empty:
                hist = df_rendimiento[df_rendimiento['proveedor'] == prov['nombre']]
                if not hist.empty:
                    # Ajustar tiempo por rendimiento real
                    prov['tiempo_entrega'] += hist['retraso_promedio'].iloc[0]
                    # Ajustar riesgo por tasa de cumplimiento
                    cumplimiento = hist['tasa_cumplimiento'].iloc[0]
                    prov['riesgo_operacional'] = (100 - cumplimiento) / 100
        
        # Estrategia de diversificación: 
        # - No más del 40% del presupuesto a un solo proveedor
        # - Priorizar proveedores con bajo riesgo geopolítico
        # - Balancear precio vs calidad
        
        asignaciones = []
        presupuesto_restante = presupuesto_total
        
        # Calcular score para cada proveedor
        for prov in proveedores:
            # Score = (calidad / precio) * (1 - riesgo_total)
            calidad_score = {'A+': 10, 'A': 8, 'B+': 6, 'B': 4}.get(prov['calidad'], 5)
            riesgo_total = prov['riesgo_geopolitico'] + prov.get('riesgo_operacional', 0.1)
            
            score = (calidad_score / prov['precio_factor']) * (1 - riesgo_total)
            prov['score'] = score
        
        # Ordenar por score
        proveedores_ordenados = sorted(proveedores, key=lambda x: x['score'], reverse=True)
        
        # Asignar presupuesto proporcionalmente
        total_score = sum(p['score'] for p in proveedores_ordenados)
        
        for prov in proveedores_ordenados:
            # Asignar proporcionalmente pero con límite del 40%
            asignacion_ideal = (prov['score'] / total_score) * presupuesto_total
            asignacion_maxima = presupuesto_total * 0.4
            
            asignacion = min(asignacion_ideal, asignacion_maxima, presupuesto_restante)
            
            if asignacion > 0:
                asignaciones.append({
                    'proveedor': prov['nombre'],
                    'presupuesto_asignado': asignacion,
                    'porcentaje': (asignacion / presupuesto_total) * 100,
                    'tiempo_entrega': prov['tiempo_entrega'],
                    'calidad': prov['calidad'],
                    'riesgo_total': prov['riesgo_geopolitico'] + prov.get('riesgo_operacional', 0.1),
                    'score': prov['score']
                })
                
                presupuesto_restante -= asignacion
        
        return pd.DataFrame(asignaciones)
    
    def mostrar_optimizacion(self):
        """Muestra interfaz de optimización de proveedores"""
        st.markdown("### 🎯 Optimizador de Cartera de Proveedores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            presupuesto = st.number_input(
                "Presupuesto Total (USD)",
                min_value=10000,
                max_value=10000000,
                value=500000,
                step=10000
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("🚀 Optimizar Cartera"):
                df_optim = self.optimizar_cartera(presupuesto, [])
                
                st.markdown("#### Asignación Óptima de Proveedores")
                st.dataframe(df_optim[['proveedor', 'presupuesto_asignado', 'porcentaje', 'calidad', 'tiempo_entrega']], 
                           use_container_width=True)
                
                # Gráfico de distribución
                import plotly.graph_objects as go
                
                fig = go.Figure(data=[go.Pie(
                    labels=df_optim['proveedor'],
                    values=df_optim['presupuesto_asignado'],
                    textinfo='label+percent',
                    marker=dict(colors=['#00ff88', '#ffa502', '#ff4757', '#5f27cd'])
                )])
                
                fig.update_layout(
                    title='Distribución de Presupuesto',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Recomendaciones
                st.success(f"✅ Cartera diversificada con {len(df_optim)} proveedores")
                st.info(f"⏱️ Tiempo promedio de entrega: {df_optim['tiempo_entrega'].mean():.0f} días")


class CalculadoraPuntoReorden:
    def __init__(self, db_manager, ai_system):
        self.db = db_manager
        self.ai = ai_system
    
    def calcular_punto_reorden(self, producto, lead_time_dias, stock_seguridad_pct=20):
        """
        Calcula punto de reorden automático
        Punto de Reorden = (Demanda Diaria * Lead Time) + Stock de Seguridad
        """
        
        # Obtener predicción de demanda
        prediccion = self.ai.predictor_demanda.predecir_demanda_producto(producto)
        
        demanda_diaria = prediccion['demanda_promedio_diaria']
        
        # Calcular stock de seguridad (% de la demanda durante lead time)
        demanda_durante_lead_time = demanda_diaria * lead_time_dias
        stock_seguridad = demanda_durante_lead_time * (stock_seguridad_pct / 100)
        
        punto_reorden = demanda_durante_lead_time + stock_seguridad
        
        return {
            'producto': producto,
            'demanda_diaria': demanda_diaria,
            'lead_time_dias': lead_time_dias,
            'demanda_durante_lead_time': demanda_durante_lead_time,
            'stock_seguridad': stock_seguridad,
            'punto_reorden': punto_reorden,
            'stock_seguridad_pct': stock_seguridad_pct
        }
    
    def mostrar_calculadora(self):
        """Muestra interfaz de calculadora de punto de reorden"""
        st.markdown("### 📊 Calculadora de Punto de Reorden")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            producto = st.selectbox(
                "Producto",
                ['Varilla 12mm', 'Viga IPE 200', 'Plancha LAC 2mm', 'Ángulo 2x2', 'Tubo 2"']
            )
        
        with col2:
            lead_time = st.number_input(
                "Lead Time (días)",
                min_value=1,
                max_value=120,
                value=40
            )
        
        with col3:
            stock_seg = st.number_input(
                "Stock Seguridad (%)",
                min_value=10,
                max_value=50,
                value=20
            )
        
        if st.button("📐 Calcular Punto de Reorden"):
            resultado = self.calcular_punto_reorden(producto, lead_time, stock_seg)
            
            st.markdown("#### Resultado del Cálculo")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Demanda Diaria", f"{resultado['demanda_diaria']:.0f} unidades")
            
            with col_b:
                st.metric("Stock de Seguridad", f"{resultado['stock_seguridad']:.0f} unidades")
            
            with col_c:
                st.metric("**PUNTO DE REORDEN**", f"{resultado['punto_reorden']:.0f} unidades")
            
            st.info(f"""
            **Interpretación:**
            - Cuando el stock llegue a **{resultado['punto_reorden']:.0f} unidades**, realizar pedido
            - El pedido cubrirá la demanda durante los {lead_time} días de espera
            - Más {stock_seg}% de stock de seguridad para imprevistos
            """)


class SimuladorEscenarios:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def simular_guerra_comercial(self):
        """Simula escenario: Guerra Comercial China-USA"""
        
        escenario = {
            'nombre': 'Guerra Comercial China-USA',
            'descripcion': 'Aranceles del 50% a importaciones desde China',
            'impactos': []
        }
        
        # Proveedor afectado: China
        escenario['impactos'].append({
            'area': 'Proveedores',
            'descripcion': 'Tianjin Steel (China) se encarece 50%',
            'accion': '→ Cambiar a Posco (Corea) o ArcelorMittal (India)'
        })
        
        escenario['impactos'].append({
            'area': 'Precios',
            'descripcion': 'Precio del acero subiría 30-40%',
            'accion': '→ Comprar stock de 6 meses AHORA antes del arancel'
        })
        
        escenario['impactos'].append({
            'area': 'Logística',
            'descripcion': 'Rutas desde China pueden tener inspecciones extras (+10 días)',
            'accion': '→ Preferir rutas desde Corea/Turquía'
        })
        
        # Calcular impacto financiero
        precio_actual = 1200
        precio_con_arancel = precio_actual * 1.5
        
        escenario['impacto_financiero'] = {
            'precio_antes': precio_actual,
            'precio_despues': precio_con_arancel,
            'aumento_pct': 50,
            'recomendacion': 'COMPRAR YA - Ahorro potencial: $600/tonelada'
        }
        
        return escenario
    
    def simular_petroleo_alto(self):
        """Simula escenario: Petróleo sube 40%"""
        
        escenario = {
            'nombre': 'Petróleo sube 40%',
            'descripcion': 'Crisis energética global, petróleo a $120/barril',
            'impactos': []
        }
        
        escenario['impactos'].append({
            'area': 'Fletes Marítimos',
            'descripcion': 'Costo de flete marítimo aumenta 35-40%',
            'accion': '→ Priorizar proveedores cercanos (menos flete)'
        })
        
        escenario['impactos'].append({
            'area': 'Rutas Óptimas',
            'descripcion': 'Ruta Turquía-Ecuador más económica que China-Ecuador',
            'accion': '→ Cambiar a Tosyali (Turquía) - ruta más corta'
        })
        
        escenario['impactos'].append({
            'area': 'Flete Terrestre',
            'descripcion': 'Distribución interna Ecuador +25% costo',
            'accion': '→ Consolidar envíos, optimizar rutas locales'
        })
        
        # Calcular impacto en landed cost
        fob = 60000
        flete_actual = 3000
        flete_nuevo = flete_actual * 1.4
        
        escenario['impacto_financiero'] = {
            'flete_antes': flete_actual,
            'flete_despues': flete_nuevo,
            'aumento_costo_landed': flete_nuevo - flete_actual,
            'recomendacion': 'Cambiar a proveedores más cercanos - Ahorro: $1,200 por contenedor'
        }
        
        return escenario
    
    def mostrar_simulador(self):
        """Muestra interfaz del simulador de escenarios"""
        st.markdown("### 🔮 Simulador de Escenarios What-If")
        
        escenario_seleccionado = st.selectbox(
            "Selecciona un escenario para simular",
            ['Guerra Comercial China-USA', 'Petróleo sube 40%', 'Bloqueo Canal de Suez', 'Crisis económica global']
        )
        
        if st.button("▶️ Simular Escenario"):
            if escenario_seleccionado == 'Guerra Comercial China-USA':
                resultado = self.simular_guerra_comercial()
            elif escenario_seleccionado == 'Petróleo sube 40%':
                resultado = self.simular_petroleo_alto()
            else:
                st.warning("Escenario en desarrollo")
                return
            
            st.markdown(f"## 🎬 Simulación: {resultado['nombre']}")
            st.info(resultado['descripcion'])
            st.markdown("---")
            
            st.markdown("### 📋 Impactos Detectados")
            
            for impacto in resultado['impactos']:
                with st.expander(f"**{impacto['area']}**"):
                    st.write(f"**Impacto:** {impacto['descripcion']}")
                    st.success(impacto['accion'])
            
            st.markdown("---")
            st.markdown("### 💰 Impacto Financiero")
            
            if escenario_seleccionado == 'Guerra Comercial China-USA':
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Precio Antes", f"${resultado['impacto_financiero']['precio_antes']:,.0f}")
                
                with col2:
                    st.metric("Precio Después", f"${resultado['impacto_financiero']['precio_despues']:,.0f}",
                            delta=f"+{resultado['impacto_financiero']['aumento_pct']}%")
                
                with col3:
                    st.write("")
                
                st.error(f"⚠️ {resultado['impacto_financiero']['recomendacion']}")
            
            elif escenario_seleccionado == 'Petróleo sube 40%':
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Flete Antes", f"${resultado['impacto_financiero']['flete_antes']:,.0f}")
                
                with col2:
                    st.metric("Flete Después", f"${resultado['impacto_financiero']['flete_despues']:,.0f}",
                            delta=f"+${resultado['impacto_financiero']['aumento_costo_landed']:,.0f}")
                
                st.warning(f"⚠️ {resultado['impacto_financiero']['recomendacion']}")
