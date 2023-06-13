from flask import Flask, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import fcntl

app = Flask(__name__)

#選択する時間データの作成
def make_time_data(n):
    num = str(n)
    data = [
        {
            "text": {
                "type": "plain_text",
                "text": num,
                "emoji": False
            },
            "value": num
        }
    ]
    return data

JSON_FILE_PATH = "JSON/register_date.json"  

def add_to_existing_section(JSON_FILE_PATH, section_text, start, end):
    with open(JSON_FILE_PATH, "r+") as json_file:
        fcntl.flock(json_file.fileno(), fcntl.LOCK_EX)
        json_data = json.load(json_file)
        blocks = json_data["blocks"]
        
        for block in blocks:
            if block.get("type") == "section":
                block_text = block.get("text", {}).get("text")
                
                if block_text == section_text:
                    accessory = block.get("accessory")
                    
                    if accessory and accessory.get("type") == "static_select":
                        for i in range(start, end):
                            data = make_time_data(i)
                            accessory["options"].extend(data)
                            
        json_file.seek(0)
        json.dump(json_data, json_file, indent=4)
        json_file.truncate()
        fcntl.flock(json_file.fileno(), fcntl.LOCK_UN)
        
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    
    # イベントの種類を取得
    event_type = data.get("event", {}).get("type")
    
    if event_type == "message":
        message_text = data.get("event", {}).get("text")
    
        if "登録" in message_text:
            add_to_existing_section("register_date.json", "起きたい時間(時)を選んでください", 0, 24)
            add_to_existing_section("register_date.json", "起きたい時間(分)を選んでください", 1, 60)
            
            send_to_slack_message("JSON/register_date.json")
            
    return "", 200

def send_to_slack_message(json_file_path):
    with open(json_file_path, "r") as file:
        json_data = json.load(file)
        
    client = WebClient(token="your_token")
    try:
        response = client.chat_postMessage(**json_data)
        print("メッセージを送信しました")
    except SlackApiError as e:
        print(f"メッセージの送信に失敗しました: {e.response['error']}")
        
if __name__ == "__main__":
    app.run()