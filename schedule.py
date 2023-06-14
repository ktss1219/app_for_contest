import os
import json
import firebase_admin
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timedelta

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 予定時刻（10分前）のUnixTime変換
def convert_to_timestamp(year, month, day, hour, minute):
    # 入力を日時オブジェクトに変換
    datetime_obj = datetime(year, month, day, hour, minute)

    timestamp = (datetime_obj - datetime(1970, 1, 1, 9, 0)).total_seconds()

    return int(timestamp) # 整数値で返す

# 起床メッセージのスケジューリング
def wu_schedule_message(text, channel_id, scheduled_time):
    with open("JSON/wakeup_scheduled_message.json", "r") as f:
        message_payload = json.load(f)

    app.client.chat_scheduleMessage(
        text = text,
        channel = channel_id,
        post_at = scheduled_time, 
        blocks = message_payload["blocks"]
    )

# 寝坊メッセージのスケジューリング
def os_schedule_message(text, channel_id, scheduled_time):
    with open("JSON/overslept_scheduled_message.json", "r") as f:
        message_payload = json.load(f)

    app.client.chat_scheduleMessage(
        text = text,
        channel = channel_id,
        post_at = scheduled_time,
        blocks = message_payload["blocks"]
    )

# ここは後々@app.actionに変更
@app.message("test")
def send_scheduled_message():
    # チャンネルID
    channel_id = "C05A7G0ARB7"
    
    # 起床確認
    text = "起床予定時刻の１０分前になりました！起きていますか？"

    # 予定時刻の計算（10分前）
    scheduled_time = convert_to_timestamp(2023, 6, 14, 20, 41) - 60# YYYYMMDDHHMM

    wu_schedule_message(text, channel_id, scheduled_time)
    
"""@app.action("wakeup")
def wakeup_confirm(ack, body, say):
    ack()
    say("起床が確認出来ました！おはようございます☀️")"""
    
@app.action("wakeup")
def unwakeup():
     # チャンネルID
    channel_id = "C05A7G0ARB7"
    
    # 起床確認
    text = ""

    # 予定時刻の計算（10分前）
    scheduled_time = convert_to_timestamp(2023, 6, 14, 20, 41) # YYYYMMDDHHMM

    os_schedule_message(text, channel_id, scheduled_time)
    

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
