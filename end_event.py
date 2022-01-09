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

sched = BlockingScheduler()

@sched.scheduled_job("interval", minutes=2)
def timed_job():
    database.db_utils.check_and_end(get_Taiwan_time())

sched.start()