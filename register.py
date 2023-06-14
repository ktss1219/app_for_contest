import os
from slack_bolt import App
import json
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

#グローバル変数の初期化
GLOBAL_DATE=0
GLOBAL_YEAR=0
GLOBAL_MONTH=0
GLOBAL_DAY=0
GLOBAL_HOUR=0
GLOBAL_MINUTE=0

#

def send_message_from_json(json_file_path, channel_id):
    with open(json_file_path, "r") as file:
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
    with open("selected_date.json", "w") as file:
        json.dump(GLOBAL_DATE, file)
        #say(GLOBAL_DATE)
    ack()
    global GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY
    GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY = GLOBAL_DATE.split("-")

#選択した時間の抽出
@app.action("select_hour")
def handle_register_hour(ack, body, say):
    global GLOBAL_HOUR
    GLOBAL_HOUR = body["actions"][0]["selected_option"]["value"]
    with open("selected_date.json", "w") as file:
        json.dump(GLOBAL_HOUR, file)
        #say(GLOBAL_HOUR)
    ack()

#選択した分の抽出
@app.action("select_minute")
def handle_register_minute(ack, body, say):
    global GLOBAL_MINUTE
    GLOBAL_MINUTE = body["actions"][0]["selected_option"]["value"]
    with open("selected_date.json", "w") as file:
        json.dump(GLOBAL_MINUTE, file)
        #say(GLOBAL_MINUTE)
    ack()
    
#送信ボタンを押したときの処理
@app.action("register_date")
def check_register_date(ack, body, say):
    global GLOBAL_YEAR, GLOBAL_MONTH, GLOBAL_DAY, GLOBAL_DAY, GLOBAL_HOUR, GLOBAL_MINUTE
    ack()
    message = f"あなたが登録したのは、{GLOBAL_YEAR}年{GLOBAL_MONTH}月{GLOBAL_DAY}日{GLOBAL_HOUR}時{GLOBAL_MINUTE}分です"
    say(message)
    

@app.view("secret_modal")
def handle_secret_modal_submission(ack, body, client):
    ack()
    user_input = body["view"]["state"]["values"]["secret_input"]["secret_input"]["value"]
    message = f"あなたの秘密は {user_input} です"
    client.chat_postMessage(channel="C05A7G0ARB7", text=message)

# アプリ起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
