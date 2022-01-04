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

user_id = 'afhalkdsjfhafh'
user_name = 'agarya'
event_id = 'ashjfq2oroh'
group_id = 'asdfaf'
done = False
must_be = False

cur.execute("""
    INSERT INTO people VALUES ('%s', '%s', '%s', '%s', %s, %s);
""" % (user_id, user_name, event_id, group_id, done, must_be))

conn.commit()
conn.close()
