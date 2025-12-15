import os
from google import genai
from google.genai import types


class GeminiService:
    def __init__(self):
        # Cargamos la API Key de las variables de entorno
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ ERROR: La variable GEMINI_API_KEY no está configurada en el archivo .env")

        # Inicializamos el cliente moderno de Google GenAI
        self.client = genai.Client(api_key=api_key)

        # Configuración del modelo de texto/visión (Gemini 2.0 Flash o 1.5 Flash)
        self.text_model_id = "gemini-2.0-flash"

        # Configuración del modelo de generación de imagen (Imagen 3)
        self.image_model_id = "imagen-3.0-generate-002"

        # Cargar instrucciones del sistema (personalidad)
        try:
            with open("prompts/bot_persona.md", "r", encoding="utf-8") as f:
                self.system_instruction = f.read()
        except FileNotFoundError:
            print("⚠️ Advertencia: No se encontró 'prompts/bot_persona.md'. Usando personalidad por defecto.")
            self.system_instruction = "Eres un asistente útil en Discord."

        # Memoria volátil: Diccionario para guardar el historial de chat de cada usuario
        # Clave: user_id (int), Valor: Objeto ChatSession
        self.chat_sessions = {}

    async def _get_or_create_chat(self, user_id: int):
        """
        Recupera una sesión de chat existente para un usuario o crea una nueva si no existe.
        """
        if user_id not in self.chat_sessions:
            # Creamos un nuevo chat con la instrucción del sistema y configuración
            chat = self.client.chats.create(
                model=self.text_model_id,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,  # Creatividad balanceada
                )
            )
            self.chat_sessions[user_id] = chat
        return self.chat_sessions[user_id]

    async def generate_text_response(self, user_prompt: str, user_id: int) -> str:
        """
        Genera una respuesta de texto manteniendo el contexto de la conversación (Chat).
        """
        try:
            chat = await self._get_or_create_chat(user_id)

            # Enviamos el mensaje y esperamos la respuesta (asíncrono si la librería lo soporta,
            # pero google-genai v1 suele ser síncrono wrapper, aquí asumimos llamada directa)
            # Nota: Si usas la versión async de la librería, sería 'await chat.send_message(...)'
            response = chat.send_message(user_prompt)

            return response.text
        except Exception as e:
            print(f"❌ Error generando texto: {e}")
            return "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?"

    async def analyze_image(self, prompt: str, image_bytes: bytes, mime_type: str = "image/png") -> str:
        """
        Analiza una imagen enviada por el usuario (Visión Multimodal).
        """
        try:
            # En la versión moderna, pasamos la imagen como un objeto Part conteniendo bytes
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )

            # Usamos generate_content directamente (sin historial de chat para imágenes por ahora)
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
            return "No pude analizar esa imagen. Asegúrate de que sea un formato válido."

    async def create_image(self, prompt: str) -> bytes:
        """
        Genera una imagen usando Imagen 3 y devuelve los bytes crudos.
        """
        try:
            # Llamada al modelo de generación de imágenes
            response = self.client.models.generate_images(
                model=self.image_model_id,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1",  # Puedes cambiar a "16:9" o "3:4"
                    include_rai_reason=True  # Filtros de seguridad
                )
            )

            # Verificamos si se generó la imagen
            if response.generated_images:
                # Retornamos los bytes de la primera imagen generada
                return response.generated_images[0].image.image_bytes
            else:
                print("⚠️ No se generó imagen (posible bloqueo de seguridad).")
                return None

        except Exception as e:
            print(f"❌ Error creando imagen: {e}")
            return None