# 🇪🇨 GUÍA PASO A PASO: Activar APIs de Ecuador

## 📋 RESUMEN EJECUTIVO

| API | Costo | Tiempo Setup | Dificultad | Prioridad |
|-----|-------|--------------|------------|-----------|
| **Banco Central** | GRATIS | ✅ YA FUNCIONA | Fácil | 🔥 ALTA |
| **SENAE (Aduana)** | GRATIS | 2-3 días | Media | 🔥 CRÍTICA |
| **SRI** | GRATIS | 1 semana | Media | 🔥 ALTA |
| **Puerto Guayaquil** | GRATIS | 3-5 días | Media | 🟡 Media |
| **SuperCías** | GRATIS | ✅ YA FUNCIONA | Fácil | 🟡 Media |

---

## 1️⃣ BANCO CENTRAL DEL ECUADOR (BCE)

### ✅ ESTADO: YA FUNCIONA

**No requiere nada - API pública disponible**

```python
# Ya implementado en apis_ecuador.py
from apis_ecuador import obtener_indicadores_bce

datos = obtener_indicadores_bce()
print(f"Riesgo país: {datos['riesgo_pais']}")
print(f"Inflación: {datos['inflacion_anual']}%")
```

**Datos que obtienes:**
- ✅ Riesgo país (actualizado diariamente)
- ✅ Inflación mensual y anual
- ✅ Precio del petróleo
- ✅ Tasas de interés

**URL:** https://contenido.bce.fin.ec/

---

## 2️⃣ SENAE - SERVICIO NACIONAL DE ADUANA

### 🔒 REQUIERE: Credenciales ECUAPASS

### PASO A PASO:

#### **Día 1: Solicitud de Acceso**

1. **Ir al portal ECUAPASS**
   - URL: https://portal.aduana.gob.ec/
   - Clic en "Registro de Usuarios"

2. **Registrar tu RUC empresarial**
   ```
   RUC: 1791251237001 (Import Aceros S.A.)
   Representante Legal: [Nombre del gerente]
   Email corporativo: info@importaceros.com.ec
   ```

3. **Documentos que necesitas:**
   - ✅ RUC actualizado
   - ✅ Cédula representante legal
   - ✅ Nombramiento vigente
   - ✅ Papeleta de votación

#### **Día 2-3: Aprobación SENAE**

4. **Esperar email de aprobación** (1-2 días hábiles)
   - Recibirás usuario y contraseña temporal
   - Debes cambiar contraseña en primer login

#### **Día 3: Activar en la Plataforma**

5. **Agregar credenciales a `.streamlit/secrets.toml`**
   ```toml
   # SENAE - ECUAPASS
   SENAE_USER = "tu-usuario-ecuapass"
   SENAE_PASSWORD = "tu-password-seguro"
   SENAE_RUC = "1791251237001"
   ```

6. **Descomentar código en `apis_ecuador.py`**
   - Buscar línea: `# CÓDIGO REAL SENAE`
   - Descomentar funciones de consulta API

7. **Instalar librería (si necesario):**
   ```bash
   pip install zeep  # Para SOAP API de SENAE
   ```

#### **¿Qué podrás hacer?**

```python
# Consultar tus importaciones en tiempo real
importaciones = obtener_estado_importaciones_senae("1791251237001")

# Ver cada DAV (Declaración Aduanera)
for dav in importaciones['declaraciones']:
    print(f"DAV: {dav['numero_dav']}")
    print(f"Estado: {dav['estado']}")
    print(f"Tributos: ${dav['total_tributos_usd']:,.0f}")
    print(f"⚠️ Alerta: {dav['alerta']}")
```

**ALTERNATIVA SI NO TIENES ACCESO API:**
- Scraping web del portal (menos confiable)
- Ingreso manual de datos
- Excel con importaciones pendientes

---

## 3️⃣ SRI - SERVICIO DE RENTAS INTERNAS

### 🔒 REQUIERE: Firma Electrónica

### PASO A PASO:

#### **Semana 1: Obtener Firma Electrónica**

1. **Ir al Banco del Pacífico, Produbanco o Security Data**
   - Solicitar "Firma Electrónica para SRI"
   - Costo: ~$35-50/año
   - Documentos: RUC, cédula, papeleta votación

