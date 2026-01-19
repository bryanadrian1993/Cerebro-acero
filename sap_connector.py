"""
CONECTOR SAP - Import Aceros S.A.
Módulo para integración con SAP ERP

INSTRUCCIONES:
1. Instalar librería: pip install pyrfc
2. Configurar credenciales en .streamlit/secrets.toml
3. Descomentar las funciones cuando tengas acceso a SAP

DATOS QUE SE EXTRAERÁN DE SAP:
- Inventario actual (MARD - Stock por almacén)
- Órdenes de compra (EKKO/EKPO)
- Proveedores (LFA1)
- Precios de compra (EINE)
- Movimientos de material (MSEG)
- Órdenes de venta (VBAK/VBAP)
"""

import pandas as pd
from datetime import datetime
import streamlit as st

# ========================================
# CONFIGURACIÓN SAP
# ========================================

# Descomentar cuando tengas las credenciales SAP Y hayas instalado: pip install pyrfc
"""
NOTA: pyrfc solo funciona LOCALMENTE (requiere SAP NetWeaver RFC SDK)
NO está disponible en Streamlit Cloud

Para instalar localmente:
1. Descargar SAP NetWeaver RFC SDK
2. pip install pyrfc

from pyrfc import Connection

def get_sap_connection():
    '''Establece conexión con SAP'''
    try:
        sap_config = {
            'user': st.secrets.get("SAP_USER", ""),
            'passwd': st.secrets.get("SAP_PASSWORD", ""),
            'ashost': st.secrets.get("SAP_HOST", ""),  # Servidor SAP
            'sysnr': st.secrets.get("SAP_SYSNR", "00"),  # Número de sistema
            'client': st.secrets.get("SAP_CLIENT", "100"),  # Mandante
        }
        
        conn = Connection(**sap_config)
        return conn
    except Exception as e:
        st.error(f"Error conectando a SAP: {str(e)}")
        return None
"""

# ========================================
# FUNCIONES DE EXTRACCIÓN SAP
# ========================================

def obtener_inventario_sap():
    """
    Obtiene inventario real desde SAP (Tabla MARD)
    
    CAMPOS SAP:
    - MATNR: Código de material
    - MAKTX: Descripción del material
    - WERKS: Centro (ej: 1000 = Quito)
    - LGORT: Almacén
    - LABST: Stock disponible
    - UMLME: Stock en tránsito
    - MEINS: Unidad de medida
    """
    
    # MODO SIMULADO (por ahora)
    # Cuando conectes a SAP, reemplazar con query RFC
    
    """
    # CÓDIGO REAL SAP (descomentar cuando tengas acceso):
    
    conn = get_sap_connection()
    if not conn:
        return pd.read_csv("inventario_simulado.csv")
    
    try:
        # RFC_READ_TABLE para leer MARD (Stock)
        result = conn.call('RFC_READ_TABLE',
            QUERY_TABLE='MARD',
            DELIMITER='|',
            FIELDS=[
                {'FIELDNAME': 'MATNR'},  # Material
                {'FIELDNAME': 'WERKS'},  # Centro
                {'FIELDNAME': 'LGORT'},  # Almacén
                {'FIELDNAME': 'LABST'},  # Stock
            ]
        )
        
        # Procesar datos SAP
        data = []
        for row in result['DATA']:
            fields = row['WA'].split('|')
            data.append({
                'sku': fields[0].strip(),
                'centro': fields[1].strip(),
                'almacen': fields[2].strip(),
                'stock_actual': float(fields[3].strip()),
            })
        
        df = pd.DataFrame(data)
        
        # Enriquecer con descripciones desde MAKT
        # ... más lógica aquí
        
        conn.close()
        return df
        
    except Exception as e:
        st.warning(f"Error SAP, usando datos simulados: {str(e)}")
        return pd.read_csv("inventario_simulado.csv")
    """
    
    # Por ahora, usar datos simulados
    return pd.read_csv("inventario_simulado.csv")


