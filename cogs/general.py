import discord
from discord.ext import commands
from discord import app_commands
import os

OWNER_ID = int(os.getenv("OWNER_ID"))

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Este evento confirma que el Cog se cargó correctamente
        print(f'✅ Cog General cargado.')

    # Comando Slash: /ping
    @app_commands.command(name="ping", description="Verifica la latencia del bot con Discord.")
    async def ping(self, interaction: discord.Interaction):
        # Calculamos la latencia en milisegundos
        latency = round(self.bot.latency * 1000)

        # Respondemos a la interacción
        await interaction.response.send_message(f"🏓 **Pong!** Tardé `{latency}ms` en responder.")

    # Comando Slash: /info
    @app_commands.command(name="info", description="Muestra información sobre este bot.")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Rebecca Info", color=discord.Color.blue())
        embed.add_field(name="Modelo", value="Google Gemini 1.5 Flash", inline=True)
        embed.add_field(name="Capacidades", value="Texto, Visión, Generación de Imagen", inline=True)
        embed.set_footer(text="Desarrollado con discord.py y Google Generative AI")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="secreto")
    async def secreto(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ No eres mi creador.", ephemeral=True)
            return
        await interaction.response.send_message("Hola jefe.")


# Función de configuración obligatoria para cargar el Cog
async def setup(bot):
    await bot.add_cog(General(bot))
