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

    timestamp = (datetime_obj - datetime(1970, 1, 1, 9, 0)).total_seconds() - 600 # 10分前

    return int(timestamp)  # 整数値で返す

# メッセージのスケジューリング
def schedule_message(text, channel_id, scheduled_time):
    with open("JSON/scheduled_message.json", "r") as f:
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
    text = "おはようございます！起床予定時刻の１０分前になりました！"

    # 予定時刻の計算（10分前）
    scheduled_time = convert_to_timestamp(2023, 6, 14, 17, 24)# YYYYMMDDHHMM

    schedule_message(text, channel_id, scheduled_time)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
