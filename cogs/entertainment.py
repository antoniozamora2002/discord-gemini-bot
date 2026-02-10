import discord
from discord.ext import commands
from discord import app_commands
import aiohttp


class Entertainment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- COMANDO DE ANIME (Jikan API) ---
    @app_commands.command(name="anime", description="Busca información de un anime en MyAnimeList")
    @app_commands.describe(nombre="El nombre del anime a buscar")
    async def anime(self, interaction: discord.Interaction, nombre: str):
        await interaction.response.defer()  # Damos tiempo a la API para responder

        url = f"https://api.jikan.moe/v4/anime?q={nombre}&limit=1"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('data', [])

                    if results:
                        anime = results[0]  # Tomamos el primer resultado

                        # Creamos un Embed bonito estilo Rebecca
                        embed = discord.Embed(
                            title=f"📺 {anime.get('title')}",
                            url=anime.get('url'),
                            description=anime.get('synopsis', 'Sin descripción.')[:400] + "...",
                            color=discord.Color.dark_purple()
                        )
                        embed.set_thumbnail(url=anime['images']['jpg']['image_url'])
                        embed.add_field(name="Episodios", value=str(anime.get('episodes', '?')), inline=True)
                        embed.add_field(name="Puntuación", value=f"⭐ {anime.get('score', 'N/A')}", inline=True)
                        embed.set_footer(text="Datos provistos por Jikan (MyAnimeList)")

                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send(f"❌ No encontré ningún anime llamado '{nombre}'.")
                else:
                    await interaction.followup.send("⚠️ Hubo un error al conectar con la API de anime.")

    # --- COMANDO DE POKEMON (PokéAPI) ---
    @app_commands.command(name="pokedex", description="Busca datos de un Pokémon")
    @app_commands.describe(pokemon="El nombre del Pokémon a buscar")
    async def pokedex(self, interaction: discord.Interaction, pokemon: str):
        await interaction.response.defer()

        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    # Creamos un Embed con la info del Pokémon
                    embed = discord.Embed(
                        title=f"⚡ {data['name'].capitalize()}",
                        description=f"ID: {data['id']}\nAltura: {data['height']} dm\nPeso: {data['weight']} hg",
                        color=discord.Color.green()
                    )
                    embed.set_thumbnail(url=data['sprites']['front_default'])
                    embed.add_field(name="Tipos", value=", ".join([t['type']['name'] for t in data['types']]), inline=True)
                    embed.set_footer(text="Datos provistos por PokéAPI")

                    await interaction.followup.send(embed=embed)
                elif response.status == 404:
                    await interaction.followup.send(f"❌ No encontré ningún Pokémon llamado '{pokemon}'.")
                else:
                    await interaction.followup.send("⚠️ Hubo un error al conectar con la API de Pokémon.")

async def setup(bot):
    await bot.add_cog(Entertainment(bot))