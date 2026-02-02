import discord
from discord.ext import commands
from services.gemini_service import GeminiService
from utils.image_utils import download_image_to_bytes
from utils.message_utils import split_message


class ChatAnalysis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Instanciamos el servicio de Gemini una sola vez al cargar el Cog
        self.gemini = GeminiService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. Ignorar mensajes del propio bot para evitar bucles infinitos
        if message.author.bot:
            return

        # 2. Verificar si el bot fue mencionado o si es un Mensaje Directo (DM)
        is_mentioned = self.bot.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)

        # Solo respondemos si nos mencionan o es un DM (puedes cambiar esta lógica)
        if is_mentioned or is_dm:

            # Indicamos que el bot está "Escribiendo..." o "Pensando..."
            async with message.channel.typing():
                try:
                    # Limpiamos el mensaje (quitamos la mención @Bot)
                    clean_text = message.content.replace(f'<@{self.bot.user.id}>', '').strip()

                    response_text = ""

                    # --- CASO A: El usuario envió una IMAGEN (Visión) ---
                    if message.attachments:
                        # Tomamos la primera imagen
                        attachment = message.attachments[0]

                        # Verificamos que sea una imagen
                        if any(ext in attachment.filename.lower() for ext in ['png', 'jpg', 'jpeg', 'webp']):
                            # Descargamos la imagen a memoria (bytes) usando nuestra utilidad
                            image_bytes = await download_image_to_bytes(attachment.url)

                            # Llamamos a Gemini en modo Visión
                            response_text = await self.gemini.analyze_image(
                                prompt=clean_text or "Describe esta imagen.",
                                image_bytes=image_bytes,
                                user_id=message.author.id
                            )
                        else:
                            response_text = "⚠️ Solo puedo analizar imágenes (PNG, JPG, WEBP)."

                    # --- CASO B: El usuario solo envió TEXTO (Chat) ---
                    else:
                        if not clean_text:
                            # Si solo lo mencionan sin texto
                            await message.reply("Hola 👋 ¿En qué puedo ayudarte hoy?")
                            return

                        # Llamamos a Gemini en modo Chat de Texto
                        # Pasamos el ID del autor para gestionar historiales separados por usuario (opcional)
                        response_text = await self.gemini.generate_text_response(clean_text, user_id=message.author.id)

                    # --- ENVIAR RESPUESTA ---
                    # Usamos nuestra utilidad para dividir mensajes si son muy largos (>2000 chars)
                    chunks = split_message(response_text)
                    for chunk in chunks:
                        await message.reply(chunk)

                except Exception as e:
                    print(f"Error en chat_analysis: {e}")
                    await message.reply("😵‍💫 Tuve un problema procesando eso. Intenta de nuevo.")


async def setup(bot):
    await bot.add_cog(ChatAnalysis(bot))