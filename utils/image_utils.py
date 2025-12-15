import aiohttp
import io

async def download_image_to_bytes(url: str) -> bytes:
    """
    Descarga una imagen desde una URL (Discord attachment) y la devuelve como bytes.
    Retorna None si falla la descarga.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Leemos el contenido binario de la respuesta
                    data = await response.read()
                    return data
                else:
                    print(f"⚠️ Error descargando imagen. Status: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Error crítico en download_image_to_bytes: {e}")
        return None