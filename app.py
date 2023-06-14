import os
from slack_bolt import App
import json
import fcntl
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def send_message_from_json(json_file_path, channel_id):
    with open(json_file_path, "r") as file:
        json_data = json.load(file)
    
    app.client.chat_postMessage(channel=channel_id, **json_data)

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

def add_to_existing_section(json_file_path, section_text, start, end):
    with open(json_file_path, "r+") as json_file:
        fcntl.flock(json_file.fileno(), fcntl.LOCK_EX)
        json_data = json.load(json_file)
        
        if end == 24:
            for i in range(start, end):
                option = make_time_data(i)
                json_data["blocks"][3]["elements"][0]["options"].append(option)
        else:
             for i in range(start, end):
                option = make_time_data(i)
                json_data["blocks"][5]["elements"][0]["options"].append(option)
    
        json_file.seek(0)
        json.dump(json_data, json_file, indent=4)
        json_file.truncate()
        fcntl.flock(json_file.fileno(), fcntl.LOCK_UN)


def extract_selected_values(payload):
    actions = payload["actions"]
    selected_values = []
    for action in actions:
        if action["action_id"] == "select_date" or action["action_id"] == "select_hour" or action["action_id"] == "select_minute":
            selected_values.append(action["selected_option"]["value"])
    return selected_values


@app.message("登録")
def select_date(say):
    add_to_existing_section("JSON/register_date.json", "起きたい時間(時)を選んでください", 0, 24)
    add_to_existing_section("JSON/register_date.json", "起きたい時間(分)を選んでください", 1, 60)
    send_message_from_json("JSON/register_date.json","C05A7G0ARB7")


@app.action("register_date")
def handle_register_date(ack, body, say):
    ack()
    selected_values = extract_selected_values(body)
    selected_date = selected_values[0] if len(selected_values) >= 1 else None
    selected_hour = selected_values[1] if len(selected_values) >= 2 else None
    selected_minute = selected_values[2] if len(selected_values) >= 3 else None
    year, month , day = map(int, selected_date.split("-"))
    hour = int(selected_hour)
    minute = int(selected_minute)
    modal_json_file = "JSON/secret_modal.json"
    with open(modal_json_file, "r") as file:
        modal_json = json.load(file)
    app.client.views_open(trigger_id=say["trigger_id"], view=modal_json)


@app.view("secret_modal")
def handle_secret_modal_submission(ack, body, client):
    ack()
    user_input = body["view"]["state"]["values"]["secret_input"]["secret_input"]["value"]
    message = f"あなたの秘密は {user_input} です"
    client.chat_postMessage(channel="C05A7G0ARB7", text=message)

# アプリ起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()