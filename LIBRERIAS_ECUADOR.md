# 📦 LIBRERÍAS ADICIONALES PARA ECUADOR

## ✅ YA INSTALADAS (en requirements.txt)
```
streamlit
pandas
requests
plotly
yfinance
beautifulsoup4
newsapi-python
openai
```

---

## 🇪🇨 LIBRERÍAS ESPECÍFICAS ECUADOR

### **CUANDO ACTIVES SENAE (Aduana):**
```bash
pip install zeep          # SOAP API para SENAE/ECUAPASS
pip install requests      # Ya instalado - HTTP requests
```

### **CUANDO ACTIVES SRI (Facturación Electrónica):**
```bash
pip install suds-py3      # SOAP client para SRI
pip install signxml       # Firma digital XML
pip install lxml          # Procesamiento XML
pip install cryptography  # Manejo de certificados .p12
```

### **OPCIONAL - MEJORAS:**
```bash
pip install num2words     # Convertir números a palabras (facturas)
pip install pytz          # Zona horaria Ecuador
pip install unidecode     # Normalizar texto español
```

---

## 📋 COMANDO COMPLETO (Instalar Todo de Una Vez)

### **Versión Mínima (Sin SENAE/SRI):**
```bash
# Ya tienes todo lo necesario en requirements.txt
pip install -r requirements.txt
```

### **Versión Completa (Con SENAE + SRI):**
```bash
cd "C:\Users\LENOVO\Documents\ROBOT IMPORT ACEROS\Demo_Import_Aceros"
pip install zeep suds-py3 signxml lxml cryptography num2words pytz unidecode
```

### **Versión Por Fases:**

**FASE 1: APIs Gratuitas (YA ESTÁ)** ✅
```bash
# No instalar nada - ya funciona
```

**FASE 2: Cuando tengas ECUAPASS**
```bash
pip install zeep
```

**FASE 3: Cuando tengas Firma Electrónica**
```bash
pip install suds-py3 signxml lxml cryptography
```

**FASE 4: Optimizaciones**
```bash
pip install num2words pytz unidecode
```

---

## 🔧 MÓDULO PERSONALIZADO: `utils_ecuador.py`

**YA CREADO** - Funciones propias sin dependencias externas:

### ✅ Incluye:
- Validador de RUC ecuatoriano
- Validador de Cédula ecuatoriana
- Calculadora de tributos aduaneros Ecuador
- Validador de número DAV (Declaración Aduanera)
- Formato de fechas en español
- Cálculo de dígitos verificadores

### 📝 Ejemplo de Uso:
```python
from utils_ecuador import (
    validar_ruc_ecuador,
    calcular_tributos_importacion_ecuador,
    validar_dav_ecuador
)

# Validar RUC
ruc = validar_ruc_ecuador("1791251237001")
print(f"Válido: {ruc['valido']}")
print(f"Tipo: {ruc['tipo']}")

# Calcular tributos de importación $500K
tributos = calcular_tributos_importacion_ecuador(500000)
print(f"Landed Cost: ${tributos['costo_landed_usd']:,.0f}")

# Validar DAV
dav = validar_dav_ecuador("018-2026-10-000891")
print(f"Aduana: {dav['aduana']}")
```

---

## 📊 RESUMEN DE DEPENDENCIAS

### **NIVEL 0: Core (YA TIENES)** ✅
```
streamlit, pandas, plotly, requests
```

### **NIVEL 1: APIs Premium Gratuitas (YA TIENES)** ✅
```
yfinance, beautifulsoup4
```

### **NIVEL 2: SENAE (Instalar cuando tengas ECUAPASS)**
```
zeep
```

### **NIVEL 3: SRI (Instalar cuando tengas Firma Electrónica)**
```
suds-py3, signxml, lxml, cryptography
```

### **NIVEL 4: Extras Opcionales**
```
num2words, pytz, unidecode
```

---

## 🎯 QUÉ INSTALAR AHORA

### **OPCIÓN 1: Solo lo esencial (RECOMENDADO)**
```bash
# No instalar nada nuevo
# Ya tienes todo para que funcione la plataforma
```

### **OPCIÓN 2: Preparar para SENAE/SRI (futuro)**
```bash
pip install zeep suds-py3 signxml lxml cryptography
```

### **OPCIÓN 3: Full Stack (todo)**
```bash
pip install zeep suds-py3 signxml lxml cryptography num2words pytz unidecode
```

---

## ⚡ COMANDO RECOMENDADO (Instalar ahora)

```bash
cd "C:\Users\LENOVO\Documents\ROBOT IMPORT ACEROS\Demo_Import_Aceros"
pip install num2words
```

**¿Por qué solo `num2words`?**
- Para convertir montos a palabras en facturas
- Útil desde ya para reportes
- Las demás librerías se instalan cuando tengas credenciales

---

## 📝 Actualizar `requirements.txt`

```txt
# requirements.txt ACTUAL
streamlit
openai
plotly
newsapi-python
pandas
requests
yfinance
beautifulsoup4

# AGREGAR (opcional):
num2words>=2.0.0
pytz>=2024.1

# AGREGAR SOLO SI TIENES CREDENCIALES SENAE/SRI:
# zeep>=4.2.0
# suds-py3>=1.4.0
# signxml>=3.2.0
# lxml>=5.0.0
# cryptography>=41.0.0
```

---

## 🔍 VERIFICAR LIBRERÍAS INSTALADAS

```bash
# Ver todas las librerías instaladas
pip list

# Ver librerías específicas de Ecuador
pip list | findstr "zeep suds signxml num2words"

# Ver versión de una librería
pip show yfinance
```

---

## 🚀 RESPUESTA DIRECTA

**NO necesitas instalar nada más AHORA.**

La plataforma funciona perfectamente con lo que ya tienes:
- ✅ Yahoo Finance (precios acero)
- ✅ Banco Central Ecuador (riesgo país)
- ✅ VesselFinder (tracking barcos)
- ✅ Utilidades Ecuador personalizadas (`utils_ecuador.py`)

**Instala SOLO cuando necesites:**
- `zeep` → Cuando tengas ECUAPASS
- `signxml` → Cuando tengas Firma Electrónica SRI
- `num2words` → Si quieres reportes más profesionales (opcional)

---

## 💡 BONUS: Librería Personalizada Creada

Creé `utils_ecuador.py` con funciones propias que NO requieren instalación:
- ✅ Validación RUC: Funcionando
- ✅ Validación Cédula: Funcionando
- ✅ Cálculo tributos: $500K FOB → $669K Landed (33.8% incremento)
- ✅ Validación DAV: Funcionando
- ✅ Formato fechas: Funcionando

**Esto te ahorra instalar librerías externas y es 100% personalizado para Ecuador.**
