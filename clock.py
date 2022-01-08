from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timezone, timedelta
from database.db_utils import mention
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
    return dt2.strftime("%Y-%m-%d %H:%M:%S")

def mention_user(group_id, user_name):
    line_bot_api.push_message(group_id, TextSendMessage(text="@" + user_name))

sched = BlockingScheduler()

already_mentioned = []

@sched.scheduled_job("interval", minutes=2)
def timed_job():
    mention_user = mention(get_Taiwan_time())
    if mention_user:
        for i in mention_user:
            index = i["user_id"] + "," + i["event_id"] + "," + i["group_id"]
            if index not in already_mentioned:
                mention_user(i["group_id"], i["user_name"])
                already_mentioned.append()

sched.start()