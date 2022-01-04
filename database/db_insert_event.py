import psycopg2
from dotenv import load_dotenv
import os

### don't touch ###
load_dotenv()
database = os.getenv("database")
user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")

conn = psycopg2.connect(database=database, user=user,
                        password=password, host=host, port=port)
cur = conn.cursor()
###################

event_id = 'ashjfq2oroh'
event_name = 'meeting'
start_date_id = '2021-12-25'
end_date_id = '2021-12-31'
start_time = '14:00'
end_time = '15:30'
roll_end_date = '2021-12-14'
roll_end_time = '22:00'
anonymous = False
day_or_night = True
have_must_be = False

cur.execute("""
    INSERT INTO event VALUES ('%s', '%s', date '%s', date '%s', time '%s', time '%s', date '%s', time '%s', %s, %s, %s);
""" % (event_id, event_name, start_date_id, end_date_id, start_time, end_time, roll_end_date, roll_end_time, anonymous, day_or_night, have_must_be))

conn.commit()
conn.close()