2. **Instalación:**
   - Descargar certificado .p12
   - Guardar en lugar seguro
   - NO COMPARTIR la contraseña

#### **Día 5-7: Registro en SRI en Línea**

3. **Portal SRI:**
   - URL: https://srienlinea.sri.gob.ec/
   - Clic en "Registro de Usuarios"
   - Usar firma electrónica para autenticación

4. **Activar servicios:**
   - ✅ Consultas en línea
   - ✅ Facturación electrónica
   - ✅ Declaraciones
   - ✅ DIMM (Anexos)

#### **Integración con Plataforma:**

5. **Opción 1: API SOAP del SRI**
   ```bash
   pip install suds-py3
   ```

   ```toml
   # En secrets.toml
   SRI_CERTIFICADO_PATH = "ruta/a/certificado.p12"
   SRI_CERTIFICADO_PASSWORD = "password-firma"
   SRI_RUC = "1791251237001"
   ```

6. **Opción 2: Web Scraping (más fácil)**
   ```python
   # Usar Selenium para automatizar consultas
   pip install selenium
   pip install webdriver-manager
   ```

**ALTERNATIVA MÁS SIMPLE:**
- Crear API interna en Excel
- Actualizar manualmente cada semana
- Exportar a CSV que lee la plataforma

---

## 4️⃣ PUERTO DE GUAYAQUIL - CONTECON

### 🔒 REQUIERE: Código de Usuario Puerto

### PASO A PASO:

#### **Día 1: Contactar Agente Naviero**

1. **Llamar a tu agente de aduanas**
   ```
   Ejemplo: 
   - Ecoatlantico
   - Ecuatoriana de Agenciamiento
   - Delnavsa
   ```

2. **Solicitar:**
   - Usuario para portal CONTECON
   - Acceso a tracking de contenedores
   - Consulta de tarifas

#### **Día 2-5: Aprobación Puerto**

3. **Documentos que piden:**
   - RUC de la empresa
   - Carta de autorización (tu agente te da formato)
   - Copia cédula representante legal

4. **Recibir credenciales:**
   - Usuario portal
   - Password temporal
   - Código de cliente

#### **Integración:**

5. **OPCIÓN FÁCIL: Usar VesselFinder (YA IMPLEMENTADO)**
   ```python
   # Ya funciona en apis_gratuitas_premium.py
   from apis_gratuitas_premium import generar_iframe_vesselfinder
   
   # Muestra mapas de barcos en tiempo real
   mapa = generar_iframe_vesselfinder("Guayaquil")
   ```

6. **OPCIÓN AVANZADA: API Puerto**
   - Portal: https://www.cgsa.com.ec/
   - Requiere desarrollo específico
   - Mejor usar VesselFinder (gratis, sin credenciales)

**RECOMENDACIÓN:**
- Por ahora usa VesselFinder (ya funciona)
- Más adelante si necesitas datos específicos del puerto, pídelo a tu agente

---

## 5️⃣ SUPERINTENDENCIA DE COMPAÑÍAS

### ✅ ESTADO: DATOS PÚBLICOS DISPONIBLES

**No requiere credenciales - Web Scraping**

#### **Opción 1: Portal Web Público**

1. **URL:** https://appscvsmovil.supercias.gob.ec/portaldeinformacion/

2. **Consultas disponibles:**
   - Estados financieros de competidores
   - Listado de empresas por sector
   - Accionistas y representantes

#### **Opción 2: API No Oficial (Web Scraping)**

```python
# Automatizar con Selenium o BeautifulSoup
pip install beautifulsoup4 requests

# Ya implementado en apis_ecuador.py
from apis_ecuador import consultar_competencia_supercias

competencia = consultar_competencia_supercias("importacion_acero")
print(competencia['empresas_sector'])
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN RECOMENDADO

### **SEMANA 1: APIs Gratuitas (0 credenciales)**
```
Día 1-2:
✅ Banco Central (ya funciona)
✅ SuperCías web scraping (ya funciona)
✅ VesselFinder para tracking barcos (ya funciona)

Resultado: 60% funcionalidad
```

### **SEMANA 2: Credenciales Básicas**
```
Día 1: Solicitar acceso ECUAPASS (SENAE)
Día 2-3: Esperar aprobación SENAE
Día 4: Integrar SENAE a plataforma
Día 5: Probar consultas aduana

