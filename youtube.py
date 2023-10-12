import feedparser, mysql.connector, subprocess, time, shlex, function, sys
from config import db_host, db_database, db_user, db_passwd, youtube_channel_ID

youtube_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id='+youtube_channel_ID

def all_reset():
    response = None
    latest_entry = None
    video_url = None
    video_id = None
    video_title = None
    sql = None
    result = None
    cursor.close()
    conn.close()

while True:
    conn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
    cursor = conn.cursor(dictionary=True)
    response = feedparser.parse(youtube_URL)

    latest_entry = response.entries[0]
    video_url = latest_entry.link
    video_id = video_url.split("v=")[1]
    video_title = latest_entry.title

    sql = "SELECT video_id FROM youtube WHERE id = 1;"
    cursor.execute(sql)
    result = cursor.fetchone()
    if result["video_id"] == str(video_id):
        all_reset()
        try:
            time.sleep(120)
        except KeyboardInterrupt:
            sys.exit()
        continue
    sql = "UPDATE youtube SET video_id = %s, url = %s WHERE id = 1;"
    cursor.execute(sql, (video_id, video_url,))
    conn.commit()
    video_url = shlex.quote(video_url)
    video_title = shlex.quote(video_title)
    subprocess.run(f"python3 ./youtube_send.py {video_title} {video_url}", shell=True)

    all_reset()
    try:
        time.sleep(120)
    except KeyboardInterrupt:
        sys.exit()
