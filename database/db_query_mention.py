import psycopg2
from dotenv import load_dotenv
import os
import time

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

# mention
time_list = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()).split()
time_now = time_list[1]
date_now = time_list[0]
cur.execute("""
    SELECT user_id, event_id, group_id FROM people
    WHERE event_id IN
        (SELECT event_id FROM event
        WHERE roll_end_time - time '%s' < time '00:30:00'
        AND roll_end_date = date '%s')
    AND done = False;
""" % (time_now, date_now))

# mention_user: (user_id, event_id, group_id)
mention_user = []

rows = cur.fetchall()
for row in rows:
    mention_user.append((row[0], row[1], row[2]))

conn.close()
