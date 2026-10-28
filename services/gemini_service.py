import base64
import io
import os
import wave
from google import genai
from google.genai import types


class GeminiService:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("❌ ERROR: La variable GEMINI_API_KEY no está configurada en el archivo .env")

        self.client = genai.Client(api_key=api_key)
        self.text_model_id = "gemini-3.8-flash"
        self.image_model_id = "gemini-3.1-flash-image"

        try:
            with open("prompts/bot_persona.md", "r", encoding="utf-8") as f:
                self.system_instruction = f.read()
        except FileNotFoundError:
            self.system_instruction = "Eres un asistente útil en Discord."

        self.chat_sessions = {}

    async def create_custom_voice(self, voice_description: str) -> str:
            """
            Crea una voz personalizada a partir de un texto (Voice Design) 
            y devuelve el ID de voz (voice_id) generado.
            """
            # Creación mediante endpoint de Voice Design
            voice = self.client.voices.create(
                voice={
                    "type": "prompted",
                    "prompted": {
                        "input": voice_description  # Ejemplo: "Chico peruano joven, entusiasta, tono claro y amigable"
                    }
                },
                store=True  # Obligatorio para voces "prompted"; Google guarda la voz y devuelve su ID
            )
            return voice.id  # ID guardado (ej. 'voice_abc123def456')
    
    async def generate_speech(self, text: str, voice: str = "Puck",
                             style: str = "friendly, conversational") -> io.BytesIO:
        """
        Genera el audio en base al texto, voz (ID personalizado o predeterminado) 
        y estilo (actuación / matiz).
        """
        interaction = self.client.interactions.create(
            model="gemini-3.8-flash-tts",
            input=[{
                "type": "user_input",
                "content": [{
                    "type": "text",
                    "text": text,
                    "annotations": [{
                        "type": "speech_metadata",
                        "style": style
                    }]
                }]
            }],
            response_format={"type": "audio"},
            generation_config={
                "speech_config": [
                    {"voice": voice}  # Puede ser "Puck" o el voice_id de Voice Design
                ]
            }
        )

        output_audio = interaction.output_audio
        if output_audio is None or not output_audio.data:
            raise RuntimeError("El modelo no devolvió audio.")

        # Decodificar el audio en base64 entregado por el modelo
        raw_audio_bytes = base64.b64decode(output_audio.data)
        audio_buffer = io.BytesIO()

        # El TTS suele entregar PCM crudo (audio/l16) sin cabecera; se envuelve en WAV
        # para que FFmpeg pueda detectar el formato al reproducirlo.
        mime_type = (output_audio.mime_type or "").lower()
        if mime_type.startswith("audio/l16") or mime_type.startswith("audio/pcm"):
            with wave.open(audio_buffer, "wb") as wav_file:
                wav_file.setnchannels(output_audio.channels or 1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(output_audio.sample_rate or 24000)
                wav_file.writeframes(raw_audio_bytes)
        else:
            audio_buffer.write(raw_audio_bytes)

        audio_buffer.seek(0)
        return audio_buffer

    async def _get_or_create_chat(self, user_id: int):
        """Crea o recupera un chat."""
        if user_id not in self.chat_sessions:
            chat = self.client.chats.create(
                model=self.text_model_id,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,
                    tools=[{"google_search": {}}]
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
