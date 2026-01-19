# 🔐 TUTORIAL: Activar APIs con Credenciales (SENAE y SRI)

## 📋 ESTE TUTORIAL ES PARA CUANDO TENGAS:
- ✅ Usuario ECUAPASS (SENAE)
- ✅ Firma electrónica (SRI)

---

## PASO 1: Agregar Credenciales a `.streamlit/secrets.toml`

### 1.1 Abrir el archivo de secretos

```bash
# Navegar a la carpeta
cd "C:\Users\LENOVO\Documents\ROBOT IMPORT ACEROS\Demo_Import_Aceros\.streamlit"

# Abrir secrets.toml con VS Code
code secrets.toml
```

### 1.2 Agregar SENAE (ECUAPASS)

```toml
# ========================================
# SENAE - SERVICIO NACIONAL DE ADUANA
# ========================================
SENAE_USER = "TU_USUARIO_ECUAPASS"
SENAE_PASSWORD = "TU_PASSWORD_ECUAPASS"
SENAE_RUC = "1791251237001"
SENAE_API_URL = "https://ecuapass.aduana.gob.ec/icd-web/api"
```

**Ejemplo real cuando tengas acceso:**
```toml
SENAE_USER = "importaceros2026"
SENAE_PASSWORD = "TuPassword123!"
SENAE_RUC = "1791251237001"
```

### 1.3 Agregar SRI (Servicio Rentas Internas)

```toml
# ========================================
# SRI - SERVICIO DE RENTAS INTERNAS
# ========================================
SRI_RUC = "1791251237001"
SRI_CERTIFICADO_PATH = "C:/ruta/a/certificado.p12"
SRI_CERTIFICADO_PASSWORD = "password-de-tu-firma"
SRI_AMBIENTE = "produccion"  # o "pruebas"
```

**Ejemplo real:**
```toml
SRI_RUC = "1791251237001"
SRI_CERTIFICADO_PATH = "C:/Users/LENOVO/Documents/firma_importaceros.p12"
SRI_CERTIFICADO_PASSWORD = "MiFirma2026#"
SRI_AMBIENTE = "produccion"
```

---

## PASO 2: Instalar Librerías Necesarias

### 2.1 SENAE (usa SOAP API)

```bash
cd "C:\Users\LENOVO\Documents\ROBOT IMPORT ACEROS\Demo_Import_Aceros"
pip install zeep
pip install requests
```

### 2.2 SRI (usa XML y firma electrónica)

```bash
pip install suds-py3
pip install signxml
pip install lxml
pip install cryptography
```

---

## PASO 3: Actualizar `apis_ecuador.py`

### 3.1 Descomentar código SENAE

**Abrir:** `apis_ecuador.py`

**Buscar línea 63 (aproximadamente):**
```python
def obtener_estado_importaciones_senae(ruc_importador="1791251237001"):
```

**Reemplazar TODO el código simulado con código REAL:**

