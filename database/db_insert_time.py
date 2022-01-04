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
    INSERT INTO time VALUES (1, time '00:00', time '00:29');
    INSERT INTO time VALUES (2, time '00:30', time '00:59');
    INSERT INTO time VALUES (3, time '01:00', time '01:29');
    INSERT INTO time VALUES (4, time '01:30', time '01:59');
    INSERT INTO time VALUES (5, time '02:00', time '02:29');
    INSERT INTO time VALUES (6, time '02:30', time '02:59');
    INSERT INTO time VALUES (7, time '03:00', time '03:29');
    INSERT INTO time VALUES (8, time '03:30', time '03:59');
    INSERT INTO time VALUES (9, time '04:00', time '04:29');
    INSERT INTO time VALUES (10, time '04:30', time '04:59');
    INSERT INTO time VALUES (11, time '05:00', time '05:29');
    INSERT INTO time VALUES (12, time '05:30', time '05:59');
    INSERT INTO time VALUES (13, time '06:00', time '06:29');
    INSERT INTO time VALUES (14, time '06:30', time '06:59');
    INSERT INTO time VALUES (15, time '07:00', time '07:29');
    INSERT INTO time VALUES (16, time '07:30', time '07:59');
    INSERT INTO time VALUES (17, time '08:00', time '08:29');
    INSERT INTO time VALUES (18, time '08:30', time '08:59');
    INSERT INTO time VALUES (19, time '09:00', time '09:29');
    INSERT INTO time VALUES (20, time '09:30', time '09:59');
    INSERT INTO time VALUES (21, time '10:00', time '10:29');
    INSERT INTO time VALUES (22, time '10:30', time '10:59');
    INSERT INTO time VALUES (23, time '11:00', time '11:29');
    INSERT INTO time VALUES (24, time '11:30', time '11:59');
    INSERT INTO time VALUES (25, time '12:00', time '12:29');
    INSERT INTO time VALUES (26, time '12:30', time '12:59');
    INSERT INTO time VALUES (27, time '13:00', time '13:29');
    INSERT INTO time VALUES (28, time '13:30', time '13:59');
    INSERT INTO time VALUES (29, time '14:00', time '14:29');
    INSERT INTO time VALUES (30, time '14:30', time '14:59');
    INSERT INTO time VALUES (31, time '15:00', time '15:29');
    INSERT INTO time VALUES (32, time '15:30', time '15:59');
    INSERT INTO time VALUES (33, time '16:00', time '16:29');
    INSERT INTO time VALUES (34, time '16:30', time '16:59');
    INSERT INTO time VALUES (35, time '17:00', time '17:29');
    INSERT INTO time VALUES (36, time '17:30', time '17:59');
    INSERT INTO time VALUES (37, time '18:00', time '18:29');
    INSERT INTO time VALUES (38, time '18:30', time '18:59');
    INSERT INTO time VALUES (39, time '19:00', time '19:29');
    INSERT INTO time VALUES (40, time '19:30', time '19:59');
    INSERT INTO time VALUES (41, time '20:00', time '20:29');
    INSERT INTO time VALUES (42, time '20:30', time '20:59');
    INSERT INTO time VALUES (43, time '21:00', time '21:29');
    INSERT INTO time VALUES (44, time '21:30', time '21:59');
    INSERT INTO time VALUES (45, time '22:00', time '22:29');
    INSERT INTO time VALUES (46, time '22:30', time '22:59');
    INSERT INTO time VALUES (47, time '23:00', time '23:29');
    INSERT INTO time VALUES (48, time '23:30', time '23:59');
""")
conn.commit()
conn.close()
