import discord
from discord.ext import commands
from discord import app_commands
import io
from services.gemini_service import GeminiService

class ImageCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Reutilizamos el servicio, o podríamos pasarlo como dependencia
        self.gemini = GeminiService()

    @app_commands.command(name="imagina", description="Genera una imagen basada en tu descripción.")
    @app_commands.describe(prompt="Descripción detallada de la imagen que quieres crear")
    async def imagine(self, interaction: discord.Interaction, prompt: str):
        # 1. Deferimos la respuesta porque la IA tarda más de 3 segundos en generar imagen
        await interaction.response.defer(thinking=True)

        try:
            # 2. Llamamos al servicio para crear la imagen
            # La función debe retornar bytes crudos de la imagen
            image_data = await self.gemini.create_image(prompt)

            if not image_data:
                await interaction.followup.send("❌ La política de seguridad bloqueó la imagen o hubo un error.")
                return

            # 3. Convertimos los bytes en un archivo de Discord
            # Usamos io.BytesIO para manejarlo en memoria
            file_obj = io.BytesIO(image_data)
            discord_file = discord.File(fp=file_obj, filename="generated_image.png")

            # 4. Enviamos la imagen
            await interaction.followup.send(content=f"🎨 **Prompt:** {prompt}", file=discord_file)

        except Exception as e:
            print(f"Error generando imagen: {e}")
            await interaction.followup.send(f"Ocurrió un error intentando generar la imagen.")

async def setup(bot):
    await bot.add_cog(ImageCreation(bot))