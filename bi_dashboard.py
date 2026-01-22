"""
DASHBOARD DE BUSINESS INTELLIGENCE
KPIs dinámicos y métricas de rendimiento
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

class BIDashboard:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def mostrar_kpis_principales(self):
        """Muestra KPIs principales en tarjetas"""
        stats = self.db.obtener_estadisticas_generales()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total Decisiones",
                value=stats['total_decisiones'],
                delta=None
            )
        
        with col2:
            st.metric(
                label="✅ Tasa de Éxito",
                value=f"{stats['tasa_exito']:.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                label="💰 Ahorro Promedio",
                value=f"${stats['ahorro_promedio']:,.0f}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="🏭 Proveedores Activos",
                value=stats['total_proveedores'],
                delta=None
            )
    
    def mostrar_rentabilidad_proveedores(self):
        """Muestra rentabilidad por proveedor"""
        st.markdown("### 💵 Rentabilidad por Proveedor")
        
        df_rendimiento = self.db.obtener_rendimiento_proveedores()
        
        if df_rendimiento.empty:
            st.info("No hay datos de rendimiento de proveedores aún")
            return
        
        # Crear gráfico de barras
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_rendimiento['proveedor'],
            y=df_rendimiento['tasa_cumplimiento'],
            name='Tasa Cumplimiento (%)',
            marker_color='#00ff88'
        ))
        
        fig.update_layout(
            title='Tasa de Cumplimiento por Proveedor',
            xaxis_title='Proveedor',
            yaxis_title='Cumplimiento (%)',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.dataframe(
            df_rendimiento[['proveedor', 'total_entregas', 'tasa_cumplimiento', 'retraso_promedio', 'precio_promedio']],
            use_container_width=True
        )
    
    def mostrar_rotacion_inventario(self):
        """Muestra ratio de rotación de inventario"""
        st.markdown("### 📦 Rotación de Inventario")
        
        # Obtener inventarios históricos
        df_inv = self.db.obtener_inventarios_historicos(dias=30)
        
        if df_inv.empty:
            st.info("No hay datos de inventario histórico")
            return
        
        # Agrupar por producto y calcular rotación promedio
        rotacion_por_producto = df_inv.groupby('producto').agg({
            'rotacion': 'mean',
            'stock_actual': 'mean',
            'demanda_mensual': 'mean'
        }).reset_index()
        
        # Gráfico de rotación
        fig = px.bar(
            rotacion_por_producto,
            x='producto',
            y='rotacion',
            title='Rotación Promedio por Producto (últimos 30 días)',
            color='rotacion',
            color_continuous_scale=['#ff4757', '#ffa502', '#00ff88']
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def mostrar_costo_adquisicion_vs_mercado(self):
        """Compara costo de adquisición vs precio de mercado"""
        st.markdown("### 📈 Costo de Adquisición vs Mercado")
        
        # Obtener precios históricos
        df_precios = self.db.obtener_precios_historicos(dias=30)
        
        if df_precios.empty:
            st.info("No hay datos de precios históricos")
            return
        
        # Obtener decisiones de compra
        df_decisiones = self.db.obtener_decisiones_historicas(dias=30)
        
        # Gráfico de línea: precio mercado vs compras realizadas
        fig = go.Figure()
        
        # Línea de precio de mercado
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df_precios['fecha']),
            y=df_precios['precio_internacional'],
            mode='lines',
            name='Precio Mercado',
            line=dict(color='#00ff88', width=2)
        ))
        
        # Puntos de compras realizadas
        if not df_decisiones.empty:
            compras = df_decisiones[df_decisiones['decision'] == 'COMPRAR']
            if not compras.empty:
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(compras['fecha']),
                    y=compras['precio_unitario'],
                    mode='markers',
                    name='Compras Realizadas',
                    marker=dict(size=10, color='#ff4757')
                ))
        
        fig.update_layout(
            title='Precio de Mercado vs Decisiones de Compra',
            xaxis_title='Fecha',
            yaxis_title='Precio (USD)',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            height=400,
            xaxis=dict(gridcolor='#2d3561'),
            yaxis=dict(gridcolor='#2d3561')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calcular ahorro/pérdida promedio
        if not df_decisiones.empty and not df_precios.empty:
            precio_mercado_promedio = df_precios['precio_internacional'].mean()
            precio_compra_promedio = df_decisiones['precio_unitario'].mean()
            diferencia = precio_mercado_promedio - precio_compra_promedio
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Precio Mercado Promedio", f"${precio_mercado_promedio:,.2f}")
            with col2:
                st.metric("Precio Compra Promedio", f"${precio_compra_promedio:,.2f}", delta=f"${diferencia:,.2f}")
    
    def mostrar_eficiencia_decisiones(self):
        """Muestra eficiencia de decisiones de compra"""
        st.markdown("### 🎯 Eficiencia de Decisiones")
        
        df_decisiones = self.db.obtener_decisiones_historicas(dias=90)
        
        if df_decisiones.empty:
            st.info("No hay decisiones registradas")
            return
        
        # Contar decisiones por tipo
        decisiones_count = df_decisiones['decision'].value_counts()
        
        # Gráfico de pie
        fig = go.Figure(data=[go.Pie(
            labels=decisiones_count.index,
            values=decisiones_count.values,
            marker=dict(colors=['#00ff88', '#ffa502', '#ff4757'])
        )])
        
        fig.update_layout(
            title='Distribución de Decisiones (últimos 90 días)',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar decisiones evaluadas
        decisiones_evaluadas = df_decisiones[df_decisiones['evaluado'] == 1]
        
        if not decisiones_evaluadas.empty:
            st.markdown("#### Resultados de Decisiones Evaluadas")
            
            col1, col2, col3 = st.columns(3)
            
            total_eval = len(decisiones_evaluadas)
            exitosas = len(decisiones_evaluadas[decisiones_evaluadas['resultado_real'] == 'EXITO'])
            fallidas = total_eval - exitosas
            
            with col1:
                st.metric("Total Evaluadas", total_eval)
            with col2:
                st.metric("Exitosas", exitosas, delta=f"{(exitosas/total_eval)*100:.1f}%")
            with col3:
                st.metric("Fallidas", fallidas)
    
    def mostrar_timeline_decisiones(self):
        """Muestra línea de tiempo de decisiones"""
        st.markdown("### ⏱️ Timeline de Decisiones")
        
        df_decisiones = self.db.obtener_decisiones_historicas(dias=30)
        
        if df_decisiones.empty:
            st.info("No hay decisiones en los últimos 30 días")
            return
        
        # Preparar datos para timeline
        df_decisiones['fecha'] = pd.to_datetime(df_decisiones['fecha'])
        df_decisiones_sorted = df_decisiones.sort_values('fecha', ascending=False)
        
        # Mostrar últimas 10 decisiones
        for _, decision in df_decisiones_sorted.head(10).iterrows():
            fecha_str = decision['fecha'].strftime('%Y-%m-%d %H:%M')
            
            # Color según decisión
            if decision['decision'] == 'COMPRAR':
                color = '🟢'
            elif decision['decision'] == 'ESPERAR':
                color = '🟡'
            else:
                color = '🔴'
            
            with st.expander(f"{color} {fecha_str} - {decision['producto']} ({decision['decision']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Proveedor:** {decision['proveedor']}")
                    st.write(f"**Cantidad:** {decision['cantidad']}")
                    st.write(f"**Precio Unitario:** ${decision['precio_unitario']:,.2f}")
                
                with col2:
                    st.write(f"**Urgencia:** {decision['urgencia']}")
                    st.write(f"**Tendencia Precio:** {decision['precio_acero_tendencia']}")
                    st.write(f"**Costo Total:** ${decision['costo_total']:,.2f}")
                
                if decision['evaluado'] == 1:
                    resultado_color = '✅' if decision['resultado_real'] == 'EXITO' else '❌'
                    st.write(f"**Resultado:** {resultado_color} {decision['resultado_real']}")
                    if decision['ganancia_perdida']:
                        st.write(f"**Ganancia/Pérdida:** ${decision['ganancia_perdida']:,.2f}")
    
    def mostrar_dashboard_completo(self):
        """Muestra dashboard completo de BI"""
        st.markdown("## 📊 Business Intelligence Dashboard")
        st.markdown("---")
        
        # KPIs principales
        self.mostrar_kpis_principales()
        st.markdown("---")
        
        # Sección de análisis
        col1, col2 = st.columns(2)
        
        with col1:
            self.mostrar_rentabilidad_proveedores()
        
        with col2:
            self.mostrar_eficiencia_decisiones()
        
        st.markdown("---")
        
        # Métricas financieras
        self.mostrar_costo_adquisicion_vs_mercado()
        
        st.markdown("---")
        
        # Timeline
        self.mostrar_timeline_decisiones()
