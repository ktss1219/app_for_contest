import os
import json
import firebase_admin
import time
from slack_sdk import WebClient
from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from firebase_admin import firestore, credentials
from datetime import datetime

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# 秘密鍵
cred = credentials.Certificate("JSON/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# グローバル変数の初期化
GLOBAL_DATE=0
GLOBAL_YEAR=0
GLOBAL_MONTH=0
GLOBAL_MONTH_RE = 0
GLOBAL_DAY=0
GLOBAL_DAY_RE = 0
GLOBAL_HOUR=0
GLOBAL_MINUTE=0
USER_ID = 0
SECRET = 0

# 起床or寝坊のフラグ
flag = False

# jsonの読み込み
def send_message_from_json(json_file_path, channel_id):
    with open(json_file_path, "r", encoding="UTF-8") as file:
        json_data = json.load(file)
    app.client.chat_postMessage(channel=channel_id, **json_data)

# ユーザーのヒミツをdatabaseに送信
def save_to_firestore(secret):
    global USER_ID
    doc_ref = db.collection('user').document(USER_ID) 
    doc_ref.set({
        'private': secret
    })
    USER_ID=0
    
# 予定時刻（10分前）のUnixTime変換
def convert_to_timestamp(year, month, day, hour, minute):
    # 入力を日時オブジェクトに変換
    datetime_obj = datetime(year, month, day, hour, minute)

    timestamp = (datetime_obj - datetime(1970, 1, 1, 9, 0)).total_seconds()

    return int(timestamp) # 整数値で返す

# メッセージのスケジューリング
def schedule_message(jsf, text, channel_id, scheduled_time, y, mo, d, h, mi):
    with open(jsf, "r") as f:
        message_payload = json.load(f)

    app.client.chat_scheduleMessage(
        text = text,
        channel = channel_id,
        post_at = scheduled_time, 
        blocks = message_payload["blocks"]
    )
    # n分間の待機
    timeout = (datetime(y, mo, d, h, mi) - datetime.now()).total_seconds() 
    time.sleep(timeout)

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
    global GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY, GLOBAL_MONTH_RE, GLOBAL_DAY_RE
    GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY = GLOBAL_DATE.split("-")
    
    GLOBAL_YEAR = int(GLOBAL_YEAR)
    
    if str(GLOBAL_MONTH).startswith("0"):
        GLOBAL_MONTH_RE = int(str(GLOBAL_MONTH)[1:])
    
    else:
        GLOBAL_MONTH_RE = int(GLOBAL_MONTH)
        
    if str(GLOBAL_DAY).startswith("0"):
        GLOBAL_DAY_RE = int(str(GLOBAL_DAY)[1:])
        
    else:
        GLOBAL_DAY_RE = int(GLOBAL_DAY)
    
# 選択した時間の抽出
@app.action("select_hour")
def handle_register_hour(ack, body, say):
    global GLOBAL_HOUR
    GLOBAL_HOUR = int(body["actions"][0]["selected_option"]["value"])
    ack()
    
# 選択した分の抽出
@app.action("select_minute")
def handle_register_minute(ack, body):
    global GLOBAL_MINUTE
    GLOBAL_MINUTE = int(body["actions"][0]["selected_option"]["value"])
    ack()
    
# 送信ボタンを押したときの処理
@app.view("register_date")
def handle_message_events(ack, say):
    global USER_ID
    ack()
    message = f"あなたが登録したのは、{GLOBAL_YEAR}年{GLOBAL_MONTH_RE}月{GLOBAL_DAY_RE}日{GLOBAL_HOUR}時{GLOBAL_MINUTE}分です"
    say(channel = USER_ID, text=message)
    send_message_from_json("JSON/check_secret.json", USER_ID)

@app.action("yes_secret")
def start_secret(ack: Ack, body: dict, client: WebClient, say):
    ack()
    with open("JSON/register_secret.json", "r", encoding="UTF-8") as file:
        view= json.load(file)
    client.views_open(trigger_id=body["trigger_id"], view=view)
    
    global USER_ID, GLOBAL_YEAR, GLOBAL_MONTH_RE, GLOBAL_DAY_RE, GLOBAL_HOUR, GLOBAL_MINUTE
    
    # ユーザ情報を取得
    id = USER_ID
    response = client.users_info(user=id)
    user = response['user']
    username = user['name']  
      
    # チャンネルID
    channel_id = USER_ID
    
    # 起床確認
    text = "起床予定時刻の１０分前になりました！起きていますか？"

    # 予定時刻の計算
    scheduled_time = convert_to_timestamp(GLOBAL_YEAR, GLOBAL_MONTH_RE, GLOBAL_DAY_RE, GLOBAL_HOUR, GLOBAL_MINUTE) - 600 # 設定の10分前
    
    # jsonファイルの読込
    jst = "JSON/wakeup_scheduled_message.json"

    schedule_message(jst, text, channel_id, scheduled_time, GLOBAL_YEAR, GLOBAL_MONTH_RE, GLOBAL_DAY_RE, GLOBAL_HOUR, GLOBAL_MINUTE)
    
    if not flag:
    # タイムアウト時の処理
        #Firestoreからデータを取得
        doc_ref = db.collection('user').document(id)
        doc = doc_ref.get()
        if doc.exists:
            secret_info = doc.to_dict()['private']
            USER_ID = 0
        else:
            secret_info = "秘密の情報がない"
            
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
				"text": f"なんと、<@{username}>さんの秘密は\n{secret_info}だそうです!",
			}
		}
	]
        )
        USER_ID = 0
    
