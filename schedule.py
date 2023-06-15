import os
import json
import firebase_admin
import time
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timedelta

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

TIMEOUT = 60
flag = False

# 予定時刻（10分前）のUnixTime変換
def convert_to_timestamp(year, month, day, hour, minute):
    # 入力を日時オブジェクトに変換
    datetime_obj = datetime(year, month, day, hour, minute)

    timestamp = (datetime_obj - datetime(1970, 1, 1, 9, 0)).total_seconds()

    return int(timestamp) # 整数値で返す

# メッセージのスケジューリング
def schedule_message(jsf, text, channel_id, scheduled_time):
    with open(jsf, "r") as f:
        message_payload = json.load(f)

    app.client.chat_scheduleMessage(
        text = text,
        channel = channel_id,
        post_at = scheduled_time, 
        blocks = message_payload["blocks"]
    )

# 後に@app.actionに変更
@app.message("test")
def send_scheduled_message(message):
    # 秘密
    secret = "大学に入ってからおもらしをしたことがある"
    
    # ユーザ情報を取得
    id = message['user']
    response = client.users_info(user=id)
    user = response['user']
    username = user['name']  
      
    # チャンネルID
    channel_id = "C05A7G0ARB7"
    
    # 起床確認
    text = "起床予定時刻の１０分前になりました！起きていますか？"

    # 予定時刻の計算
    scheduled_time = convert_to_timestamp(2023, 6, 16, 0, 1)- 60 # 設定の10分前
    
    # jsonファイルの読込
    jst = "JSON/wakeup_scheduled_message.json"

    schedule_message(jst, text, channel_id, scheduled_time)
    
    # タイムアウト時間まで待機
    time.sleep(TIMEOUT)
    
    if not flag:
    # タイムアウト時の処理
        app.client.chat_postMessage(
            channel = "C05A7G0ARB7",
            blocks =  [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": f"残念ながら、<@{username}>さんは寝坊してしまったようです…",
			}
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": f"たいっっっっっっっっへん心苦しいですが、<@{username}>さんの秘密を暴露したいと思います😄",
			}
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": f"なんと、<@{username}>さんは\n{secret}\nそうです！",
			}
		}
	]
        )
@app.action("wakeup")
def wakeup_confirm(ack, say):
    global flag
    flag = True
    ack()
    say("起床が確認出来ました！おはようございます☀️")
    
"""   
@app.action("default")
def unwakeup():
     # チャンネルID
    channel_id = "C05A7G0ARB7"
    
    # 起床確認
    text = ""

    # 予定時刻の計算
    scheduled_time = convert_to_timestamp(2023, 6, 15, 0, 19) # YYYYMMDDHHMM
    
    # jsonファイルの読込
    jst = "JSON/overslept_scheduled_message.json"
    
    schedule_message(jst, text, channel_id, scheduled_time)
"""


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