Resultado: 80% funcionalidad
```

### **SEMANA 3-4: Firma Electrónica**
```
Día 1-5: Tramitar firma electrónica
Día 6-7: Registrar en SRI
Día 8: Integrar SRI (básico)
Día 9-10: Pruebas completas

Resultado: 100% funcionalidad
```

---

## 💡 SOLUCIÓN RÁPIDA (SIN CREDENCIALES)

### **Mientras consigues accesos oficiales:**

1. **Crea archivo CSV manual:** `datos_ecuador_manual.csv`
   ```csv
   fecha,dav_abiertas,tributos_pendientes,contenedores_puerto,riesgo_pais
   2026-01-19,3,167592,5,892
   ```

2. **La plataforma lee el CSV:**
   ```python
   # En app.py
   try:
       # Intentar API real
       datos = obtener_estado_importaciones_senae()
   except:
       # Fallback a CSV manual
       datos = pd.read_csv("datos_ecuador_manual.csv")
   ```

3. **Actualizas manualmente cada semana**
   - 15 minutos por semana
   - Datos suficientes para decisiones

---

## 📞 CONTACTOS ÚTILES

### **SENAE (Aduana)**
- Portal: https://portal.aduana.gob.ec/
- Teléfono: 1800-ADUANA (238262)
- Email: contacto@aduana.gob.ec
- Horario: Lun-Vie 8:00-17:00

### **SRI**
- Portal: https://www.sri.gob.ec/
- Teléfono: 1700-774-774
- Email: contacto@sri.gob.ec

### **Puerto Guayaquil**
- Portal: https://www.puertoguayaquil.gob.ec/
- Teléfono: (04) 248-8888

### **Firma Electrónica**
- Security Data: https://www.securitydata.net.ec/ | (02) 398-7800
- Banco del Pacífico: https://www.bancodelpacifico.com/

---

## ✅ CHECKLIST DE ACTIVACIÓN

```
APIs GRATIS (Ya funcionan):
☑ Banco Central Ecuador
☑ SuperCías (datos públicos)
☑ VesselFinder (tracking barcos)

APIs Requieren Registro (2-5 días):
☐ SENAE/ECUAPASS (solicitar acceso)
☐ Puerto Guayaquil (vía agente)

APIs Requieren Firma Electrónica (1-2 semanas):
☐ Obtener firma electrónica ($35-50)
☐ SRI en Línea (registro)
☐ API SRI (integración)
```

---

## 🎯 RESUMEN: ¿Qué Hacer HOY?

### **HOY (15 minutos):**
1. ✅ Verificar que BCE funciona (ya está)
2. ✅ Probar VesselFinder (ya está)
3. ✅ Crear archivo CSV manual con tus datos reales

### **ESTA SEMANA (2 horas):**
1. ☐ Ir a https://portal.aduana.gob.ec/ → Solicitar ECUAPASS
2. ☐ Llamar a tu agente de aduanas → Pedir usuario puerto
3. ☐ Llenar datos en `datos_ecuador_manual.csv`

### **PRÓXIMAS 2 SEMANAS (1 día):**
1. ☐ Tramitar firma electrónica (Security Data o banco)
2. ☐ Registrar en SRI en Línea
3. ☐ Activar APIs cuando tengas credenciales

---

## 🔥 BONUS: Integración Inteligente

### **La plataforma funciona EN CAPAS:**

```python
# Nivel 1: APIs gratuitas (BCE, VesselFinder) - ACTIVO
# Nivel 2: Datos manuales CSV - ACTIVO
# Nivel 3: APIs con credenciales (SENAE, SRI) - CUANDO TENGAS ACCESO

# El cerebro usa lo que esté disponible
# NO necesitas TODO para empezar
# Puedes ir agregando APIs gradualmente
```

**IMPORTANTE:** La plataforma YA ES ÚTIL con solo:
- ✅ Yahoo Finance (precios acero)
- ✅ Banco Central (riesgo país)
- ✅ VesselFinder (barcos)
- ✅ Datos CSV manuales

Las APIs de SENAE y SRI son **MEJORAS**, no requisitos.

---

¿Empezamos por crear el archivo CSV manual con tus datos reales de esta semana?
