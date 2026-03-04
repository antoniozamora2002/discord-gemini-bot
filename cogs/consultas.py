import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os


class Consultas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Si Decolecta requiere un token, lo ideal es guardarlo en el archivo .env
        self.api_token = os.getenv("DECOLECTA_TOKEN", "")

    @app_commands.command(name="dni", description="Consulta los datos de un DNI en RENIEC")
    @app_commands.describe(numero="El número de DNI de 8 dígitos")
    async def dni(self, interaction: discord.Interaction, numero: str):
        if len(numero) != 8 or not numero.isdigit():
            await interaction.response.send_message("❌ El DNI debe tener exactamente 8 números.", ephemeral=True)
            return

        # Deferimos la respuesta para darle tiempo a la API
        await interaction.response.defer()

        url = f"https://api.decolecta.com/v1/reniec/dni?numero={numero}"
        headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = discord.Embed(
                        title=f"👤 Consulta DNI: {numero}",
                        color=discord.Color.red()
                    )

                    # Obtenemos el nombre completo usando la llave correcta de la API
                    nombre_completo = data.get('full_name', 'Desconocido')

                    embed.add_field(name="Nombre Completo", value=nombre_completo, inline=False)
                    embed.set_footer(text="Datos provistos por Decolecta")

                    await interaction.followup.send(embed=embed)
                elif response.status == 404:
                    await interaction.followup.send(f"❌ No se encontró información para el DNI '{numero}'.")
                else:
                    await interaction.followup.send("⚠️ Hubo un error al conectar con la API de Decolecta.")

    @app_commands.command(name="ruc", description="Consulta los datos de un RUC en SUNAT")
    @app_commands.describe(numero="El número de RUC de 11 dígitos")
    async def ruc(self, interaction: discord.Interaction, numero: str):
        if len(numero) != 11 or not numero.isdigit():
            await interaction.response.send_message("❌ El RUC debe tener exactamente 11 números.", ephemeral=True)
            return

        await interaction.response.defer()

        url = f"https://api.decolecta.com/v1/sunat/ruc?numero={numero}"
        headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = discord.Embed(
                        title=f"🏢 Consulta RUC: {numero}",
                        color=discord.Color.blue()
                    )

                    # Actualizado con 'razon_social'
                    embed.add_field(name="Razón Social", value=data.get('razon_social', 'Desconocido'), inline=False)
                    embed.add_field(name="Estado", value=data.get('estado', 'Desconocido'), inline=True)
                    embed.add_field(name="Condición", value=data.get('condicion', 'Desconocido'), inline=True)

                    # Agregando el campo de dirección para aprovechar la información extra
                    direccion = data.get('direccion', '')
                    if direccion:
                        embed.add_field(name="Dirección", value=direccion, inline=False)

                    embed.set_footer(text="Datos provistos por Decolecta")

                    await interaction.followup.send(embed=embed)
                elif response.status == 404:
                    await interaction.followup.send(f"❌ No se encontró información para el RUC '{numero}'.")
                else:
                    await interaction.followup.send("⚠️ Hubo un error al conectar con la API de Decolecta.")


async def setup(bot):
    await bot.add_cog(Consultas(bot))
