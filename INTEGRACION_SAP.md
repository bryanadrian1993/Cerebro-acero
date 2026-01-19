# 🔌 INTEGRACIÓN SAP - Import Aceros S.A.

## 📋 Requisitos Previos

### 1. Información SAP Necesaria
Necesitas obtener de tu departamento de TI:

```
- Host SAP: __________ (ej: sap.importaceros.com)
- Número de Sistema (SYSNR): __________ (ej: 00)
- Mandante (CLIENT): __________ (ej: 100)
- Usuario SAP: __________
- Contraseña SAP: __________
- RFC habilitado: ✅ Sí / ❌ No
```

### 2. Instalar Librería SAP

```bash
pip install pyrfc
```

**Nota:** `pyrfc` requiere SAP NetWeaver RFC SDK instalado en el servidor.

---

## 🔧 Configuración

### Paso 1: Agregar credenciales a `.streamlit/secrets.toml`

```toml
# Conexión SAP
SAP_USER = "tu-usuario-sap"
SAP_PASSWORD = "tu-password-sap"
SAP_HOST = "sap.importaceros.com"
SAP_SYSNR = "00"
SAP_CLIENT = "100"
```

### Paso 2: Activar módulo SAP

En `sap_connector.py`, descomentar las funciones marcadas con:
```python
# CÓDIGO REAL SAP (descomentar cuando tengas acceso):
```

### Paso 3: Modificar `app.py`

Reemplazar:
```python
df_inv = pd.read_csv("inventario_simulado.csv")
```

Por:
```python
from sap_connector import get_datos_empresa
datos_sap = get_datos_empresa()
df_inv = datos_sap["inventario"]
```

---

## 📊 Datos que se Extraerán de SAP

### 1. Inventario (Tabla MARD)
- ✅ Stock actual por almacén
- ✅ Stock en tránsito
- ✅ Ubicaciones
- ✅ Unidades de medida

### 2. Órdenes de Compra (EKKO/EKPO)
- ✅ Pedidos abiertos
- ✅ Fechas de entrega
- ✅ Proveedores
- ✅ Precios acordados

### 3. Maestro de Proveedores (LFA1)
- ✅ Datos de contacto
- ✅ Países de origen
- ✅ Lead times promedio

### 4. Ventas Históricas (VBAK/VBAP)
- ✅ Facturación por producto
- ✅ Tendencias de demanda
- ✅ Clientes principales

### 5. Movimientos de Material (MSEG)
- ✅ Entradas de mercancía
- ✅ Salidas por venta
- ✅ Traspasos entre almacenes

---

## 🔄 Sincronización Automática

La plataforma sincronizará datos de SAP cada:
- ⏰ **1 hora** - Inventario y órdenes
- ⏰ **6 horas** - Ventas y proveedores
- ⏰ **Diario** - Análisis de tendencias

---

## 🎯 Beneficios de la Integración

### Antes (Simulado):
- ❌ Datos ficticios
- ❌ Actualización manual
- ❌ No refleja realidad

### Después (SAP Real):
- ✅ **Datos en tiempo real** desde tu ERP
- ✅ **Sincronización automática** cada hora
- ✅ **Decisiones basadas** en tu inventario real
- ✅ **Alertas precisas** según tu stock actual
- ✅ **Órdenes de compra** sincronizadas
- ✅ **Proveedores reales** con lead times

---

## 🚀 Plan de Implementación

### Fase 1: Preparación (Ahora)
- ✅ Arquitectura lista
- ✅ Código preparado
- ⏳ Obtener credenciales SAP

### Fase 2: Conexión (Próximamente)
1. Configurar secrets.toml
2. Descomentar funciones SAP
3. Probar conexión
4. Validar datos

### Fase 3: Producción
1. Sincronización automática
2. Monitoreo de errores
3. Optimización de queries

---

## 📞 Soporte

### Si hay problemas de conexión:

1. **Verificar firewall**: SAP debe permitir conexiones RFC desde la IP del servidor
2. **Usuario SAP**: Debe tener permisos para leer tablas MARD, EKKO, EKPO, LFA1
3. **SAP Basis**: Contactar a equipo SAP Basis para habilitar RFC

### Contacto IT Import Aceros:
- Email: sistemas@importaceros.com
- Interno: Ext. ____

---

## 🔐 Seguridad

- ✅ Credenciales en `secrets.toml` (NO se suben a GitHub)
- ✅ Conexión encriptada RFC
- ✅ Solo lectura (no modifica datos SAP)
- ✅ Logs de acceso

---

**Estado Actual:** 🟡 Preparado para conexión
**Próximo Paso:** Obtener credenciales SAP de IT
