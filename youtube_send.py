import sys, discord, function, mysql.connector
from config import db_host, db_database, db_user, db_passwd, discord_token_path, discord_key_path, discord_channel_ID

token = function.decrypt_token(discord_token_path, discord_key_path)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

title = sys.argv[1]
url = sys.argv[2]
title = title.replace("'", '')
url = url.replace("'", '')

bot = discord.Client(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    conn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
    cursor = conn.cursor()
    sql = "SELECT user_id FROM users;"
    cursor.execute(sql)
    user_ids = [str(row[0]) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    for channel in bot.get_all_channels():
        if str(channel.id) == discord_channel_ID:
            mentions = [f"<@{user_id}>" for user_id in user_ids]
            mention_message = ", ".join(mentions)
            message_content = f'{mention_message}\n動画タイトル: {title}\n動画URL: {url}'
            await channel.send(message_content)
            await bot.close()
            sys.exit()

bot.run(token)