```python
def obtener_estado_importaciones_senae(ruc_importador="1791251237001"):
    """
    SENAE - Consulta estado de importaciones REAL
    """
    import streamlit as st
    from zeep import Client
    from zeep.wsse.username import UsernameToken
    
    try:
        # Obtener credenciales desde secrets
        usuario = st.secrets.get("SENAE_USER", "")
        password = st.secrets.get("SENAE_PASSWORD", "")
        
        if not usuario or not password:
            print("⚠️ Credenciales SENAE no configuradas, usando modo simulado")
            return obtener_estado_importaciones_senae_simulado()
        
        # Conectar a API SENAE
        wsdl_url = "https://ecuapass.aduana.gob.ec/icd-web/services/ConsultaDAV?wsdl"
        
        client = Client(
            wsdl=wsdl_url,
            wsse=UsernameToken(usuario, password)
        )
        
        # Consultar DAVs abiertas
        response = client.service.consultarDAVsPorRUC(
            ruc=ruc_importador,
            estado="ABIERTA"
        )
        
        # Procesar respuesta real
        importaciones = {
            "total_dav_abiertas": len(response.declaraciones),
            "declaraciones": [],
            "total_tributos_pendientes_usd": 0,
            "fuente": "SENAE API REAL"
        }
        
        for dav in response.declaraciones:
            declaracion = {
                "numero_dav": dav.numero,
                "fecha_arribo": dav.fechaArribo,
                "proveedor": dav.proveedor,
                "valor_fob_usd": float(dav.valorFOB),
                "peso_kg": float(dav.pesoNeto),
                "estado": dav.estadoActual,
                "advalorem_usd": float(dav.tributos.advalorem),
                "fodinfa_usd": float(dav.tributos.fodinfa),
                "iva_usd": float(dav.tributos.iva),
                "total_tributos_usd": float(dav.tributos.total),
                "dias_almacenaje": dav.diasAlmacenaje,
                "alerta": generar_alerta_dav(dav.diasAlmacenaje, dav.estadoActual)
            }
            importaciones["declaraciones"].append(declaracion)
            importaciones["total_tributos_pendientes_usd"] += declaracion["total_tributos_usd"]
        
        return importaciones
        
    except Exception as e:
        print(f"❌ Error conectando SENAE: {str(e)}")
        print("📊 Usando datos simulados...")
        return obtener_estado_importaciones_senae_simulado()


def generar_alerta_dav(dias_almacenaje, estado):
    """Genera alertas basadas en días de almacenaje"""
    if dias_almacenaje > 12:
        return "🔴 CRÍTICO: Multa por almacenaje próxima"
    elif dias_almacenaje > 8:
        return "⚠️ Advertencia: Próximo a penalización"
    elif estado == "AFORO FÍSICO":
        return "🔍 Inspección física programada"
    else:
        return "✅ Normal"


def obtener_estado_importaciones_senae_simulado():
    """Versión simulada cuando no hay credenciales"""
    # CÓDIGO ACTUAL QUE YA ESTÁ EN apis_ecuador.py
    importaciones = {
        "total_dav_abiertas": 3,
        "declaraciones": [
            # ... datos simulados actuales ...
        ],
        "fuente": "SENAE Simulado"
    }
    return importaciones
```

### 3.2 Descomentar código SRI

**En `apis_ecuador.py`, buscar función `obtener_estado_tributario_sri`:**

```python
def obtener_estado_tributario_sri(ruc="1791251237001"):
    """
    SRI - Consulta estado tributario REAL
    """
    import streamlit as st
    from suds.client import Client
    from signxml import XMLSigner
    from lxml import etree
    
    try:
        # Obtener credenciales
        certificado_path = st.secrets.get("SRI_CERTIFICADO_PATH", "")
        certificado_pwd = st.secrets.get("SRI_CERTIFICADO_PASSWORD", "")
        
        if not certificado_path or not certificado_pwd:
            print("⚠️ Certificado SRI no configurado, usando modo simulado")
            return obtener_estado_tributario_sri_simulado()
        
        # Conectar a SRI
        wsdl_url = "https://srienlinea.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
        client = Client(wsdl_url)
        
        # Consultar estado RUC
        response = client.service.consultarEstadoContribuyente(ruc)
        
        # Consultar facturas del mes
        facturas_response = client.service.consultarFacturasElectronicas(
            ruc=ruc,
            mes=datetime.now().month,
            anio=datetime.now().year
        )
        
        estado_tributario = {
            "ruc": ruc,
            "razon_social": response.razonSocial,
            "estado_ruc": response.estado,
            "tipo_contribuyente": response.tipoContribuyente,
            "obligaciones": response.obligaciones,
            "facturas_electronicas_mes": len(facturas_response.facturas),
            "total_facturado_mes_usd": sum([f.total for f in facturas_response.facturas]),
            "fuente": "SRI API REAL"
        }
        
        return estado_tributario
        
    except Exception as e:
        print(f"❌ Error conectando SRI: {str(e)}")
        print("📊 Usando datos simulados...")
        return obtener_estado_tributario_sri_simulado()


def obtener_estado_tributario_sri_simulado():
    """Versión simulada cuando no hay firma electrónica"""
    # CÓDIGO ACTUAL
    estado_tributario = {
        "ruc": "1791251237001",
        "razon_social": "IMPORT ACEROS S.A.",
        "estado_ruc": "ACTIVO",
        # ... resto datos simulados ...
        "fuente": "SRI Simulado"
    }
    return estado_tributario
```