# 秘密の保存(firebase)
@app.view("register_secret")
def save_secret(say, body, ack):
    global SECRET
    
    SECRET = body["view"]["state"]["values"][body["view"]["blocks"][0]["block_id"]]["input_secret"]["value"]
    
    ack()
    
    message = f"登録が完了しました！それでは、期日にお会いしましょう😎"
    say(channel = USER_ID, text = message)
    
    save_to_firestore(SECRET)

"""  
# ここからschedued.pyの内容
@app.action("input_secret")
def send_scheduled_message():
    global USER_ID, GLOBAL_YEAR, GLOBAL_MONTH_RE, GLOBAL_DAY_RE, GLOBAL_HOUR, GLOBAL_MINUTE
    
    # ユーザ情報を取得
    id = USER_ID
    response = client.users_info(user=id)
    user = response['user']
    username = user['name']  
      
    # チャンネルID
    channel_id = USER_ID
    
    # 起床確認
    text = "起床予定時刻の１０分前になりました！起きていますか？"

    # 予定時刻の計算
    scheduled_time = convert_to_timestamp(GLOBAL_YEAR, GLOBAL_MONTH_RE, GLOBAL_DAY_RE, GLOBAL_HOUR, GLOBAL_MINUTE)- 60 # 設定の10分前
    
    # jsonファイルの読込
    jst = "JSON/wakeup_scheduled_message.json"

    schedule_message(jst, text, channel_id, scheduled_time)
    
    if not flag:
    # タイムアウト時の処理
        #Firestoreからデータを取得
        doc_ref = db.collection('user').document(USER_ID)
        doc = doc_ref.get()
        if doc.exists:
            secret_info = doc.to_dict()['private']
            USER_ID = 0
        else:
            secret_info = "秘密の情報がない"
            
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
				"text": f"なんと、<@{username}>さんの秘密は\n{secret_info}だそうです!",
			}
		}
	]
        )
        USER_ID = 0"""
        
@app.action("wakeup")
def wakeup_confirm(ack, say):
    global USER_ID, flag
    flag = True
    ack()
    say("起床が確認出来ました！おはようございます☀️")
    
    USER_ID = 0
        
# アプリ起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()