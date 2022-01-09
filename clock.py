from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timezone, timedelta
import database.db_utils
import os
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import *
from linebot.models import FlexSendMessage, TextSendMessage
import json

load_dotenv()
# Channel Access Token
line_bot_api_token = os.getenv("line_bot_api_token")
line_bot_api = LineBotApi(line_bot_api_token)

def get_Taiwan_time():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
    time_date_now = []
    time_date_now.append(dt2.strftime("%Y-%m-%d"))
    time_date_now.append(dt2.strftime("%H:%M:%S"))
    return time_date_now

def mention_user(group_id, user_name_list, event_name, event_id):
    user_name = ""
    for i in user_name_list:
        user_name += "@" + i + " "
    FlexMessage = json.load(open('mention.json', 'r', encoding='utf-8'))
    FlexMessage["body"]["contents"][0]["contents"][0]["contents"][0]["text"] = user_name + "尚未填寫「" + event_name + "」意願時間，請盡速填寫!!"
    FlexMessage["footer"]["contents"][0]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/vote?event_id=" + event_id
    FlexMessage["footer"]["contents"][1]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/display_vote?event_id=" + event_id
    line_bot_api.push_message(group_id, FlexSendMessage('Scheduling Bot', FlexMessage))

sched = BlockingScheduler()

@sched.scheduled_job("interval", minutes=2)
def timed_job():
    mention_list = database.db_utils.mention(get_Taiwan_time())
    print(mention_list)
    send_list = {}
    for i in mention_list:
        tmp_send = []
        tmp_send.append(i[2]) # event_id
        tmp_send.append(i[3]) # group_id
        tmp_send.append(i[4]) # event_name
        tmp_send.append([])
        send_list[i[2] + "," + i[3]] = tmp_send
    for i in mention_list:
        send_list[i[2] + "," + i[3]][3].append(i[1])
    print(send_list)
    for i in send_list:
        event_id = send_list[i][0]
        group_id = send_list[i][1]
        event_name = send_list[i][2]
        user_name_list = send_list[i][3]
        mention_user(group_id, user_name_list, event_name, event_id)
    
    database.db_utils.check_and_end(get_Taiwan_time())
    
sched.start()