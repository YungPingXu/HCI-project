import psycopg2
from dotenv import load_dotenv
import os

### don't touch ###
load_dotenv()
database = os.getenv("database")
user = os.getenv("user")
password = os.getenv("password")
host= os.getenv("host")
port = os.getenv("port")

conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
cur = conn.cursor()
###################

cur.execute("""
    UPDATE test SET col2='test5' WHERE col1='test3';
""")
conn.commit()
conn.close()