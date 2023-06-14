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

@app.message("登録")
def select_date(say):
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
