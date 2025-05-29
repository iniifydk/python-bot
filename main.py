import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Načtení proměnných z .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
default_prefix = os.getenv("COMMAND_PREFIX")
mongo_url = os.getenv("MONGODB_URI")

# Připojení k MongoDB
cluster = MongoClient(mongo_url)
db = cluster["discord_bot"]
prefixes_collection = db["prefixes"]

# Funkce pro získání prefixu z databáze
def get_prefix(bot, message):
    if not message.guild:
        return default_prefix or "."

    try:
        guild_data = prefixes_collection.find_one({"guild_id": str(message.guild.id)})
        if guild_data and "prefix" in guild_data:
            return guild_data["prefix"]
    except Exception as e:
        print(f"Chyba při získávání prefixu z MongoDB: {e}")

    return default_prefix or "."


# Nastavení botových záměrů a inicializace
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Načítání všech cogs ze složky 'cogs'
async def load_extensions():
    for root, _, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py"):
                relative_path = os.path.join(root, filename)
                module = relative_path.replace(os.sep, ".")[:-3]
                try:
                    await bot.load_extension(module)
                    print(f"✅ Načtený soubor: {module}")
                except Exception as e:
                    print(f"❌ Chyba při načítání {module}: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} je připravený.")
    await load_extensions()

# Spuštění bota
bot.run(token)
