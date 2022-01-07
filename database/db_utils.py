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
                have_must_attend boolean,
                group_id varchar(50)
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

    group_id = event_attribute[11]

    cur.execute("""
        INSERT INTO event VALUES ('%s', '%s', date '%s', date '%s', time '%s', time '%s', date '%s', time '%s', %s, '%s', %s, '%s');
    """ % (event_id, event_name, start_date, end_date, start_time, end_time, deadline_date, deadline_time, anonymous, preference, have_must_attend, group_id))

    conn.commit()
    conn.close()


def update_people_done(user_id):
    '''
        This function updates table people if a person voted.
        Input:
            user_id: string
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute('''
        UPDATE people SET done = True
        WHERE user_id = '%s';
    ''' % (user_id))

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
    choose_date_raw = user_choose[2].split('/')
    choose_date = '2022-' + \
        choose_date_raw[0] + '-' + choose_date_raw[1]  # need modify
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
            mention_user: list, [{'user_id':__, 'event_id':__, 'group_id':__},...,{}]
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

    mention_user = []
    usr = {}
    rows = cur.fetchall()
    for row in rows:
        usr['user_id'] = row[0]
        usr['event_id'] = row[1]
        usr['group_id'] = row[2]
        mention_user.append(usr)

    conn.close()

    return mention_user


def result_sofar(event_id):
    '''
        This function returns the result of a selected event so far.
        Input:
            event_id: string
        Output:
            result: list, [{'choose_date':__, 'choose_time_id':__, 'count':__},...,{}]
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT choose_date, choose_time_id FROM choose 
        WHERE event_id = '%s' 
    """ % (event_id))

    rows = cur.fetchall()
    result = []
    for row in rows:
        find = False
        for re in result:
            if re['choose_date'] == row[0] and re['choose_time_id'] == row[1]:
                re['count'] += 1
                find = True
        if find == False:
            time_section = {}
            time_section['choose_date'] = row[0]
            time_section['choose_time_id'] = row[1]
            time_section['count'] = 1
            result.append(time_section)

    conn.close()

    return result


def result_final(deadline):
    '''
        This function returns the result of events that up to deadline.
        Input:
            deadline: list
        Output:
            result: list, contains below three parameters
                event_id: string
                event_time_result: list, [{'date':__, 'time_id':__, 'count':__},...,{}]
                event_time_user: list, [{'user_id':__, 'choose_date':__, 'choose_time_id':__},...,{}]
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
            SELECT choose_date, choose_time_id FROM choose 
            WHERE event_id = '%s' 
        """ % (event_id))

        rows = cur.fetchall()
        event_time_result = []
        for row in rows:
            find = False
            for re in event_time_result:
                if re['date'] == row[0] and re['time_id'] == row[1]:
                    re['count'] += 1
                    find = True
            if find == False:
                time_section = {}
                time_section['date'] = row[0]
                time_section['time_id'] = row[1]
                time_section['count'] = 1
                event_time_result.append(time_section)

        cur.execute("""
            SELECT user_id, choose_date, choose_time_id FROM choose 
            WHERE event_id = '%s'; 
        """ % (event_id))

        rows = cur.fetchall()
        event_time_user = []
        for row in rows:
            user_choose = {}
            user_choose['user_id'] = row[0]
            user_choose['choose_date'] = row[1]
            user_choose['choose_time_id'] = row[2]
            event_time_user.append(user_choose)

        result.append([event_id, event_time_result, event_time_user])

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


def arbitrate(event_id):
    '''
        This function arbitrates an event.
        Input:
            event_id: string
        Output:

    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()
    cur.execute("""
    """)
    conn.commit()
    conn.close()
    return


def init_time():
    '''
        This function initializes table time.
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


def select_event(group_id):
    '''
        This function returns the content of table event using group_id.
        Input:
            group_id: string
        Output:
            event_attribute: dict
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM event
        WHERE group_id = '%s';
    """ % (group_id))

    event_attribute = {}
    rows = cur.fetchall()
    for row in rows:
        event_attribute['event_id'] = row[0]
        event_attribute['event_name'] = row[1]
        event_attribute['start_date'] = time.strftime(row[2], '%Y-%m-%d')
        event_attribute['end_date'] = time.strftime(row[3], '%Y-%m-%d')
        event_attribute['start_time'] = time.strftime(row[4], '%H:%M:%S')
        event_attribute['end_time'] = time.strftime(row[5], '%H:%M:%S')
        event_attribute['deadline_date'] = time.strftime(row[6], '%Y-%m-%d')
        event_attribute['deadline_time'] = time.strftime(row[7], '%H:%M:%S')
        event_attribute['anonymous'] = row[8]
        event_attribute['preference'] = row[9]
        event_attribute['have_must_attend'] = row[10]
        event_attribute['group_id'] = row[11]

    conn.commit()
    conn.close()

    return event_attribute


def select_event_id(event_id):
    '''
        This function returns the content of table event using event_id.
        Input:
            event_id: string
        Output:
            event_attribute: dict
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM event
        WHERE event_id = '%s';
    """ % (event_id))

    event_attribute = {}
    rows = cur.fetchall()
    for row in rows:
        print(row)
        event_attribute['event_id'] = row[0]
        event_attribute['event_name'] = row[1]
        event_attribute['start_date'] = str(row[2])
        event_attribute['end_date'] = str(row[3])
        event_attribute['start_time'] = str(row[4])
        event_attribute['end_time'] = str(row[5])
        event_attribute['anonymous'] = row[8]

    conn.commit()
    conn.close()

    return event_attribute


def select_time(time_id):
    '''
        This function returns time_start and time_end of an time_id.
        Input:
            time_id: int
        Output:
            time_slot: dict
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT time_start, time_end FROM time
        WHERE time_id = '%s';
    """ % (time_id))

    time_slot = {}
    rows = cur.fetchall()
    for row in rows:
        time_slot['time_start'] = row[0]
        time_slot['time_end'] = row[1]

    conn.commit()
    conn.close()

    return time_slot


def select_people(group_id):
    '''
        This function returns members of a group.
        Input:
            group_id: string
        Output:
            group_member: list, [{'user_id':__, 'user_name':__},...,{}]
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, user_name FROM people
        WHERE group_id = '%s';
    """ % (group_id))

    group_member = []
    rows = cur.fetchall()
    for row in rows:
        member = {}
        member['user_id'] = row[0]
        member['user_name'] = row[1]
        group_member.append(member)

    conn.commit()
    conn.close()

    return group_member