def obtener_ordenes_compra_sap():
    """
    Obtiene órdenes de compra desde SAP (Tablas EKKO/EKPO)
    
    CAMPOS SAP:
    - EBELN: Número de pedido
    - EBELP: Posición del pedido
    - LIFNR: Proveedor
    - MATNR: Material
    - MENGE: Cantidad
    - NETPR: Precio neto
    - EEIND: Fecha de entrega
    """
    
    """
    # CÓDIGO REAL SAP:
    conn = get_sap_connection()
    if not conn:
        return []
    
    try:
        result = conn.call('RFC_READ_TABLE',
            QUERY_TABLE='EKPO',
            DELIMITER='|',
            OPTIONS=[
                {'TEXT': "EEIND >= '20260101'"}  # Órdenes futuras
            ]
        )
        
        ordenes = []
        for row in result['DATA']:
            # Procesar datos...
            pass
        
        return ordenes
    except:
        return []
    """
    
    # Simulado por ahora
    return [
        {
            "pedido": "4500123456",
            "proveedor": "Tianjin Steel",
            "material": "Viga IPE 200mm",
            "cantidad": 500,
            "fecha_entrega": "2026-02-15",
            "estado": "En tránsito"
        },
        {
            "pedido": "4500123457",
            "proveedor": "Posco Korea",
            "material": "Tubería Inox 304",
            "cantidad": 200,
            "fecha_entrega": "2026-02-20",
            "estado": "Confirmado"
        }
    ]


def obtener_proveedores_sap():
    """
    Obtiene maestro de proveedores desde SAP (Tabla LFA1)
    
    CAMPOS SAP:
    - LIFNR: Código proveedor
    - NAME1: Nombre
    - LAND1: País
    - ORT01: Ciudad
    """
    
    return [
        {"codigo": "100001", "nombre": "Tianjin Steel Co.", "pais": "CN", "lead_time": 45},
        {"codigo": "100002", "nombre": "Posco", "pais": "KR", "lead_time": 35},
        {"codigo": "100003", "nombre": "Tosyali Iron & Steel", "pais": "TR", "lead_time": 50},
        {"codigo": "100004", "nombre": "ArcelorMittal India", "pais": "IN", "lead_time": 40},
    ]


def obtener_ventas_sap(meses=6):
    """
    Obtiene histórico de ventas desde SAP (VBAK/VBAP)
    
    Para análisis de demanda y forecasting
    """
    
    # Simulado - En SAP sería query a VBAP con agregación
    return pd.DataFrame({
        'mes': pd.date_range(start='2025-08-01', periods=6, freq='MS'),
        'ventas_usd': [250000, 280000, 310000, 295000, 320000, 340000],
        'unidades': [1200, 1350, 1480, 1400, 1520, 1600]
    })


def sincronizar_inventario_sap():
    """
    Función principal: Sincroniza inventario de SAP a la plataforma
    Se ejecutará automáticamente cada hora
    """
    
    # Sincronizando datos desde SAP...
    
    # 1. Obtener inventario
    df_inventario = obtener_inventario_sap()
    df_inventario.to_csv("inventario_real_sap.csv", index=False)
    
    # 2. Obtener órdenes de compra
    ordenes = obtener_ordenes_compra_sap()
    pd.DataFrame(ordenes).to_csv("ordenes_compra_sap.csv", index=False)
    
    # 3. Obtener proveedores
    proveedores = obtener_proveedores_sap()
    pd.DataFrame(proveedores).to_csv("proveedores_sap.csv", index=False)
    
    # 4. Obtener ventas
    df_ventas = obtener_ventas_sap()
    df_ventas.to_csv("ventas_historico_sap.csv", index=False)
    
    # Sincronización completada
    
    return {
        "inventario": df_inventario,
        "ordenes": ordenes,
        "proveedores": proveedores,
        "ventas": df_ventas
    }


# ========================================
# MODO HÍBRIDO: SAP + SIMULADO
# ========================================

def usar_datos_reales():
    """Verifica si hay credenciales SAP configuradas"""
    try:
        return bool(st.secrets.get("SAP_USER", ""))
    except:
        return False


def get_datos_empresa():
    """
    Función inteligente: Usa SAP si está configurado, sino usa simulados
    """
    import os
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(ruta_base, "inventario_simulado.csv")
    
    if usar_datos_reales():
        # Usando datos REALES de SAP
        return sincronizar_inventario_sap()
    else:
        # Modo SIMULADO
        return {
            "inventario": pd.read_csv(ruta_csv),
            "ordenes": obtener_ordenes_compra_sap(),
            "proveedores": obtener_proveedores_sap(),
            "ventas": obtener_ventas_sap()
        }


if __name__ == "__main__":
    # Test de conexión
    datos = get_datos_empresa()
    print(f"\nInventario: {len(datos['inventario'])} productos")
    print(f"Ordenes de compra: {len(datos['ordenes'])}")
    print(f"Proveedores: {len(datos['proveedores'])}")
    print(f"Meses de ventas: {len(datos['ventas'])}")
