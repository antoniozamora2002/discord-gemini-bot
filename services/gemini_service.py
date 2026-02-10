import os
from google import genai
from google.genai import types


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("❌ ERROR: La variable GEMINI_API_KEY no está configurada en el archivo .env")

        self.client = genai.Client(api_key=api_key)
        self.text_model_id = "gemini-2.5-pro"
        self.image_model_id = "gemini-2.5-flash-image"

        try:
            with open("prompts/bot_persona.md", "r", encoding="utf-8") as f:
                self.system_instruction = f.read()
        except FileNotFoundError:
            self.system_instruction = "Eres un asistente útil en Discord."

        self.chat_sessions = {}

    async def _get_or_create_chat(self, user_id: int):
        """Crea o recupera un chat."""
        if user_id not in self.chat_sessions:
            chat = self.client.chats.create(
                model=self.text_model_id,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7
                )
            )
            self.chat_sessions[user_id] = chat
        return self.chat_sessions[user_id]

    async def generate_text_response(self, user_prompt: str, user_id: int) -> str:
        try:
            chat = await self._get_or_create_chat(user_id)
            response = chat.send_message(user_prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error generando texto: {e}")
            return "Lo siento, no puedo responder a eso (posible bloqueo de seguridad)."

    async def analyze_image(self, prompt: str, image_bytes: bytes, user_id: int = None,
                            mime_type: str = "image/png") -> str:
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            response = self.client.models.generate_content(
                model=self.text_model_id,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )
            )
            return response.text
        except Exception as e:
            print(f"❌ Error analizando imagen: {e}")
            return "No pude analizar esa imagen o el contenido fue bloqueado."

    async def create_image(self, prompt: str) -> bytes:
        try:
            print(f"📝 Iniciando generación de imagen con prompt: {prompt[:100]}...")

            response = self.client.models.generate_content(
                model=self.image_model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"]
                )
            )

            print(f"✅ Respuesta recibida de Gemini")
            print(f"🔍 Candidates disponibles: {len(response.candidates) if response.candidates else 0}")

            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        data_size = len(part.inline_data.data)
                        print(f"✅ Imagen encontrada! Tamaño: {data_size} bytes")
                        return part.inline_data.data
            return None
        except Exception as e:
            print(f"❌ Error imagen: {e}")
            return None
