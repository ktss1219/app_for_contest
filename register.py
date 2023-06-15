import os
from slack_bolt import App
import json
import logging
from slack_bolt.adapter.socket_mode import SocketModeHandler
import secret
#sec test
from firebase_admin import firestore
from firebase_admin import credentials

firebase_key_path = os.environ.get('serviceAccountKey.json')
cred = credentials.Certificate(firebase_key_path)# Firebase Admin SDKの秘密鍵へのパス
db = firestore.client()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

#グローバル変数の初期化
GLOBAL_DATE=0
GLOBAL_YEAR=0
GLOBAL_MONTH=0
GLOBAL_DAY=0
GLOBAL_HOUR=0
GLOBAL_MINUTE=0

#sec test
jan = '4901990522731'
p_name = '赤いきつねうどん'
stock = 2
lower = 1
doc_ref = db.collection('user').document(jan)
doc_ref.set({
    'product_name': p_name,
    'stock': stock,
    'lower': lower
})

def send_message_from_json(json_file_path, channel_id):
    with open(json_file_path, "r", encoding="UTF-8") as file:
        json_data = json.load(file)
    app.client.chat_postMessage(channel=channel_id, **json_data)
    
@app.message("登録")
def select_date(say):
    send_message_from_json("JSON/register_date.json","C05A7G0ARB7")
    
#選択した日付の抽出
@app.action("select_date")
def handle_register_hour(ack, body, say):
    global GLOBAL_DATE
    GLOBAL_DATE = body["actions"][0]["selected_date"]
    ack()
    global GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY
    GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY = GLOBAL_DATE.split("-")
    
#選択した時間の抽出
@app.action("select_hour")
def handle_register_hour(ack, body, say):
    global GLOBAL_HOUR
    GLOBAL_HOUR = body["actions"][0]["selected_option"]["value"]
    ack()
    
#選択した分の抽出
@app.action("select_minute")
def handle_register_minute(ack, body, say):
    global GLOBAL_MINUTE
    GLOBAL_MINUTE = body["actions"][0]["selected_option"]["value"]
    ack()
    
#送信ボタンを押したときの処理
@app.action("register_date")
def check_register_date(ack, body, say):
    global GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY, GLOBAL_DAY, GLOBAL_HOUR, GLOBAL_MINUTE
    ack()
    message = f"あなたが登録したのは、{GLOBAL_YEAR}年{GLOBAL_MONTH}月{GLOBAL_DAY}日{GLOBAL_HOUR}時{GLOBAL_MINUTE}分です"
    say(message)
    say(f"続いて秘密の入力に移ります\n内容が「~こと」となるように入力してください")
    
@app.event("message")
def handle_message_events(body, say):
    # ユーザーからのメッセージを取得
    user_message = body["event"]["text"]
    if user_message.endswith("こと"):
       message = f"以下の秘密を登録しました\n{user_message}"
       secret.save_to_firestore(user_message)
       say(message)
    else:
        say(user_message)
        
# アプリ起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()