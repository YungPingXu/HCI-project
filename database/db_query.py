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
    SELECT * FROM test;
""")
rows = cur.fetchall()
print("col1 col2")
for row in rows:
    print(row[0], row[1])
conn.close()