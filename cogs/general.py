import discord
from discord.ext import commands
from discord import app_commands


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
        embed = discord.Embed(title="🤖 GemiBot Info", color=discord.Color.blue())
        embed.add_field(name="Modelo", value="Google Gemini 1.5 Flash", inline=True)
        embed.add_field(name="Capacidades", value="Texto, Visión, Generación de Imagen", inline=True)
        embed.set_footer(text="Desarrollado con discord.py y Google Generative AI")
        await interaction.response.send_message(embed=embed)


# Función de configuración obligatoria para cargar el Cog
async def setup(bot):
    await bot.add_cog(General(bot))