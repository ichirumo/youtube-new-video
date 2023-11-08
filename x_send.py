import sys, discord, function
from config import discord_token_path, discord_key_path, discord_channel_ID

token = function.decrypt_token(discord_token_path, discord_key_path)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

contents = sys.argv[1].replace("'", '')
url = sys.argv[2].replace("'", '')

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    for channel in bot.get_all_channels():
        if str(channel.id) == discord_channel_ID:
            message_content = f'ツイート内容: {contents}\nツイートURL: {url}'
            await channel.send(message_content)
            await bot.close()
            sys.exit()

bot.run(token)
