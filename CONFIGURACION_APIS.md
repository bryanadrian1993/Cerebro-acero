# 🔑 Configuración de APIs - CEREBRO DE ACERO

## APIs Integradas

### 1. ✅ NewsAPI (Noticias Mundiales)

**Propósito:** Obtiene noticias reales sobre crisis geopolíticas, economía, acero, minería, etc.

**Cómo obtener tu API Key:**
1. Visita: https://newsapi.org/
2. Haz clic en "Get API Key"
3. Registra una cuenta gratuita
4. Copia tu API Key

**Plan Gratuito:**
- ✅ 100 requests por día
- ✅ Noticias de los últimos 30 días
- ✅ Suficiente para este proyecto

**Configuración:**
- Abre `app.py`
- Línea 22: Reemplaza `"TU_NEWSAPI_KEY_AQUI"` con tu key real
```python
NEWSAPI_KEY = "tu_key_aqui_ejemplo_abc123xyz"
```

---

### 2. ✅ World Bank API (Datos Económicos)

**Propósito:** Obtiene indicadores económicos globales (precio de commodities, acero, etc.)

**¡NO REQUIERE API KEY!** 
- Es completamente pública y gratuita
- Ya está configurada en el código
- Se activa automáticamente

---

### 3. ⚠️ OpenAI API (Opcional - Deshabilitada)

**Estado:** NO ACTIVA (reemplazada por sistema de reglas)

**Razón:** Tu cuenta excedió la cuota (error 429)

**Si quieres reactivarla:**
1. Agrega créditos a tu cuenta OpenAI
2. La API key ya está configurada en línea 21
3. Descomentar el código de generación de recomendaciones

---

## 🚀 Modo de Operación

### Con NewsAPI configurada:
- ✅ Obtiene noticias reales de Reuters, Bloomberg, CNN, etc.
- ✅ Detecta eventos como: guerras, huelgas, terremotos, booms mineros
- ✅ Genera escenarios basados en eventos reales
- ✅ Muestra fuente de cada noticia

### Sin NewsAPI (Modo Offline):
- ✅ Usa noticias simuladas con probabilidades
- ✅ Todo funciona igual
- ✅ No requiere internet
- ✅ Ideal para demos/desarrollo

---

## 📊 Estado Actual

| API | Estado | Requiere Key | Activa |
|-----|--------|--------------|--------|
| NewsAPI | Configurada | ✅ Sí | ⚠️ Necesitas pegar tu key |
| World Bank | Configurada | ❌ No | ✅ Activa |
| OpenAI | Configurada | ✅ Sí | ❌ Deshabilitada (sin créditos) |

---

## 🔧 Troubleshooting

**Error: "Error obteniendo noticias"**
- Verifica que tu NEWSAPI_KEY sea correcta
- Revisa que no hayas excedido 100 requests/día
- El sistema cambiará a modo simulado automáticamente

**No aparecen noticias reales**
- Verifica conexión a internet
- Confirma que NEWSAPI_KEY esté configurada
- Presiona "🔄 Actualizar Noticias" en el sidebar

**¿Cómo sé si estoy usando noticias reales?**
- En el sidebar verás: "✅ Noticia Real - Fuente: Reuters" (o similar)
- Si dice "📊 Simulado" = está usando noticias offline

---

## 💡 Recomendaciones

1. **Configura NewsAPI primero** - Es gratis y mejora muchísimo la experiencia
2. **No necesitas OpenAI** - El sistema funciona perfecto sin ella
3. **World Bank ya funciona** - No necesitas hacer nada

---

¿Necesitas ayuda? Revisa la documentación de cada API:
- NewsAPI: https://newsapi.org/docs
- World Bank: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
