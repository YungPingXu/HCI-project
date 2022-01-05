from flask import Flask, request, abort, render_template, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot.models import FlexSendMessage, TextSendMessage
from dotenv import load_dotenv
from ..database import db_utils

import os
import json
import string
import random
import time

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
    message = event.message.text
    print(event.message)

    if message == "botbot":
        FlexMessage = json.load(open('new_event.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(
            event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "botdone":
        FlexMessage = json.load(
            open('attend_event.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(
            event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "hihi":
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="I'm here !! :)"))


# this event will be triggered when the bot is invited to a group
@handler.add(JoinEvent)
def handle_join(event):
    summary = line_bot_api.get_group_summary(event.source.group_id)
    message = "Group Info\n"
    message += "group id" + summary.group_id + "\n"
    message += "group name" + summary.group_name + "\n"
    message += "picture url" + summary.picture_url
    line_bot_api.reply_message(event.reply_token, TextSendMessage(message))


@app.route("/", methods=["GET"])  # 路由和處理函式配對
def index():
    return render_template("index.html")


@app.route("/create-event", methods=["POST"])  # 路由和處理函式配對
def create_event():
    if request.method == "POST":
        '''event_attribute = []

        length_of_string = 8
        event_id = ''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(length_of_string))
        event_attribute.append(event_id)
        event_attribute.append(request.values["event_name"])

        dates = []
        for date in request.values["date"].split(','):
            temp_date = date.split('-')
            change_date = temp_date[2] + '-' + \
                temp_date[1] + '-' + temp_date[0]
            dates.append(change_date)
        event_attribute.append(dates[0])
        event_attribute.append(dates[1])

        event_attribute.append(request.values["start_time"])
        event_attribute.append(request.values["end_time"])

        deadline_date = request.values["deadline_date"]
        if request.values["deadline_date"] == '':
            deadline_date = dates[0]
        event_attribute.append(deadline_date)

        deadline_time = request.values["deadline_time"]
        if request.values["deadline_time"] == '':
            deadline_time = request.values["start_time"]
        event_attribute.append(deadline_time)

        event_attribute.append(request.values["anonymous"])

        preference = request.values["preference"]
        if request.values["preference"] == '':
            preference = 'all_ok'
        event_attribute.append(preference)

        # event_attribute.append(request.values["have_must_attend"])
        event_attribute.append('false')

        db_utils.insert_event(event_attribute)

        # print * of table event
        # db_utils.test()'''

        return "success"
    return redirect(url_for("index"))


# don't touch this
if __name__ == "__main__":
    # db_utils.create_tables()
    # db_utils.init_time()
    app.debug = True
    app.run()
