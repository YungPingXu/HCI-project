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
###################


def create_tables():
    '''
        This function creates tables: choose, event, time and people.
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()
    cur.execute("""
            DROP TABLE IF EXISTS choose;
            CREATE TABLE choose(
                user_id varchar(50),
                event_id varchar(50),
                choose_date date,
                choose_time_id integer
            );

            DROP TABLE IF EXISTS event;
            CREATE TABLE event(
                event_id varchar(50) PRIMARY KEY,
                event_name varchar(50),
                start_date date,
                end_date date,
                start_time time,
                end_time time,
                deadline_date date,
                deadline_time time,
                anonymous boolean,
                preference varchar(50),
                have_must_attend boolean
            );

            DROP TABLE IF EXISTS people;
            CREATE TABLE people(
                user_id varchar(50) PRIMARY KEY,
                user_name varchar(50),
                event_id varchar(50),
                group_id varchar(50),
                done boolean,
                must_attend boolean
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


def insert_event(event_attribute):
    '''
        This function inserts attributes of an event into table event.
        Input:
            event_attribute: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    event_id = event_attribute[0]
    event_name = event_attribute[1]
    start_date = event_attribute[2]
    end_date = event_attribute[3]
    start_time = event_attribute[4] + ':00'
    end_time = event_attribute[5] + ':00'
    deadline_date = event_attribute[6]
    deadline_time = event_attribute[7] + ':00'

    anonymous = False
    if event_attribute[8] == 'true':
        anonymous = True

    preference = event_attribute[9]

    have_must_attend = False
    if event_attribute[10] == 'true':
        have_must_attend = True

    cur.execute("""
        INSERT INTO event VALUES ('%s', '%s', date '%s', date '%s', time '%s', time '%s', date '%s', time '%s', %s, '%s', %s);
    """ % (event_id, event_name, start_date, end_date, start_time, end_time, deadline_date, deadline_time, anonymous, preference, have_must_attend))

    conn.commit()
    conn.close()


def insert_choose(user_choose):
    '''
        This function inserts user's choice into table choose.
        Input:
            user_choose: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    user_id = user_choose[0]
    event_id = user_choose[1]
    choose_date = user_choose[2]
    choose_time_id = int(user_choose[3])  # string to integer

    cur.execute("""
        INSERT INTO choose VALUES ('%s', '%s', date '%s', %s);
    """ % (user_id, event_id, choose_date, choose_time_id))

    conn.commit()
    conn.close()


def delete_choose_rows(user_delete):
    '''
        This function deletes the rows of table choose 
        when a user wants to change his/her choices.
        Input:
            user_delete: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    user_id = user_delete[0]
    event_id = user_delete[1]

    cur.execute("""
        DELETE FROM choose 
        WHERE user_id = '%s'
        AND event_id = '%s';
    """ % (user_id, event_id))

    conn.commit()
    conn.close()


def mention(time_date_now):
    '''
        This function returns a list whom need to be mentioned.
        Input:
            time_date_now: list
        Output:
            mention_user: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    #time_date_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()).split()
    time_now = time_date_now[1]
    date_now = time_date_now[0]
    cur.execute("""
        SELECT user_id, event_id, group_id FROM people
        WHERE event_id IN
            (SELECT event_id FROM event
            WHERE deadline_time - time '%s' < time '00:30:00'
            AND deadline_date = date '%s')
        AND done = False;
    """ % (time_now, date_now))

    # mention_user: (user_id, event_id, group_id)
    mention_user = []

    rows = cur.fetchall()
    for row in rows:
        mention_user.append((row[0], row[1], row[2]))

    conn.close()

    return mention_user


def result_sofar(event_id):
    '''
        This function returns the result of a selected event so far.
        Input:
            event_id: string
        Output:
            result: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT time_id, count(time_id) FROM choose 
        WHERE event_id = '%s' 
        GROUP BY time_id
        ORDER by count(time_id) DESC;
    """ % (event_id))

    rows = cur.fetchall()
    result = []  # (time_id, count(time_id))
    for row in rows:
        result.append([row[0], row[1]])

    conn.close()

    return result


def result_final(deadline):
    '''
        This function returns the result of events that up to deadline.
        Input:
            deadline: list
        Output:
            result: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    deadline_time = deadline[1]
    deadline_date = deadline[0]
    cur.execute("""
        SELECT event_id FROM event 
        WHERE deadline_time = '%s'
        AND deadline_date = '%s';
    """ % (deadline_time, deadline_date))

    result = []
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

        result.append((event_id, time_user))

    conn.close()

    return result


def insert_people(user_attribute):
    '''
        This function inserts user's attributes into table people.
        Input:
            user_attribute: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    user_id = user_attribute[0]
    user_name = user_attribute[1]
    event_id = user_attribute[2]
    group_id = user_attribute[3]

    done = False
    if user_attribute[4] == 'true':
        done = True

    must_attend = False
    if user_attribute[5] == 'true':
        must_attend = True

    cur.execute("""
        INSERT INTO people VALUES ('%s', '%s', '%s', '%s', %s, %s);
    """ % (user_id, user_name, event_id, group_id, done, must_attend))

    conn.commit()
    conn.close()


def init_time():
    '''
        This function initializes table time;
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

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


def test():
    '''
        This function is just for test.
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        select * from event;
    """)

    rows = cur.fetchall()
    for row in rows:
        print(row)

    conn.commit()
    conn.close()
