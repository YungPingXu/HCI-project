from flask import Flask, request, abort, render_template, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot.models import FlexSendMessage, TextSendMessage
from dotenv import load_dotenv
from database import db_utils

from datetime import timedelta
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
    group_id = event.source.group_id
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    user_message = event.message.text
    message = event.message.text
    print(event.message)

    if message == "botbot":
        FlexMessage = json.load(open('new_event.json', 'r', encoding='utf-8'))
        FlexMessage["footer"]["contents"][0]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com?group_id=" + group_id
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "botdone":
        FlexMessage = json.load(open('voting_time.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "no_common":
        FlexMessage = json.load(open('no_common.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "everyone_ok_result":
        FlexMessage = json.load(open('eneryone_ok_result.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "result":
        FlexMessage = json.load(open('normal_result.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "judge":
        FlexMessage = json.load(open('judge.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('profile', FlexMessage))
    elif message == "hihi":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="I'm here !! :)"))



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
    if request.method == "GET":
        if "group_id" in request.values:
            group_id = request.values["group_id"]
            return render_template("index.html", group_id=group_id)
        else:
            return redirect("/?group_id=C36e166f739d14fffbd20c0ce7c772eef")
    return ""


@app.route("/create-event", methods=["POST"])  # 路由和處理函式配對
def create_event():
    if request.method == "POST":
        event_attribute = []

        length_of_string = 8
        event_id = ''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(length_of_string))
        print("event id is", event_id)  # add
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
            deadline_date = str(datetime.datetime.strptime(
                dates[0], "%Y-%m-%d") - timedelta(1))
            print(deadline_date)
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

        event_attribute.append(request.values["group_id"])
        event_attribute.append('none')

        db_utils.insert_event(event_attribute)

        # use member_list to insert table people
        for member in db_utils.get_members(request.values["group_id"]):
            user_attribute = []
            user_attribute.append(member[0])
            user_attribute.append(member[1])
            user_attribute.append(event_id)
            user_attribute.append(request.values["group_id"])
            user_attribute.append("false")
            user_attribute.append("false")
            user_attribute.append(request.values["event_name"])
            print(request.values["event_name"])
            db_utils.insert_people(user_attribute)

        return event_id
    return redirect(url_for("index"))


time_mapping = {
    "00:00": 1,
    "00:30": 2,
    "01:00": 3,
    "01:30": 4,
    "02:00": 5,
    "02:30": 6,
    "03:00": 7,
    "03:30": 8,
    "04:00": 9,
    "04:30": 10,
    "05:00": 11,
    "05:30": 12,
    "06:00": 13,
    "06:30": 14,
    "07:00": 15,
    "07:30": 16,
    "08:00": 17,
    "08:30": 18,
    "09:00": 19,
    "09:30": 20,
    "10:00": 21,
    "10:30": 22,
    "11:00": 23,
    "11:30": 24,
    "12:00": 25,
    "12:30": 26,
    "13:00": 27,
    "13:30": 28,
    "14:00": 29,
    "14:30": 30,
    "15:00": 31,
    "15:30": 32,
    "16:00": 33,
    "16:30": 34,
    "17:00": 35,
    "17:30": 36,
    "18:00": 37,
    "18:30": 38,
    "19:00": 39,
    "19:30": 40,
    "20:00": 41,
    "20:30": 42,
    "21:00": 43,
    "21:30": 44,
    "22:00": 45,
    "22:30": 46,
    "23:00": 47,
    "23:30": 48
}


@app.route("/vote", methods=["GET"])  # 路由和處理函式配對
def vote():
    if request.method == "GET":
        if "event_id" in request.values:
            event_attribute = db_utils.select_event_id(
                request.values["event_id"])
            if event_attribute:
                result = {}
                result["event_id"] = event_attribute["event_id"]
                result["event_name"] = event_attribute['event_name']
                result["member_list"] = db_utils.get_members(
                    event_attribute['group_id'])
                result["date_list"] = []

                current_date = event_attribute["start_date"]
                weekdays = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
                current_day = weekdays[datetime.datetime.strptime(
                    current_date, "%Y-%m-%d").isoweekday() - 1]
                # 星期幾
                while True:
                    tmp = current_date.split("-")
                    date_format = []
                    date_format.append(tmp[1] + "/" + tmp[2] + current_day)
                    date_format.append(current_date)
                    result["date_list"].append(date_format)
                    if current_date == event_attribute["end_date"]:
                        break
                    next_date = datetime.datetime.strptime(
                        current_date, "%Y-%m-%d") + datetime.timedelta(days=1)
                    current_day = weekdays[next_date.isoweekday() - 1]
                    current_date = next_date.strftime('%Y-%m-%d')

                result["time_list"] = []
                current_time = event_attribute["start_time"]
                end_time = datetime.datetime.strptime(
                    event_attribute["end_time"], "%H:%M:%S") + datetime.timedelta(minutes=1)
                end_time = end_time.strftime("%H:%M:%S")
                while current_time != end_time:
                    tmp = current_time.split(":")
                    tmplist = []
                    tmplist.append(tmp[0] + ":" + tmp[1])
                    tmplist.append(time_mapping[tmp[0] + ":" + tmp[1]])
                    result["time_list"].append(tmplist)
                    next_time = datetime.datetime.strptime(
                        current_time, "%H:%M:%S") + datetime.timedelta(minutes=30)
                    current_time = next_time.strftime("%H:%M:%S")
                result["start_time"] = event_attribute["start_time"]
                result["end_time"] = event_attribute["end_time"]
                return render_template("vote.html", result=result)
            else:
                return "this event_id does not exist"
        else:
            return "event_id parameter does not exist"
    else:
        return redirect(url_for("index"))


@app.route("/send_vote", methods=["POST"])  # 路由和處理函式配對
def send_vote():
    if request.method == "POST":
        date_and_time = request.values["selected_time"][:-1].split(';')

        user_delete = []
        user_delete.append(request.values["user_id"])
        user_delete.append(request.values["event_id"])
        db_utils.delete_choose_rows(user_delete)

        for dt in date_and_time:
            print(dt)
            choose_attribute = []
            choose_attribute.append(request.values["user_id"])
            choose_attribute.append(request.values["event_id"])
            choose_date = dt.split(',')[0]
            choose_time_id = dt.split(',')[1]
            choose_attribute.append(choose_date)
            choose_attribute.append(choose_time_id)
            db_utils.insert_choose(choose_attribute)
            db_utils.update_people_done(request.values["user_id"])

        return "成功送出！"
    return redirect(url_for("index"))


@app.route("/display_vote", methods=["GET"])  # 路由和處理函式配對
def display_vote():
    if request.method == "GET":
        if "event_id" in request.values:
            event_attribute = db_utils.select_event_id(
                request.values["event_id"])
            if event_attribute:
                result = {}
                result["event_id"] = event_attribute["event_id"]
                result["event_name"] = event_attribute['event_name']
                result["date_list"] = []

                current_date = event_attribute["start_date"]
                weekdays = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
                current_day = weekdays[datetime.datetime.strptime(
                    current_date, "%Y-%m-%d").isoweekday() - 1]
                # 星期幾
                while True:
                    tmp = current_date.split("-")
                    date_format = []
                    date_format.append(tmp[1] + "/" + tmp[2] + current_day)
                    date_format.append(current_date)
                    result["date_list"].append(date_format)
                    if current_date == event_attribute["end_date"]:
                        break
                    next_date = datetime.datetime.strptime(
                        current_date, "%Y-%m-%d") + datetime.timedelta(days=1)
                    current_day = weekdays[next_date.isoweekday() - 1]
                    current_date = next_date.strftime('%Y-%m-%d')

                result["time_list"] = []
                current_time = event_attribute["start_time"]
                end_time = datetime.datetime.strptime(
                    event_attribute["end_time"], "%H:%M:%S") + datetime.timedelta(minutes=1)
                end_time = end_time.strftime("%H:%M:%S")
                while current_time != end_time:
                    tmp = current_time.split(":")
                    tmplist = []
                    tmplist.append(tmp[0] + ":" + tmp[1])
                    tmplist.append(time_mapping[tmp[0] + ":" + tmp[1]])
                    result["time_list"].append(tmplist)
                    next_time = datetime.datetime.strptime(
                        current_time, "%H:%M:%S") + datetime.timedelta(minutes=30)
                    current_time = next_time.strftime("%H:%M:%S")
                result["start_time"] = event_attribute["start_time"]
                result["end_time"] = event_attribute["end_time"]

                print(result["date_list"])
                display_vote = []
                for i in db_utils.result_sofar(result["event_id"]):
                    display_vote.append(
                        str(i["choose_date"]) + "," + str(i["choose_time_id"]) + "," + str(i["count"]))
                result["display_vote"] = display_vote

                result["not_yet_vote"] = db_utils.not_yet_vote(result["event_id"])[
                    'no_vote_count']

                return render_template("display-vote.html", result=result)
            else:
                return "this event_id does not exist"
        else:
            return "event_id parameter does not exist"
    return redirect(url_for("index"))


# don't touch this
if __name__ == "__main__":
    db_utils.create_tables()
    app.debug = True
    app.run()
