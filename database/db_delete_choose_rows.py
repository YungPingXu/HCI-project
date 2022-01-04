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

cur.execute("""
    DELETE FROM choose 
    WHERE user_id = '%s'
    AND event_id = '%s';
""" % (user_id, event_id))

conn.commit()
conn.close()