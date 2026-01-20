"""
SAP INTEGRATION MODULE - Import Aceros S.A.
============================================
Módulo para conectar con SAP ERP/S4HANA

ESTADO: Listo para conectar (modo simulación hasta tener credenciales)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ========================================
# ESTADO DE CONEXIÓN SAP
# ========================================

def verificar_conexion_sap():
    """
    Verifica si las credenciales SAP están configuradas
    Retorna: dict con estado y detalles
    """
    try:
        sap_host = st.secrets.get("SAP_HOST", "")
        sap_user = st.secrets.get("SAP_USER", "")
        sap_password = st.secrets.get("SAP_PASSWORD", "")
        sap_sysnr = st.secrets.get("SAP_SYSNR", "")
        sap_client = st.secrets.get("SAP_CLIENT", "")
        
        if sap_host and sap_user and sap_password:
            # Credenciales configuradas - intentar conexión real
            return {
                "conectado": True,
                "modo": "REAL",
                "host": sap_host,
                "mensaje": "✅ Conectado a SAP",
                "color": "green"
            }
        else:
            return {
                "conectado": False,
                "modo": "SIMULADO",
                "host": None,
                "mensaje": "⚠️ SAP no configurado - Datos simulados",
                "color": "orange"
            }
    except:
        return {
            "conectado": False,
            "modo": "SIMULADO",
            "host": None,
            "mensaje": "⚠️ SAP no configurado - Datos simulados",
            "color": "orange"
        }


def conectar_sap_real():
    """
    Conexión real a SAP usando pyrfc
    Solo funciona en servidor local con SAP NetWeaver RFC SDK
    """
    try:
        from pyrfc import Connection
        
        conn = Connection(
            user=st.secrets["SAP_USER"],
            passwd=st.secrets["SAP_PASSWORD"],
            ashost=st.secrets["SAP_HOST"],
            sysnr=st.secrets.get("SAP_SYSNR", "00"),
            client=st.secrets.get("SAP_CLIENT", "100")
        )
        return conn
    except ImportError:
        st.warning("⚠️ pyrfc no instalado. Ejecute: pip install pyrfc")
        return None
    except Exception as e:
        st.error(f"❌ Error SAP: {str(e)}")
        return None


# ========================================
# FUNCIONES DE DATOS SAP
# ========================================

def obtener_inventario_sap():
    """Obtiene inventario desde SAP o datos simulados"""
    
    estado = verificar_conexion_sap()
    
    if estado["modo"] == "REAL":
        # TODO: Implementar lectura real de SAP
        # conn = conectar_sap_real()
        # result = conn.call('RFC_READ_TABLE', QUERY_TABLE='MARD', ...)
        pass
    
    # DATOS SIMULADOS (realistas para Import Aceros)
    inventario = [
        {"sku": "VIG-IPE-200", "descripcion": "Viga IPE 200mm x 6m", "stock": 450, "ubicacion": "Bodega Quito", "proveedor": "Tianjin Steel", "costo_unit": 285.50, "lead_time": 45},
        {"sku": "VIG-IPE-300", "descripcion": "Viga IPE 300mm x 6m", "stock": 280, "ubicacion": "Bodega Quito", "proveedor": "Posco Korea", "costo_unit": 385.00, "lead_time": 35},
        {"sku": "VIG-HEA-200", "descripcion": "Viga HEA 200mm x 6m", "stock": 320, "ubicacion": "Bodega Guayaquil", "proveedor": "ArcelorMittal", "costo_unit": 310.25, "lead_time": 40},
        {"sku": "TUB-INX-2", "descripcion": "Tubería Inox 304 2\"", "stock": 1200, "ubicacion": "Bodega Quito", "proveedor": "Tianjin Steel", "costo_unit": 45.80, "lead_time": 45},
        {"sku": "TUB-INX-4", "descripcion": "Tubería Inox 304 4\"", "stock": 850, "ubicacion": "Bodega Quito", "proveedor": "Tosyali Turkey", "costo_unit": 89.50, "lead_time": 50},
        {"sku": "PLA-A36-6", "descripcion": "Plancha A36 6mm", "stock": 180, "ubicacion": "Bodega Guayaquil", "proveedor": "Posco Korea", "costo_unit": 520.00, "lead_time": 35},
        {"sku": "PLA-A36-10", "descripcion": "Plancha A36 10mm", "stock": 95, "ubicacion": "Bodega Quito", "proveedor": "Tianjin Steel", "costo_unit": 780.00, "lead_time": 45},
        {"sku": "ANG-L-3", "descripcion": "Ángulo L 3\" x 1/4\"", "stock": 2500, "ubicacion": "Bodega Quito", "proveedor": "ArcelorMittal India", "costo_unit": 28.50, "lead_time": 40},
        {"sku": "BAR-RED-1", "descripcion": "Barra Redonda 1\"", "stock": 3200, "ubicacion": "Bodega Guayaquil", "proveedor": "Local Ecuador", "costo_unit": 12.30, "lead_time": 5},
        {"sku": "TUB-GAL-2", "descripcion": "Tubería Galvanizada 2\"", "stock": 1800, "ubicacion": "Bodega Quito", "proveedor": "Tosyali Turkey", "costo_unit": 38.90, "lead_time": 50},
    ]
    
    return pd.DataFrame(inventario)


def obtener_ordenes_compra_sap():
    """Obtiene órdenes de compra abiertas desde SAP"""
    
    estado = verificar_conexion_sap()
    
    # DATOS SIMULADOS
    hoy = datetime.now()
    ordenes = [
        {
            "pedido": "4500001234",
            "proveedor": "Tianjin Steel Co.",
            "pais": "🇨🇳 China",
            "material": "Viga IPE 200mm",
            "cantidad": 500,
            "unidad": "Unidades",
            "valor_usd": 142750.00,
            "fecha_pedido": (hoy - timedelta(days=30)).strftime("%Y-%m-%d"),
            "fecha_entrega": (hoy + timedelta(days=15)).strftime("%Y-%m-%d"),
            "estado": "En tránsito",
            "puerto": "Manzanillo → Guayaquil"
        },
        {
            "pedido": "4500001235",
            "proveedor": "Posco",
            "pais": "🇰🇷 Corea",
            "material": "Tubería Inox 304",
            "cantidad": 2000,
            "unidad": "Metros",
            "valor_usd": 89500.00,
            "fecha_pedido": (hoy - timedelta(days=15)).strftime("%Y-%m-%d"),
            "fecha_entrega": (hoy + timedelta(days=20)).strftime("%Y-%m-%d"),
            "estado": "Producción",
            "puerto": "Busan → Guayaquil"
        },
        {
            "pedido": "4500001236",
            "proveedor": "Tosyali Iron & Steel",
            "pais": "🇹🇷 Turquía",
            "material": "Plancha A36 10mm",
            "cantidad": 150,
            "unidad": "Planchas",
            "valor_usd": 117000.00,
            "fecha_pedido": (hoy - timedelta(days=7)).strftime("%Y-%m-%d"),
            "fecha_entrega": (hoy + timedelta(days=43)).strftime("%Y-%m-%d"),
            "estado": "Confirmado",
            "puerto": "Iskenderun → Guayaquil"
        },
        {
            "pedido": "4500001237",
            "proveedor": "ArcelorMittal India",
            "pais": "🇮🇳 India",
            "material": "Ángulo L 3\"",
            "cantidad": 5000,
            "unidad": "Unidades",
            "valor_usd": 142500.00,
            "fecha_pedido": (hoy - timedelta(days=3)).strftime("%Y-%m-%d"),
            "fecha_entrega": (hoy + timedelta(days=37)).strftime("%Y-%m-%d"),
            "estado": "Pendiente pago",
            "puerto": "Mumbai → Guayaquil"
        }
    ]
    
    return ordenes


def obtener_proveedores_sap():
    """Obtiene maestro de proveedores desde SAP"""
    
    proveedores = [
        {
            "codigo": "100001",
            "nombre": "Tianjin Steel Co., Ltd.",
            "pais": "🇨🇳 China",
            "ciudad": "Tianjin",
            "lead_time_dias": 45,
            "calificacion": 4.5,
            "productos": ["Vigas IPE", "Tuberías Inox", "Planchas"],
            "contacto": "sales@tianjinsteel.cn",
            "volumen_anual_usd": 850000
        },
        {
            "codigo": "100002",
            "nombre": "Posco",
            "pais": "🇰🇷 Corea del Sur",
            "ciudad": "Pohang",
            "lead_time_dias": 35,
            "calificacion": 4.8,
            "productos": ["Tuberías Inox Premium", "Planchas A36"],
            "contacto": "export@posco.co.kr",
            "volumen_anual_usd": 620000
        },
        {
            "codigo": "100003",
            "nombre": "Tosyali Iron & Steel",
            "pais": "🇹🇷 Turquía",
            "ciudad": "Iskenderun",
            "lead_time_dias": 50,
            "calificacion": 4.2,
            "productos": ["Tuberías Galvanizadas", "Varillas"],
            "contacto": "international@tosyali.com.tr",
            "volumen_anual_usd": 420000
        },
        {
            "codigo": "100004",
            "nombre": "ArcelorMittal India",
            "pais": "🇮🇳 India",
            "ciudad": "Mumbai",
            "lead_time_dias": 40,
            "calificacion": 4.4,
            "productos": ["Ángulos", "Vigas HEA", "Perfiles"],
            "contacto": "exports@arcelormittal.in",
            "volumen_anual_usd": 380000
        }
    ]
    
    return proveedores


def obtener_ventas_historicas_sap():
    """Obtiene historial de ventas desde SAP"""
    
    # Simulación de ventas mensuales
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    ventas = []
    for i, mes in enumerate(meses):
        ventas.append({
            "mes": mes,
            "ventas_usd": random.randint(180000, 320000),
            "unidades": random.randint(800, 1500),
            "margen_pct": round(random.uniform(18, 28), 1)
        })
    
    return ventas


def obtener_cuentas_por_cobrar_sap():
    """Obtiene cuentas por cobrar desde SAP"""
    
    cuentas = [
        {"cliente": "Constructora Hidalgo", "monto": 45680.00, "vencimiento": "2026-01-25", "dias_vencido": 0},
        {"cliente": "Metalúrgica Andina", "monto": 32150.00, "vencimiento": "2026-01-15", "dias_vencido": 4},
        {"cliente": "Ingeniería Pacífico", "monto": 28900.00, "vencimiento": "2026-02-01", "dias_vencido": 0},
        {"cliente": "Aceros del Sur", "monto": 67200.00, "vencimiento": "2025-12-30", "dias_vencido": 20},
    ]
    
    return cuentas


def obtener_kpis_financieros_sap():
    """Obtiene KPIs financieros desde SAP"""
    
    return {
        "ventas_mes": 285000,
        "ventas_anio": 3150000,
        "margen_bruto": 22.5,
        "inventario_valor": 1850000,
        "cuentas_cobrar": 173930,
        "cuentas_pagar": 289000,
        "rotacion_inventario": 4.2,
        "dias_cobro_promedio": 38
    }


# ========================================
# COMPONENTE UI PARA SIDEBAR
# ========================================

def mostrar_estado_sap_sidebar():
    """Muestra el estado de conexión SAP en el sidebar"""
    
    estado = verificar_conexion_sap()
    
    st.markdown("---")
    st.markdown("### 🔌 **Conexión SAP**")
    
    if estado["modo"] == "REAL":
        st.success(estado["mensaje"])
        st.caption(f"Host: {estado['host']}")
    else:
        st.warning(estado["mensaje"])
        st.caption("Configurar en secrets.toml")
    
    # Mostrar datos resumidos
    with st.expander("📦 Inventario SAP", expanded=False):
        df_inv = obtener_inventario_sap()
        total_items = len(df_inv)
        valor_total = (df_inv['stock'] * df_inv['costo_unit']).sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Items", f"{total_items}")
        col2.metric("Valor", f"${valor_total:,.0f}")
        
        # Items con bajo stock
        bajo_stock = df_inv[df_inv['stock'] < 200]
        if len(bajo_stock) > 0:
            st.warning(f"⚠️ {len(bajo_stock)} items con stock bajo")
    
    with st.expander("📋 Órdenes Abiertas", expanded=False):
        ordenes = obtener_ordenes_compra_sap()
        total_valor = sum(o['valor_usd'] for o in ordenes)
        
        st.metric("Órdenes", f"{len(ordenes)}")
        st.metric("Valor Total", f"${total_valor:,.0f}")
        
        # Próximas entregas
        for orden in ordenes[:2]:
            st.caption(f"📦 {orden['material'][:20]}... - {orden['estado']}")


def mostrar_panel_sap_completo():
    """Panel completo de SAP para la sección principal"""
    
    estado = verificar_conexion_sap()
    
    st.subheader("🔌 Integración SAP ERP")
    
    # Estado de conexión
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if estado["modo"] == "REAL":
            st.success("✅ **CONECTADO**")
            st.caption(f"Host: {estado['host']}")
        else:
            st.warning("⚠️ **MODO DEMO**")
            st.caption("Datos simulados")
    
    with col2:
        st.info("📡 **Última sincronización**")
        st.caption(datetime.now().strftime("%H:%M:%S"))
    
    with col3:
        if st.button("🔄 Sincronizar Ahora"):
            st.rerun()
    
    st.markdown("---")
    
    # Tabs de datos SAP
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventario", "📋 Órdenes Compra", "🏭 Proveedores", "📊 KPIs"])
    
    with tab1:
        df_inv = obtener_inventario_sap()
        st.dataframe(df_inv, use_container_width=True)
        
        # Alertas de stock
        bajo_stock = df_inv[df_inv['stock'] < 200]
        if len(bajo_stock) > 0:
            st.warning(f"⚠️ {len(bajo_stock)} productos con stock bajo:")
            for _, row in bajo_stock.iterrows():
                st.caption(f"• {row['descripcion']} - Stock: {row['stock']} unidades")
    
    with tab2:
        ordenes = obtener_ordenes_compra_sap()
        df_ordenes = pd.DataFrame(ordenes)
        st.dataframe(df_ordenes[['pedido', 'proveedor', 'material', 'cantidad', 'valor_usd', 'estado', 'fecha_entrega']], use_container_width=True)
    
    with tab3:
        proveedores = obtener_proveedores_sap()
        for prov in proveedores:
            with st.expander(f"{prov['pais']} {prov['nombre']}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Lead Time", f"{prov['lead_time_dias']} días")
                col2.metric("Calificación", f"⭐ {prov['calificacion']}")
                col3.metric("Vol. Anual", f"${prov['volumen_anual_usd']:,}")
                st.caption(f"Productos: {', '.join(prov['productos'])}")
    
    with tab4:
        kpis = obtener_kpis_financieros_sap()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ventas Mes", f"${kpis['ventas_mes']:,}")
        col2.metric("Margen Bruto", f"{kpis['margen_bruto']}%")
        col3.metric("Rotación Inv.", f"{kpis['rotacion_inventario']}x")
        col4.metric("Días Cobro", f"{kpis['dias_cobro_promedio']} días")
