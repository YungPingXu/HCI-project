from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timezone, timedelta
import database.db_utils
import os
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import *
from linebot.models import FlexSendMessage, TextSendMessage

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

def mention_user(group_id, user_name):
    line_bot_api.push_message(group_id, TextSendMessage(text="@" + user_name + " 尚未填寫 請盡速填寫！"))

sched = BlockingScheduler()

#already_mentioned = []

@sched.scheduled_job("interval", minutes=2)
def timed_job():
    mention_list = database.db_utils.mention(get_Taiwan_time())
    print(mention_list)
    for i in mention_list:
        #index = i["user_id"] + "," + i["event_id"] + "," + i["group_id"]
        #if index not in already_mentioned:
        mention_user(i[3], i[1])
            #already_mentioned.append(index)

sched.start()