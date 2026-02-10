
# 🤖 Rebecca - Discord Gemini Bot

**Rebecca** es un bot de Discord avanzado y con personalidad, desarrollado en Python utilizando la librería `discord.py` e integrado con la API de **Google Gemini** (Generative AI). No solo responde a mensajes de texto, sino que también puede analizar imágenes, generar arte visual y consultar bases de datos de entretenimiento.

## ✨ Características principales

* **Inteligencia Artificial (Gemini 2.5):** Respuestas de texto fluidas y con memoria de conversación por usuario.
* **Visión Artificial:** Capacidad para "ver" y describir imágenes enviadas por los usuarios (formatos PNG, JPG, WEBP).
* **Generación de Imágenes:** Crea arte visual a partir de descripciones textuales mediante el comando `/imagina`.
* **Personalidad Única:** Rebecca es amable, directa y un poco sarcástica, siguiendo una identidad definida en Markdown.
* **Módulo de Entretenimiento:**
* `🔍 /anime`: Busca información detallada en MyAnimeList a través de la API de Jikan.
* `⚡ /pokedex`: Consulta datos de Pokémon usando PokéAPI.


* **Gestión de Seguridad Dinámica:** Los filtros de contenido de la IA se ajustan automáticamente si el usuario es el administrador configurado.

## 🛠️ Requisitos

El proyecto utiliza las siguientes librerías principales:

* `discord.py` (Para la conexión con Discord).
* `google-genai` (Para interactuar con los modelos de Google).
* `python-dotenv` (Para la gestión de variables de entorno).
* `aiohttp` (Para peticiones a APIs externas).

## 🚀 Instalación y Configuración

1. **Clonar el repositorio:**
```bash
git clone <url-del-repositorio>
cd discord-gemini-bot

```


2. **Crear un entorno virtual e instalar dependencias:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

```


3. **Configurar variables de entorno:**
Crea un archivo `.env` en la raíz del proyecto con los siguientes datos:
```env
DISCORD_TOKEN=tu_token_de_discord
GEMINI_API_KEY=tu_api_key_de_google
OWNER_ID=tu_id_de_usuario_discord
ADMIN_ID=tu_id_de_usuario_discord

```


4. **Ejecutar el bot:**
```bash
python main.py

```



## 📂 Estructura del Proyecto

* `main.py`: Punto de entrada que carga los Cogs y sincroniza los comandos Slash.
* `cogs/`: Contiene los módulos de comandos (General, Chat, Imágenes, Entretenimiento).
* `services/gemini_service.py`: Lógica central para la comunicación con los modelos de IA de Google.
* `prompts/bot_persona.md`: Define la identidad y reglas de comportamiento de Rebecca.
* `utils/`: Funciones de apoyo para manejo de mensajes largos y descarga de imágenes.

## 🎮 Comandos Disponibles

| Comando | Descripción |
| --- | --- |
| `/ping` | Verifica la latencia del bot. |
| `/info` | Muestra información técnica del bot. |
| `/imagina [prompt]` | Genera una imagen mediante IA. |
| `/anime [nombre]` | Busca un anime en MyAnimeList. |
| `/pokedex [pokemon]` | Busca datos de un Pokémon. |
| `Mención o DM` | Inicia una conversación o análisis de imagen con Rebecca. |

---

*Desarrollado por Antonio Zamora*