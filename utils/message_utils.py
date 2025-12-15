def split_message(text: str, limit: int = 1900) -> list[str]:
    """
    Divide un texto largo en fragmentos más pequeños para cumplir con el límite de Discord (2000 chars).
    Usamos 1900 como límite por seguridad (para dejar espacio a negritas, emojis, etc).
    """
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = ""

    # Dividimos por líneas para intentar respetar la estructura del texto
    lines = text.split('\n')

    for line in lines:
        # +1 es por el salto de línea que perdimos al hacer split
        if len(current_chunk) + len(line) + 1 > limit:
            # Si la línea actual hace que nos pasemos del límite, 
            # guardamos el chunk actual y empezamos uno nuevo
            chunks.append(current_chunk)
            current_chunk = line + "\n"
        else:
            # Si cabe, la añadimos al chunk actual
            current_chunk += line + "\n"

    # Añadimos el último trozo sobrante
    if current_chunk:
        chunks.append(current_chunk)

    return chunks