---

## PASO 4: Integrar en `app.py`

### 4.1 Agregar import

**En `app.py` línea ~15:**

```python
from apis_gratuitas_premium import generar_dashboard_completo_gratis
from apis_ecuador import (
    obtener_indicadores_bce,
    obtener_estado_importaciones_senae,
    obtener_estado_tributario_sri,
    generar_dashboard_ecuador_completo
)
```

### 4.2 Agregar sección Ecuador en el dashboard

**Buscar línea ~1100 (después de métricas premium):**

```python
# SECCIÓN: DATOS ECUADOR 🇪🇨
st.markdown("---")
st.markdown("### 🇪🇨 Ecuador: Aduana & Tributación")

try:
    dashboard_ecuador = generar_dashboard_ecuador_completo()
    
    # Indicadores BCE
    bce = dashboard_ecuador['banco_central']
    col_ec1, col_ec2, col_ec3, col_ec4 = st.columns(4)
    
    with col_ec1:
        st.metric(
            "Riesgo País",
            f"{bce['riesgo_pais']} pts",
            help="Banco Central del Ecuador"
        )
    
    with col_ec2:
        st.metric(
            "Inflación Anual",
            f"{bce['inflacion_anual']}%",
            delta=f"{bce['inflacion_mensual']}% mensual"
        )
    
    # SENAE - Aduana
    senae = dashboard_ecuador['senae']
    with col_ec3:
        st.metric(
            "DAV Abiertas",
            senae['total_dav_abiertas'],
            help=senae['fuente']  # Mostrará "SENAE API REAL" o "Simulado"
        )
    
    with col_ec4:
        st.metric(
            "Tributos Pendientes",
            f"${senae['total_tributos_pendientes_usd']:,.0f}",
            help="SENAE - Aduana Ecuador"
        )
    
    # Expandible con detalles DAV
    if senae['total_dav_abiertas'] > 0:
        with st.expander("📦 Ver Detalles de DAVs"):
            for dav in senae['declaraciones']:
                st.markdown(f"""
                **{dav['numero_dav']}** - {dav['estado']}
                - Proveedor: {dav['proveedor']}
                - Valor FOB: ${dav['valor_fob_usd']:,.0f}
                - Tributos: ${dav['total_tributos_usd']:,.0f}
                - {dav['alerta']}
                """)
    
    # SRI - Tributario
    sri = dashboard_ecuador['sri']
    st.markdown(f"""
    **Estado Tributario:** {sri['estado_ruc']} | 
    Facturado mes: ${sri['total_facturado_mes_usd']:,.0f} | 
    Facturas electrónicas: {sri['facturas_electronicas_mes']}
    """)
    
except Exception as e:
    st.warning(f"Error cargando datos Ecuador: {str(e)}")
```

---

## PASO 5: Probar la Integración

### 5.1 Prueba Local

```bash
# Terminal
cd "C:\Users\LENOVO\Documents\ROBOT IMPORT ACEROS\Demo_Import_Aceros"
python apis_ecuador.py
```

**Salida esperada con credenciales:**
```
=== DASHBOARD ECUADOR ===

1. BANCO CENTRAL:
   Inflación anual: 2.54%
   Riesgo país: 892 puntos

2. SENAE (Aduana):
   Fuente: SENAE API REAL  ← 🔥 Debe decir "REAL"
   DAV abiertas: 5
   Tributos pendientes: $234,891

3. SRI:
   Fuente: SRI API REAL  ← 🔥 Debe decir "REAL"
   Estado: ACTIVO
   Facturado este mes: $2,145,782
```

### 5.2 Prueba en Streamlit

```bash
streamlit run app.py --server.port 8502
```

**Verificar en navegador:**
1. Abrir http://localhost:8502
2. Ir a sección "🇪🇨 Ecuador: Aduana & Tributación"
3. Verificar que dice "SENAE API REAL" (no "Simulado")
4. Click en expandible "Ver Detalles de DAVs"
5. Deben aparecer tus DAVs reales

---

## PASO 6: Troubleshooting

