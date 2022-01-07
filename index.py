from flask import Flask, request, abort, render_template, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot.models import FlexSendMessage, TextSendMessage
from dotenv import load_dotenv
from database import db_utils

import datetime
import time
import random
import string
import json
import os

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
        event_attribute = []

        length_of_string = 8
        event_id = ''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(length_of_string))
        print("event id is", event_id) # add
        event_attribute.append(event_id)
        event_attribute.append(request.values["event_name"])

        dates = []
        for date in request.values["date"].split(','):
            temp_date = date.split('-')
            change_date = temp_date[2] + '-' + \
                temp_date[1] + '-' + temp_date[0]
            dates.append(change_date)
        event_attribute.append(dates[0])
        event_attribute.append(dates[-1])

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

        # event_attribute.append(request.values["group_id"])
        event_attribute.append('none')
        print(event_attribute)
        db_utils.insert_event(event_attribute)

        return event_id
    return redirect(url_for("index"))

@app.route("/vote", methods=["GET"])  # 路由和處理函式配對
def vote():
    event_attribute = db_utils.select_event_id(request.values["event_id"])
    result = {}
    result["event_id"] = event_attribute["event_id"]
    result["event_name"] = event_attribute['event_name']
    result["date_list"] = []

    current_date = event_attribute["start_date"]
    weekdays = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
    current_day = weekdays[datetime.datetime.strptime(current_date, "%Y-%m-%d").isoweekday() - 1]
    # 星期幾
    while True:
        tmp = current_date.split("-")
        result["date_list"].append(tmp[1] + "/" + tmp[2] + current_day)
        if current_date == event_attribute["end_date"]:
            break
        next_date = datetime.datetime.strptime(current_date, "%Y-%m-%d") + datetime.timedelta(days=1)
        current_day = weekdays[next_date.isoweekday() - 1]
        current_date = next_date.strftime('%Y-%m-%d')
    
    result["time_list"] = []
    current_time = event_attribute["start_time"]
    end_time = datetime.datetime.strptime(event_attribute["end_time"], "%H:%M:%S") + datetime.timedelta(minutes=1)
    end_time = end_time.strftime("%H:%M:%S")
    while True:
        tmp = current_time.split(":")
        result["time_list"].append(tmp[0] + ":" + tmp[1])
        if current_time == end_time:
            break
        result["time_list"].append(current_time)
        next_time = datetime.datetime.strptime(current_time, "%H:%M:%S") + datetime.timedelta(minutes=30)
        current_time = next_time.strftime("%H:%M:%S")
    result["start_time"] = event_attribute["start_time"]
    result["end_time"] = event_attribute["end_time"]
    print(result["start_time"], result["end_time"])
    print(result["time_list"])
    return render_template("vote.html", result=result)

# don't touch this
if __name__ == "__main__":
    db_utils.create_tables()
    db_utils.init_time()
    app.debug = True
    app.run()
