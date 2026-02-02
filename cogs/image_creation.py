import discord
from discord.ext import commands
from discord import app_commands
import io
from services.gemini_service import GeminiService
import os


class ImageCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Reutilizamos el servicio, o podríamos pasarlo como dependencia
        self.gemini = GeminiService()

    @app_commands.command(name="imagina", description="Genera una imagen basada en tu descripción.")
    @app_commands.describe(prompt="Descripción detallada de la imagen que quieres crear")
    async def imagine(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(thinking=True)

        # 1. Obtenemos el ID del admin desde las variables de entorno
        admin_id_env = os.getenv("ADMIN_ID")

        # 2. Verificamos si el usuario actual es el admin
        # Convertimos a int porque las variables de entorno son strings
        is_admin = False
        if admin_id_env and str(interaction.user.id) == admin_id_env:
            is_admin = True

        # 3. Llamamos al servicio pasando el estado de admin
        image_data = await self.bot.gemini.create_image(prompt, is_admin=is_admin)

        if image_data:
            # (El resto del código de envío de imagen sigue igual...)
            file = discord.File(io.BytesIO(image_data), filename="imagen_generada.png")
            embed = discord.Embed(
                title="🎨 Imagen Generada",
                description=f"**Prompt:** {prompt}",
                color=discord.Color.random()
            )
            embed.set_image(url="attachment://imagen_generada.png")
            embed.set_footer(text=f"Generado por {interaction.user.display_name} • Modelo: Gemini 2.5 Flash")

            await interaction.followup.send(embed=embed, file=file)
        else:
            await interaction.followup.send(
                "❌ No se pudo generar la imagen. Puede que el prompt sea demasiado explícito incluso para mis filtros relajados.",
                ephemeral=True)


async def setup(bot):
    await bot.add_cog(ImageCreation(bot))
