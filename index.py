from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Channel Access Token
line_bot_api_token = os.getenv("line_bot_api_token")
line_bot_api = LineBotApi(line_bot_api_token)
# Channel Secret
webhook_token = os.getenv("webhook_token")
handler = WebhookHandler(webhook_token)

# don't touch this
# listen all the post request from /callback
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# this event will be triggered when someone send a message in a group
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    user_message = event.message.text
    print(event.message)
    reply_message = "@" + user_name + "your ID:" + user_id + "\n Testing!!! \n 您傳送的訊息為：\n" + user_message
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_message))

# this event will be triggered when the bot is invited to a group
@handler.add(JoinEvent)
def handle_join(event):
    summary = line_bot_api.get_group_summary(event.source.group_id)
    message = "Group Info\n"
    message += "group id" + summary.group_id + "\n"
    message += "group name" + summary.group_name + "\n"
    message += "picture url" + summary.picture_url
    line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

# don't touch this
if __name__ == "__main__":
    app.debug = True
    app.run()