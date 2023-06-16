import os
import json
import logging
import secret
from slack_bolt import App, Ack, Say, BoltContext, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from firebase_admin import firestore, credentials
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


app = App()
client = WebClient(token="YOUR_SLACK_API_TOKEN")

""""
# 秘密鍵
cred = credentials.Certificate("JSON/serviceAccountKey.json")
db = firestore.client()
"""

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# グローバル変数の初期化
GLOBAL_DATE=0
GLOBAL_YEAR=0
GLOBAL_MONTH=0
GLOBAL_DAY=0
GLOBAL_HOUR=0
GLOBAL_MINUTE=0
USER_ID = 0
SECRET = 0

# jsonの読み込み
def send_message_from_json(json_file_path, channel_id):
    with open(json_file_path, "r", encoding="UTF-8") as file:
        json_data = json.load(file)
    app.client.chat_postMessage(channel=channel_id, **json_data)


@app.message("登録")
def select_date(message):
    global USER_ID
    USER_ID = message['user']
    send_message_from_json("JSON/check_register.json", USER_ID)

@app.action("yes_register")
def start_register(ack: Ack, body: dict, client: WebClient):
    ack()
    with open("JSON/register_date.json", "r", encoding="UTF-8") as file:
        view= json.load(file)
    client.views_open(trigger_id=body["trigger_id"], view=view)

@app.action("no_register")
def not_register(ack, say):
    ack()
    say("登録したいときは，もう一度「登録」と送ってください")

"""
@app.message("登録")
def abc(ack, body, say, client):
    modal = "JSON/a.json"
    response = client.views_open(
        trigger_id=body["trigger_id"],
        view=modal
    )

    # APIリクエストの結果を確認
    if response["ok"]:
        ack()
    else:
        say(f"モーダルの表示に失敗しました: {response['error']}")
"""

# 選択した日付の抽出
@app.action("select_date")
def handle_register_hour(ack, body, say):
    global GLOBAL_DATE
    GLOBAL_DATE = body["actions"][0]["selected_date"]
    ack()
    global GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY
    GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY = GLOBAL_DATE.split("-")
    
# 選択した時間の抽出
@app.action("select_hour")
def handle_register_hour(ack, body, say):
    global GLOBAL_HOUR
    GLOBAL_HOUR = body["actions"][0]["selected_option"]["value"]
    ack()
    
# 選択した分の抽出
@app.action("select_minute")
def handle_register_minute(ack, body):
    global GLOBAL_MINUTE
    GLOBAL_MINUTE = body["actions"][0]["selected_option"]["value"]
    ack()
    
# 送信ボタンを押したときの処理
@app.view("register_date")
def handle_message_events(ack, say):
    global USER_ID
    ack()
    message = f"あなたが登録したのは、{GLOBAL_YEAR}年{GLOBAL_MONTH}月{GLOBAL_DAY}日{GLOBAL_HOUR}時{GLOBAL_MINUTE}分です"
    say(channel = USER_ID, text=message)
    send_message_from_json("JSON/check_secret.json", USER_ID)

@app.action("yes_secret")
def start_secret(ack: Ack, body: dict, client: WebClient, say):
    ack()
    with open("JSON/register_secret.json", "r", encoding="UTF-8") as file:
        view= json.load(file)
    client.views_open(trigger_id=body["trigger_id"], view=view)

@app.action("input_secret")
def update(body):
    global SECRET
    SECRET = body["actions"][0]["value"]
    
# 秘密の保存(firebase)
@app.view("register_secret")
def save_secret(say, body, ack):
    global SECRET
    ack()
    message = f"登録が完了しました！それでは、期日にお会いしましょう😎"
    say(channel = USER_ID, text=message)
    
    secret.save_to_firestore(SECRET)
    
        
# アプリ起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()