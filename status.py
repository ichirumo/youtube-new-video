import discord
import function, config
from config import discord_token_path, discord_key_path

token = function.decrypt_token(discord_token_path, discord_key_path)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=config.status))

bot.run(token)
