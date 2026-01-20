from google import genai

# Tu API key
GEMINI_API_KEY = "AIzaSyCygQTij-aojvrYB4xY02feLngZp_kTy70"

# Crear cliente
client = genai.Client(api_key=GEMINI_API_KEY)

# Probar traducción
texto_ingles = "Gold and silver prices hit high after arancel threat"
prompt = f"Translate this text to Spanish (only output the translation, no explanations): {texto_ingles}"

print(f"Texto original: {texto_ingles}")
print("Traduciendo con Gemini...")

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=prompt
)

print(f"Traducción: {response.text.strip()}")
