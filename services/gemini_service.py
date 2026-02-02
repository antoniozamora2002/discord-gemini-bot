import os
from google import genai
from google.genai import types


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.admin_id = os.getenv("ADMIN_ID")

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

    def _get_safety_settings(self, user_id: int):
        """Devuelve la configuración de seguridad basada en si el usuario es Admin."""
        if self.admin_id and str(user_id) == str(self.admin_id):
            threshold = "BLOCK_NONE"
        else:
            threshold = "BLOCK_ONLY_HIGH"

        return [
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold=threshold),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold=threshold),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold=threshold),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold=threshold),
        ]

    async def _get_or_create_chat(self, user_id: int):
        """Crea o recupera un chat con filtros dinámicos según el usuario."""
        if user_id not in self.chat_sessions:
            safety_settings = self._get_safety_settings(user_id)

            chat = self.client.chats.create(
                model=self.text_model_id,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,
                    safety_settings=safety_settings
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

            safety_settings = self._get_safety_settings(user_id) if user_id else None

            response = self.client.models.generate_content(
                model=self.text_model_id,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    safety_settings=safety_settings
                )
            )
            return response.text
        except Exception as e:
            print(f"❌ Error analizando imagen: {e}")
            return "No pude analizar esa imagen o el contenido fue bloqueado."

    async def create_image(self, prompt: str, is_admin: bool = False) -> bytes:
        try:
            safety_threshold = "BLOCK_NONE" if is_admin else "BLOCK_ONLY_HIGH"
            response = self.client.models.generate_content(
                model=self.image_model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    safety_settings=[
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold=safety_threshold),
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold=safety_threshold),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold=safety_threshold)
                    ]
                )
            )
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        return part.inline_data.data
            return None
        except Exception as e:
            print(f"❌ Error imagen: {e}")
            return None
