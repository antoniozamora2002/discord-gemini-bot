import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("🔍 Buscando modelos disponibles...")
for model in client.models.list(config={"query_base": True}):
    if "generateContent" in model.supported_actions:
        print(f"✅ Disponible: {model.name}")