import discord, sys, requests, uuid
import function, config, mysql.connector
from config import discord_token_path, discord_key_path
from langdetect import detect

token = function.decrypt_token(discord_token_path, discord_key_path)
key = function.decrypt_token(config.translator_token_path, config.translator_key_path)

intents = discord.Intents.default()
intents.presences = False
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    try:
        conn = mysql.connector.connect(host=config.db_host, user=config.db_user, passwd=config.db_passwd, db=config.db_database)
    except mysql.connector.Error:
        await ctx.send(f'データベース接続エラー')
        return
    cursor = conn.cursor()
    sql = "SELECT word_count FROM number WHERE id = 1;"
    cursor.execute(sql)
    result = cursor.fetchone()
    text_message = message.content
    text_message = text_message.replace('@everyone', '@\u200beveryone')
    lang_from = detect(text_message)
    text_num = len(text_message)
    num = text_num + result[0]
    if num >= 100000:
        await message.channel.send('文字数制限に到達しました')
        return

    lang_to = 'ja'
    if lang_from == 'ja':
        lang_to = 'en'
    elif lang_from == 'en':
        lang_to = 'ja'
    url = f'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from={lang_from}&to={lang_to}'
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': config.translator_region,
        'Content-type': 'application/json; charset=UTF-8',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{'text' : str(text_message)}]
    request = requests.post(url, headers=headers, json=body)
    res = request.json()
    translation_text = res[0]['translations'][0]['text']
    sql = "UPDATE number SET word_count = %s WHERE id = 1;"
    cursor.execute(sql, (num,))
    conn.commit()
    cursor.close()
    conn.close()
    await message.channel.send(translation_text)

bot.run(token)
