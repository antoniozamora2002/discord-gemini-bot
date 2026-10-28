import discord
from discord.ext import commands
import os
import asyncio
import logging
from dotenv import load_dotenv
from services.gemini_service import GeminiService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RebeccaBot')

# 1. Cargar variables de entorno desde .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Verificación de seguridad
if not TOKEN:
    raise ValueError("⛔ ERROR: No se encontró el DISCORD_TOKEN en el archivo .env")

if not GEMINI_API_KEY:
    raise ValueError("⛔ ERROR: No se encontró la GEMINI_API_KEY en el archivo .env")

# 2. Configurar Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Útil para logs o bienvenidas futuras


# 3. Definir la clase del Bot
class GeminiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",  # Prefijo para comandos antiguos (opcional si usas slash commands)
            intents=intents,
            help_command=None  # Desactivamos la ayuda por defecto para hacer la nuestra propia si queremos
        )
        # Instanciar el servicio global de Gemini
        self.gemini_service = GeminiService(api_key=GEMINI_API_KEY)

    async def setup_hook(self):
        """
        Este metodo se ejecuta UNA vez al iniciar el bot.
        Es el lugar perfecto para cargar los Cogs y sincronizar comandos.
        """
        print("⚙️  Cargando extensiones (Cogs)...")

        # Lista de cogs a cargar
        initial_extensions = [
            'cogs.general',
            'cogs.chat_analysis',
            'cogs.image_creation',
            'cogs.entertainment',
            'cogs.consultas',
            'cogs.voice'  # <-- Agregado aquí
        ]

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
                print(f"  ✅ Extensión cargada: {extension}")
            except Exception as e:
                print(f"  ❌ Error cargando {extension}: {e}")

        # Sincronizar los comandos Slash (/) con Discord
        # Nota: En bots muy grandes esto no se hace aquí, pero para este proyecto está bien.
        print("🔄 Sincronizando árbol de comandos...")
        await self.tree.sync()
        print("✨ ¡Árbol de comandos sincronizado!")

    async def on_ready(self):
        print(f"------------------------------------")
        print(f"🤖 Bot conectado como: {self.user} (ID: {self.user.id})")
        print(f"------------------------------------")
        # Cambiar el estado del bot (Ej: "Jugando a Conversar")
        await self.change_presence(activity=discord.Game(name="con la chala de toño"))


# 4. Instanciar y ejecutar el bot
async def main():
    bot = GeminiBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario.")
