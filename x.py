import time, sys, subprocess, shlex
import config, mysql.connector, feedparser
from config import db_host, db_database, db_user, db_passwd
from bs4 import BeautifulSoup

if config.X_disabled:
    sys.exit()

user = ""

def all_reset():
    url = None
    feed = None
    latest_post = None
    post_link = None
    post_content = None
    result = None
    message_content = None
    channel = None
    bot = None
    cmd = None
    cursor.close()
    conn.close()
    sql = None

while True:
    url = f'nitter url/{user}/rss'
    feed = feedparser.parse(url)
    latest_post = feed.entries[0]
    post_link = latest_post.link
    post_content = BeautifulSoup(latest_post.description, 'html.parser')
    post_content = post_content.get_text()
    conn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT contents FROM Twitter WHERE id = 1;"
    cursor.execute(sql)
    result = cursor.fetchone()
    if result['contents'] == post_content:
        try:
            all_reset()
            time.sleep(3600)
            continue
        except KeyboardInterrupt:
            sys.exit()
    post_link = post_link.replace("nitter url", 'twitter.com')
    sql = "UPDATE Twitter SET contents = %s WHERE id = 1;"
    cursor.execute(sql, (post_content,))
    conn.commit()
    post_content = shlex.quote(post_content)
    post_link = shlex.quote(post_link)
    cmd = ['python3', 'x_send.py', post_content, post_link]
    subprocess.Popen(cmd)
    all_reset()
    try:
        time.sleep(3600)
    except KeyboardInterrupt:
        sys.exit()
