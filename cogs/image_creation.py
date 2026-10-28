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
        await interaction.response.defer(thinking=True)

        try:
            # Llamamos al servicio
            image_data = await self.gemini.create_image(prompt)

            if image_data:
                file = discord.File(io.BytesIO(image_data), filename="imagen_generada.png")
                embed = discord.Embed(
                    title="🎨 Imagen Generada",
                    description=f"**Prompt:** {prompt}",
                    color=discord.Color.random()
                )
                embed.set_image(url="attachment://imagen_generada.png")
                embed.set_footer(text=f"Generado por {interaction.user.display_name} • Modelo: Gemini 3.1 Flash")
                await interaction.followup.send(embed=embed, file=file)
            else:
                # Caso donde image_data es None o vacío
                error_embed = discord.Embed(
                    title="❌ Error al Generar Imagen",
                    description="No se pudo generar la imagen. Por favor, intenta de nuevo más tarde.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)

        except Exception as e:
            print(f"❌ Error en comando /imagina: {e}")
            error_embed = discord.Embed(
                title="❌ Error al Generar Imagen",
                description="Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ImageCreation(bot))
