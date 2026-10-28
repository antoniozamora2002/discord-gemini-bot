import discord
from discord.ext import commands
import asyncio
from services.gemini_service import GeminiService


class VoiceCog(commands.Cog):
    def __init__(self, bot, gemini_service: GeminiService):
        self.bot = bot
        self.gemini_service = gemini_service
        self.custom_voices = {}  # guild_id -> voice_id creado con !crear_voz

    @commands.command(name="join")
    async def join_voice(self, ctx: commands.Context):
        """Conecta al bot al canal de voz donde se encuentre el usuario."""
        if not ctx.author.voice:
            await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f"🔊 Me he conectado a **{channel.name}**.")

    @commands.command(name="leave")
    async def leave_voice(self, ctx: commands.Context):
        """Desconecta al bot del canal de voz."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Me he desconectado del canal de voz.")
        else:
            await ctx.send("❌ No estoy en ningún canal de voz.")

    @commands.command(name="crear_voz")
    async def create_voice(self, ctx: commands.Context, *, descripcion: str):
        """
        Diseña una voz desde cero enviando una descripción en lenguaje natural.
        Ejemplo: !crear_voz Un locutor de radio peruano, voz grave, muy alegre y dinámica.
        """
        async with ctx.typing():
            try:
                voice_id = await self.gemini_service.create_custom_voice(descripcion)
                self.custom_voices[ctx.guild.id] = voice_id
                await ctx.send(f"🎙️ **¡Voz creada y configurada para este servidor!**\nID: `{voice_id}`")
            except Exception as e:
                await ctx.send(f"❌ Error al diseñar la voz: `{e}`")
    
    @commands.command(name="habla", aliases=["say", "tts"])
    async def speak_text(self, ctx: commands.Context, *, texto: str):
        """Sintetiza un texto enviado por un usuario sin micrófono y lo reproduce en el canal de voz."""
        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("❌ No estoy en un canal de voz. Usa `!join` o conéctate a uno.")
                return

        vc: discord.VoiceClient = ctx.voice_client

        if vc.is_playing():
            await ctx.send("⏳ Espera a que termine de hablar la reproducción actual.")
            return

        async with ctx.typing():
            try:
                # 1. Obtener audio generado desde Gemini TTS
                # Usa la voz personalizada del servidor si existe; si no, la voz por defecto
                voice = self.custom_voices.get(ctx.guild.id, "Puck")
                audio_buffer = await self.gemini_service.generate_speech(texto, voice=voice)

                # 2. Reproducir en el canal de voz usando FFmpeg
                source = discord.FFmpegPCMAudio(audio_buffer, pipe=True)
                vc.play(source)

                await ctx.message.add_reaction("🔊")
            except Exception as e:
                await ctx.send(f"⚠️ Ocurrió un error al generar la voz: `{e}`")


async def setup(bot):
    await bot.add_cog(VoiceCog(bot, bot.gemini_service))
