import uuid, requests, json, subprocess, shlex, random, os
import interactions, mysql.connector, psutil, humanize, feedparser, openai
import function, config
from interactions import slash_command, OptionType, slash_option
from config import db_host, db_database, db_user, db_passwd, discord_token_path, discord_key_path, required_role_id
from langdetect import detect
from bs4 import BeautifulSoup

token = function.decrypt_token(discord_token_path, discord_key_path)
bot = interactions.Client(token=token)

subprocess.Popen('python3 status.py', shell=True)

@slash_command(
    name = "mention_add",
    description = "メンションします"
)
async def mention_add(ctx):
    user_id = str(ctx.author.id)
    user_uuid = str(uuid.uuid4())
    if function.check_username_exists(db_host, db_database, db_user, db_passwd, user_id):
        await ctx.send('ユーザーが存在します')
        return
    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
    except mysql.connector.Error as e:
        await ctx.send(f'データベース接続エラー: {e}')
        return
    cursor = conn.cursor()
    sql = "INSERT INTO users (id, user_uuid, user_id) VALUES (NULL, %s, %s);"
    try:
        cursor.execute(sql, (user_uuid, user_id,))
        conn.commit()
        res = '成功しました!'
    except mysql.connector.Error as e:
        conn.rollback()
        await ctx.send(f"内部エラー: {e}")
        res = '失敗しました'
    cursor.close()
    conn.close()
    await ctx.send(f'結果: {res}')

@slash_command(
    name = "mention_delete",
    description = "メンションしなくします"
)
async def mention_delete(ctx):
    user_id = str(ctx.author.id)
    if not function.check_username_exists(db_host, db_database, db_user, db_passwd, user_id):
        await ctx.send('ユーザーが存在しません')
        return
    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
    except mysql.connector.Error as e:
        await ctx.send(f'データベース接続エラー: {e}')
        return
    cursor = conn.cursor()
    sql = "DELETE FROM users WHERE user_id = %s;"
    try:
        cursor.execute(sql, (user_id,))
        conn.commit()
        res = '成功しました!'
    except mysql.connector.Error as e:
        conn.rollback()
        await ctx.send(f"内部エラー: {e}")
        res = '失敗しました'
    cursor.close()
    conn.close()
    await ctx.send(f'結果: {res}')

@slash_command(
    name = "tran",
    description = "翻訳をします",
)
@slash_option(
    name="text",
    description="文章を翻訳",
    opt_type=OptionType.STRING,
    required=True,
)
async def tran(ctx, text: str):
    if not os.path.isfile('text_number.txt'):
        async with open('text_number.txt', 'w') as f:
            await f.write('0')
    file_num = function.read_from_file('text_number.txt')
    text_num = len(text)
    lang_from = detect(text)
    if int(file_num) >= 100000:
        await ctx.send('文字数制限に到達しました')
        return
    key = function.decrypt_token(config.translator_token_path, config.translator_key_path)
    lang_to = 'ja'
    if lang_from == 'ja':
        lang_to = 'en'
    elif lang_from == 'en':
        lang_to = 'ja'
    url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from={lang_from}&to={lang_to}"
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': config.translator_region,
        'Content-type': 'application/json; charset=UTF-8',
    }
    body = [{'text' : str(text)}]
    request = requests.post(url, headers=headers, json=body)
    res = request.json()
    num = int(file_num) + text_num
    await function.write_to_file('text_number.txt', str(num))
    translation_text = res[0]['translations'][0]['text']
    await ctx.send(translation_text)

@slash_command(
    name = "tran_auto",
    description = "自動的に翻訳をします",
)
@slash_option(
    name="setting",
    description="有効, 無効",
    opt_type=OptionType.BOOLEAN,
    required=True,
)
async def tran_auto(ctx, setting: bool):
    #開発中
    if True:
        await ctx.send('この機能は現在、開発中です。')
        return
    if setting and not os.path.isfile('tran.txt'):
        await function.write_to_file('tran.txt', '')
        await ctx.send('設定変更完了')
    elif setting == False and os.path.isfile('tran.txt'):
        os.remove('tran.txt')
        return
    if os.path.isfile('tran.txt'):
        process = subprocess.Popen('python3 auto_tran.py', shell=True)
        return

@slash_command(
    name = "server_status",
    description = "サーバーステータス",
)
async def server_status(ctx):
    has_required_role = any(role.id == int(required_role_id) for role in ctx.author.roles)
    if not has_required_role:
        await ctx.send('必要なロールが付与されていません')
        return
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().used
    memory = humanize.naturalsize(memory, binary=True)
    swp = psutil.swap_memory().used
    swp = humanize.naturalsize(swp, binary=True)
    message = f"CPU: {cpu}\nメモリ: {memory}\nスワップ: {swp}"
    await ctx.send(message)

@slash_command(
    name = "discord_issues",
    description = "ディスコードの問題の確認",
)
async def discord_issues(ctx):
    feed = feedparser.parse('https://discordstatus.com/history.rss')
    latest_issue = feed.entries[0]
    issue_title = latest_issue.title
    issue_contents = BeautifulSoup(latest_issue.summary, 'html.parser')
    issue_summary = issue_contents.get_text()
    await ctx.send(f"タイトル: {issue_title}\n内容: {issue_summary}")

@slash_command(
    name = "gpt",
    description = "Chat-GPTと会話",
)
@slash_option(
    name="text",
    description="Chat-GPTとの会話内容",
    opt_type=OptionType.STRING,
    required=True,
)
async def chat_gpt(ctx, text: str):
    if config.ChatGPT_disabled:
        await ctx.send('この機能は無効化されています')
        return
    openai.api_key = function.decrypt_token(config.ChatGPT_token, config.ChatGPT_key)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": f"{text}"}
        ]
    )
    await ctx.send(response["choices"][0]["message"]["content"])

@slash_command(
    name = "contents_save",
    description = "チャットの会話内容の保存",
)
@slash_option(
    name="permission",
    description="許可または不許可",
    opt_type=OptionType.BOOLEAN,
    required=True,
)
async def contents_save(ctx, permission: bool):
    if False:
        await ctx.send('無効化されています')
        return
    user_id = ctx.author.id
    username = ctx.author.username
    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
    except mysql.connector.Error as e:
        await ctx.send(f'データベース接続エラー: {e}')
        return
    cursor = conn.cursor()
    if permission:
        sql = "DELETE FROM permission WHERE user_id = %s;"
        message = f"{username}の会話内容を保存するように変更されました。"
        cursor.execute(sql, (user_id,))
    else:
        sql = "INSERT INTO permission (id, user_id, username) VALUES (NULL, %s, %s);"
        message = f"{username}の会話内容を保存しないように変更されました。"
        cursor.execute(sql, (user_id, username,))
    conn.commit()
    cursor.close()
    conn.close()
    await ctx.send(message)

bot.start()
