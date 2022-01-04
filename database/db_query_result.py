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

# result
roll_end_time = '14:00'
roll_end_date = '2022-01-10'
cur.execute("""
    SELECT event_id FROM event 
    WHERE roll_end_time = '%s'
    AND roll_end_date = '%s';
""" % (roll_end_time, roll_end_date))

events = cur.fetchall()
for event in events:
    event_id = event[0]

    cur.execute("""
        SELECT time_id, count(time_id) FROM choose 
        WHERE event_id = '%s' 
        GROUP BY time_id
        ORDER by count(time_id) DESC;
    """ % (event_id))

    rows = cur.fetchall()
    times = []
    for row in rows:
        # print(row)
        times.append([row[0], row[1]])

    time_user = []
    for time_roll in times:
        time_id = time_roll[0]
        cur.execute("""
            SELECT user_id FROM choose 
            WHERE event_id = '%s' AND time_id = %s; 
        """ % (event_id, time_id))
        rows = cur.fetchall()
        for row in rows:
            time_user.append([time_id, row[0]])

    '''for usr in time_user:
        print(usr)'''

conn.close()
