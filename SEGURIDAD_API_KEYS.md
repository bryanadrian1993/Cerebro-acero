# 🔐 SEGURIDAD DE API KEYS

## ⚠️ IMPORTANTE

**NUNCA subas API keys directamente al código en GitHub**

## ✅ Configuración SEGURA

### Para Desarrollo Local:
1. Tus claves están en `.streamlit/secrets.toml`
2. Este archivo está en `.gitignore` → **NO se sube a GitHub**
3. Solo existe en tu computadora

### Para Streamlit Cloud:
1. Ve a tu app en Streamlit Cloud
2. Click en ⚙️ Settings → Secrets
3. Agrega tus claves allí (formato TOML):
```toml
NEWSAPI_KEY = "tu-clave-aqui"
OPENAI_API_KEY = "tu-clave-aqui"
```

## 🛡️ Verificación de Seguridad

Antes de hacer `git push`, verifica:
```bash
git status
```

**NUNCA debe aparecer:**
- `.streamlit/secrets.toml`

Si aparece, bórralo de git:
```bash
git rm --cached .streamlit/secrets.toml
```

## 📋 Claves que necesitas:

1. **NewsAPI** (Gratis): https://newsapi.org/
   - 100 requests/día gratis
   
2. **OpenAI** (Opcional - de pago): https://platform.openai.com/
   - Solo si quieres análisis con IA

## ✅ Tu código actual está protegido

- ✅ `.gitignore` configurado
- ✅ Claves en archivo local seguro
- ✅ Código sin claves hardcodeadas