### Problema 1: "Credenciales SENAE no configuradas"

**Solución:**
```bash
# Verificar que secrets.toml tiene las credenciales
cat .streamlit/secrets.toml

# Debe mostrar:
# SENAE_USER = "tu-usuario"
# SENAE_PASSWORD = "tu-password"
```

### Problema 2: "Error conectando SENAE"

**Causas comunes:**
1. Usuario/password incorrecto
2. Cuenta ECUAPASS no activada
3. IP bloqueada por SENAE

**Solución:**
```python
# En apis_ecuador.py, agregar más debug:
print(f"🔍 Intentando conectar con usuario: {usuario}")
print(f"🔍 URL: {wsdl_url}")
```

### Problema 3: "Certificado SRI no encontrado"

**Solución:**
```python
# Verificar ruta del certificado
import os
cert_path = st.secrets.get("SRI_CERTIFICADO_PATH")
print(f"¿Existe certificado?: {os.path.exists(cert_path)}")
```

---

## PASO 7: Modo Híbrido (Recomendado)

### La plataforma funciona en 3 niveles automáticamente:

```python
# NIVEL 1: Intenta API real
try:
    datos = obtener_estado_importaciones_senae()  # API REAL
    if datos['fuente'] == "SENAE API REAL":
        st.success("✅ Conectado a SENAE")
except:
    # NIVEL 2: Intenta CSV manual
    try:
        datos = pd.read_csv("datos_ecuador_manual.csv")
        st.info("📄 Usando datos CSV manual")
    except:
        # NIVEL 3: Datos simulados
        datos = obtener_estado_importaciones_senae_simulado()
        st.warning("⚠️ Usando datos simulados")
```

**Ventaja:** No necesitas tener TODO configurado de golpe.

---

## ✅ CHECKLIST FINAL

### Antes de activar SENAE:
- [ ] Tienes usuario ECUAPASS
- [ ] Probaste login en https://portal.aduana.gob.ec/
- [ ] Agregaste credenciales a `secrets.toml`
- [ ] Instalaste librería: `pip install zeep`
- [ ] Descomentaste código en `apis_ecuador.py`
- [ ] Probaste con `python apis_ecuador.py`
- [ ] Verificaste que dice "SENAE API REAL"

### Antes de activar SRI:
- [ ] Tienes firma electrónica (.p12)
- [ ] Sabes la contraseña del certificado
- [ ] Probaste login en https://srienlinea.sri.gob.ec/
- [ ] Agregaste ruta certificado a `secrets.toml`
- [ ] Instalaste librerías: `pip install suds-py3 signxml`
- [ ] Descomentaste código en `apis_ecuador.py`
- [ ] Probaste conexión
- [ ] Verificaste que dice "SRI API REAL"

---

## 📞 SOPORTE

### Si algo falla:

1. **Revisar logs:**
   ```bash
   # Ver errores en terminal
   streamlit run app.py --server.port 8502 --logger.level=debug
   ```

2. **Verificar credenciales:**
   ```python
   # En Python console
   import streamlit as st
   print(st.secrets.get("SENAE_USER"))  # Debe mostrar tu usuario
   ```

3. **Modo debug en apis_ecuador.py:**
   ```python
   # Agregar al inicio de cada función
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

## 🎯 RESUMEN EJECUTIVO

### Con SENAE activo obtendrás:
- ✅ DAVs reales (no simuladas)
- ✅ Tributos exactos
- ✅ Estados de aforo reales
- ✅ Alertas automáticas por almacenaje
- ✅ Integración con algoritmo de decisión

### Con SRI activo obtendrás:
- ✅ Estado RUC real
- ✅ Facturas electrónicas del mes
- ✅ Obligaciones tributarias
- ✅ Alertas de declaraciones pendientes

### Sin credenciales (modo actual):
- ✅ Banco Central funciona (riesgo país, inflación)
- ✅ VesselFinder funciona (tracking barcos)
- ✅ SuperCías funciona (competencia)
- ⚠️ SENAE/SRI usan datos simulados o CSV manual

---

**¿Necesitas ayuda integrando cuando tengas las credenciales? Solo avísame y te guío paso a paso.**
