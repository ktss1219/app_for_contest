import os
import json
import logging
import secret
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from firebase_admin import firestore, credentials

# 秘密鍵
cred = credentials.Certificate("JSON/serviceAccountKey.json")
db = firestore.client()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# グローバル変数の初期化
GLOBAL_DATE=0
GLOBAL_YEAR=0
GLOBAL_MONTH=0
GLOBAL_DAY=0
GLOBAL_HOUR=0
GLOBAL_MINUTE=0
USER_ID = 0

# jsonの読み込み
def send_message_from_json(json_file_path, channel_id):
    with open(json_file_path, "r", encoding="UTF-8") as file:
        json_data = json.load(file)
    app.client.chat_postMessage(channel=channel_id, **json_data)

@app.message("登録")
def select_date(message):
    global USER_ID
    USER_ID = message['user']
    send_message_from_json("JSON/register_date.json", USER_ID)
    
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
@app.action("register_date")
def handle_message_events(ack):
    global USER_ID
    
    ack()
    
    with open("JSON/secret_input.json", "r") as f:
        message_payload = json.load(f)
    
    app.client.chat_postMessage(
        channel = USER_ID, 
        blocks = message_payload["blocks"]
    )
    
# 秘密の保存(firebase)
@app.action("input_action")
def save_secret(say, body, ack):
    say("登録が完了しました！それでは、期日にお会いしましょう😎")
    
    ack()
    
    secret_ = body["actions"][0]["value"]
    
    secret.save_to_firestore(secret_)
    
    """
    # ユーザーからのメッセージを取得
    user_message = body["event"]["text"]
    if user_message.endswith("こと"):
        message = f"以下の秘密を登録しました\n{user_message}"
        secret.save_to_firestore(user_message)
        say(message)
    else:
        say(user_message)
    """
        
"""
@app.event("message")
def touroku():
    #sec test
    jan = 'iuGlUc0tXNWWLIKazTgt'
    p_name = '赤いきつねうどん'
    stock = 2
    lower = 1
    doc_ref = db.collection('user').document(jan)
    doc_ref.set({
        'product_name': p_name,
        'stock': stock,
        'lower': lower
    })
"""
        
# アプリ起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()