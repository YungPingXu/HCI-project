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

cur.execute("""
    DROP TABLE IF EXISTS choose;
    CREATE TABLE choose(
        user_id varchar(50),
        event_id varchar(50),
        date_id date,
        time_id integer
    );

    DROP TABLE IF EXISTS event;
    CREATE TABLE event(
        event_id varchar(50) PRIMARY KEY,
        event_name varchar(50),
        start_date_id date,
        end_date_id date,
        start_time time,
        end_time time,
        roll_end_date date,
        roll_end_time time,
        anonymous boolean,
        day_or_night boolean,
        have_must_be boolean
    );

    DROP TABLE IF EXISTS people;
    CREATE TABLE people(
        user_id varchar(50) PRIMARY KEY,
        user_name varchar(50),
        event_id varchar(50),
        group_id varchar(50),
        done boolean,
        must_be boolean
    );

    DROP TABLE IF EXISTS time;
    CREATE TABLE time(
        time_id integer,
        time_start time,
        time_end time
    );
""")

conn.commit()
conn.close()
