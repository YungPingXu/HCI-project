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
    INSERT INTO test VALUES ('test1', 'test2');
    INSERT INTO test VALUES ('test3', 'test4');
""")
conn.commit()
conn.close()