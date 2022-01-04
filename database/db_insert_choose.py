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

user_id = 'ghjdjshfsr'
event_id = 'ashjfq2oroh'
date_id = '2021-12-13'
time_id = 4

cur.execute("""
    INSERT INTO choose VALUES ('%s', '%s', date '%s', %s);
""" % (user_id, event_id, date_id, time_id))

conn.commit()
conn.close()
