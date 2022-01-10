import psycopg2
from dotenv import load_dotenv
import os
import time
from operator import itemgetter
import json
from linebot import LineBotApi
from linebot.models import *
from linebot.models import FlexSendMessage, TextSendMessage
from urllib import parse

### don't touch ###
load_dotenv()
# Channel Access Token
line_bot_api_token = os.getenv("line_bot_api_token")
line_bot_api = LineBotApi(line_bot_api_token)
database = os.getenv("database")
user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")
user1_id = os.getenv("user1_id")
user1_name = os.getenv("user1_name")
user1_group_id = os.getenv("user1_group_id")
user2_id = os.getenv("user2_id")
user2_name = os.getenv("user2_name")
user2_group_id = os.getenv("user2_group_id")
user3_id = os.getenv("user3_id")
user3_name = os.getenv("user3_name")
user3_group_id = os.getenv("user3_group_id")
###################


def create_constant_table():
    '''
        This function creates tables: time and member_list.
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()
    cur.execute("""
            DROP TABLE IF EXISTS time;
            CREATE TABLE time(
                time_id integer,
                time_start time,
                time_end time
            );

            DROP TABLE IF EXISTS member_list;
            CREATE TABLE member_list(
                user_id varchar(50) PRIMARY KEY,
                user_name varchar(50),
                group_id varchar(50)
            );
        """)

    conn.commit()
    conn.close()


def create_tables():
    '''
        This function creates tables: choose, event, and people.
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
                group_id varchar(50),
                dead boolean
            );

            DROP TABLE IF EXISTS people;
            CREATE TABLE people(
                user_id varchar(50),
                user_name varchar(50),
                event_id varchar(50),
                group_id varchar(50),
                done boolean,
                must_attend boolean,
                event_name varchar(50),
                PRIMARY KEY (user_id, event_id)
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

    preference = 'late'
    if event_attribute[9] == 'early':
        preference = 'early'

    have_must_attend = False
    if event_attribute[10] == 'true':
        have_must_attend = True

    group_id = event_attribute[11]

    dead = False
    if event_attribute[12] == 'true':
        dead = True

    cur.execute("""
        INSERT INTO event VALUES ('%s', '%s', date '%s', date '%s', time '%s', time '%s', date '%s', time '%s', %s, '%s', %s, '%s', %s);
    """ % (event_id, event_name, start_date, end_date, start_time, end_time, deadline_date, deadline_time, anonymous, preference, have_must_attend, group_id, dead))

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
    choose_date = user_choose[2]
    choose_time_id = int(user_choose[3])

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
            mention_user: list, [['user_id', 'user_name', 'event_id', 'group_id', 'event_name'],...,[]]
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    time_now = time_date_now[1]
    date_now = time_date_now[0]
    cur.execute("""
        SELECT user_id, user_name, event_id, group_id, event_name FROM people
        WHERE event_id IN
            (SELECT event_id FROM event
            WHERE deadline_time - time '%s' < time '00:30:00'
            AND time '%s' < deadline_time
            AND deadline_date = date '%s')
        AND done = False;
    """ % (time_now, time_now, date_now))

    mention_user = []
    rows = cur.fetchall()
    print(rows)
    for row in rows:
        usr = []
        usr.append(row[0])
        usr.append(row[1])
        usr.append(row[2])
        usr.append(row[3])
        usr.append(row[4])
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


def result_final(event_id):
    '''
        This function returns the result of a event that up to deadline.
        Input:
            event_id: string
        Output:
            result: list, contains below four parameters
                event_id: string
                event_time_result: list, [{'date':__, 'time_id':__, 'count':__},...,{}]
                event_time_user: list, [{'user_id':__, 'choose_date':__, 'choose_time_id':__},...,{}]
                voted_number: int
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

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
    voted_number = 0
    user_vote = []
    for row in rows:
        user_choose = {}
        user_choose['user_id'] = row[0]
        user_choose['choose_date'] = row[1]
        user_choose['choose_time_id'] = row[2]
        event_time_user.append(user_choose)

        check = False
        for usr in user_vote:
            if usr == row[0]:
                check = True
                break
        if check == False:
            user_vote.append(row[0])
            voted_number += 1

    conn.close()

    return [event_id, event_time_result, event_time_user, voted_number]


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

    event_name = user_attribute[6]

    cur.execute("""
        INSERT INTO people VALUES ('%s', '%s', '%s', '%s', %s, %s, '%s');
    """ % (user_id, user_name, event_id, group_id, done, must_attend, event_name))

    conn.commit()
    conn.close()


def arbitrate_first(event_id):
    '''
        This function arbitrates an event first time.
        Input:
            event_id: string
        Output:
            arbitrate_result: list, [{'date':__, 'time_id':__, 'absent_user':__, 'voted_number':__, 'present_user':__},...,{}]
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()
    cur.execute("""
        SELECT choose.user_id, choose_date, choose_time_id, event_id FROM choose
        INNER JOIN (SELECT user_id FROM people
                    WHERE event_id = '%s'
                    AND must_attend = True
                    AND done = True) AS attend
        ON choose.user_id = attend.user_id
        WHERE event_id = '%s';
    """ % (event_id, event_id))

    rows = cur.fetchall()
    result = []
    for row in rows:
        find = False
        for re in result:
            if re['choose_date'] == row[1] and re['choose_time_id'] == row[2]:
                re['count'] += 1
                find = True
        if find == False:
            time_section = {}
            time_section['choose_date'] = row[1]
            time_section['choose_time_id'] = row[2]
            time_section['count'] = 1
            result.append(time_section)

    total_must_attend_user = 0
    user_list = []
    for row in rows:
        check = False
        for usr in user_list:
            if row[0] == usr:
                check = True
                break
        if check == False:
            user_list.append(row[0])
            total_must_attend_user += 1

    cur.execute("""
        SELECT user_id FROM people
        WHERE event_id = '%s';
    """ % (event_id))

    rows = cur.fetchall()
    total_user = 0
    user_vote = []
    for row in rows:
        check = False
        for usr in user_vote:
            if usr == row[0]:
                check = True
                break
        if check == False:
            user_vote.append(row[0])
            total_user += 1

    ordered_result = sorted(result, key=itemgetter('count'), reverse=True)

    if len(ordered_result) == 0:
        return [{'date': '', 'time_id': -1, 'absent_user': [], 'voted_number':0, 'present_user':[]}]

    if ordered_result[0]['count'] < total_must_attend_user / 2:
        conn.commit()
        conn.close()
        return [{'date': '', 'time_id': -1, 'absent_user': [], 'voted_number':0, 'present_user':[]}]
    else:
        if ordered_result[0]['count'] == total_user:
            max_time_slot = []
            for ore in ordered_result:
                if ore['count'] == ordered_result[0]['count']:
                    max_time_slot.append(ore)
            ordered_max_time_slot = sorted(
                max_time_slot, key=itemgetter('choose_time_id', 'choose_date'))

            cur.execute("""
                SELECT preference FROM event
                WHERE event_id = '%s';
            """ % (event_id))
            rows = cur.fetchall()
            prefer = ''
            for row in rows:
                prefer = row[0]

            arbitrate_result = []
            temp_time = {}
            if prefer == 'early':
                temp_time['date'] = str(
                    ordered_max_time_slot[0]['choose_date'])
                temp_time['time_id'] = ordered_max_time_slot[0]['choose_time_id']
            else:
                temp_time['date'] = str(
                    ordered_max_time_slot[-1]['choose_date'])
                temp_time['time_id'] = ordered_max_time_slot[-1]['choose_time_id']

            cur.execute("""
                SELECT count(distinct user_id) FROM choose
                WHERE choose_date = date '%s'
                AND choose_time_id = %s
                AND event_id = '%s';
            """ % (temp_time['date'], temp_time['time_id'], event_id))
            rows = cur.fetchall()
            voted_number = 0
            for row in rows:
                voted_number = row[0]
            temp_time['voted_number'] = voted_number

            cur.execute("""
                SELECT user_id, user_name FROM people
                WHERE event_id = '%s';
            """ % (event_id))
            rows = cur.fetchall()
            user_name = []
            for row in rows:
                user_name.append((row[0], row[1]))

            cur.execute("""
                SELECT DISTINCT user_id FROM choose
                WHERE event_id = '%s'
                AND choose_date = date '%s'
                AND choose_time_id = %s;
            """ % (event_id, temp_time['date'], temp_time['time_id']))
            rows = cur.fetchall()
            present_user = []
            for row in rows:
                present_user.append(row[0])

            present_user_name = []
            for pre in present_user:
                for un in user_name:
                    if pre == un[0]:
                        present_user_name.append(un[1])
            temp_time['present_user'] = present_user_name

            temp_time['absent_user'] = []

            conn.commit()
            conn.close()

            arbitrate_result.append(temp_time)

            return arbitrate_result
        else:
            cur.execute("""
                SELECT preference FROM event
                WHERE event_id = '%s';
            """ % (event_id))
            rows = cur.fetchall()
            prefer = ''
            for row in rows:
                prefer = row[0]

            ordered_time_slot = ordered_result
            if prefer == 'late':
                ordered_time_slot = sorted(
                    ordered_result, key=lambda k: (-k['count'], -k['choose_time_id'], k['choose_date']))

            arbitrate_result = []
            for ots in ordered_time_slot:
                temp_time = {}
                temp_time['date'] = str(ots['choose_date'])
                temp_time['time_id'] = ots['choose_time_id']

                cur.execute("""
                    SELECT DISTINCT user_id FROM choose
                    WHERE event_id = '%s'
                    AND choose_date = date '%s'
                    AND choose_time_id = %s;
                """ % (event_id, temp_time['date'], temp_time['time_id']))
                rows = cur.fetchall()
                present_user = []
                for row in rows:
                    present_user.append(row[0])

                cur.execute("""
                    SELECT user_id, user_name FROM people
                    WHERE event_id = '%s';
                """ % (event_id))
                rows = cur.fetchall()
                all_user = []
                user_name = []
                for row in rows:
                    all_user.append(row[0])
                    user_name.append((row[0], row[1]))

                absent_user = []
                for au in all_user:
                    pre = False
                    for pu in present_user:
                        if au == pu:
                            pre = True
                            break
                    if pre == False:
                        for un in user_name:
                            if au == un[0]:
                                absent_user.append(un[1])
                                break
                temp_time['absent_user'] = absent_user

                present_user_name = []
                for pre in present_user:
                    for un in user_name:
                        if pre == un[0]:
                            present_user_name.append(un[1])
                temp_time['present_user'] = present_user_name

                cur.execute("""
                    SELECT count(distinct user_id) FROM choose
                    WHERE choose_date = date '%s'
                    AND choose_time_id = %s
                    AND event_id = '%s';
                """ % (temp_time['date'], temp_time['time_id'], event_id))
                rows = cur.fetchall()
                voted_number = 0
                for row in rows:
                    voted_number = row[0]
                temp_time['voted_number'] = voted_number

                arbitrate_result.append(temp_time)

                if len(arbitrate_result) == 3:
                    break

    conn.commit()
    conn.close()

    return arbitrate_result


def arbitrate_second(event_id, first_result):
    '''
        This function arbitrates an event second time.
        Input:
            event_id: string
            first_result: list
        Output:
            arbitrate_result: list, [{'date':__, 'time_id':__, 'absent_user':__, 'voted_number':__, 'present_user':__}]
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT choose.user_id, choose_date, choose_time_id, event_id FROM choose
        INNER JOIN (SELECT user_id FROM people
                    WHERE event_id = '%s'
                    AND must_attend = True
                    AND done = True) AS attend
        ON choose.user_id = attend.user_id
        WHERE event_id = '%s';
    """ % (event_id, event_id))

    result = []
    for fre in first_result:
        result.append(
            {'choose_date': fre['date'], 'choose_time_id': fre['time_id'], 'count': 0})

    rows = cur.fetchall()
    for row in rows:
        for re in result:
            if re['choose_date'] == str(row[1]) and re['choose_time_id'] == row[2]:
                re['count'] += 1

    total_must_attend_user = 0
    user_list = []
    for row in rows:
        check = False
        for usr in user_list:
            if row[0] == usr:
                check = True
                break
        if check == False:
            user_list.append(row[0])
            total_must_attend_user += 1

    cur.execute("""
        SELECT user_id FROM people
        WHERE event_id = '%s';
    """ % (event_id))

    rows = cur.fetchall()
    total_user = 0
    user_vote = []
    for row in rows:
        check = False
        for usr in user_vote:
            if usr == row[0]:
                check = True
                break
        if check == False:
            user_vote.append(row[0])
            total_user += 1

    ordered_result = sorted(result, key=itemgetter('count'), reverse=True)

    if len(ordered_result) == 0:
        return [{'date': '', 'time_id': -1, 'absent_user': [], 'voted_number':0, 'present_user':[]}]

    most_count = []
    for i in range(len(ordered_result)):
        if ordered_result[i]['count'] == ordered_result[0]['count']:
            most_count.append(ordered_result[i])
    ordered_time_slot = sorted(
        most_count, key=itemgetter('choose_time_id', 'choose_date'))

    arbitrate_result = []
    cur.execute("""
        SELECT preference FROM event
        WHERE event_id = '%s';
    """ % (event_id))
    rows = cur.fetchall()
    prefer = ''
    for row in rows:
        prefer = row[0]

    temp_time = {}
    if prefer == 'early':
        temp_time['date'] = str(ordered_time_slot[0]['choose_date'])
        temp_time['time_id'] = ordered_time_slot[0]['choose_time_id']
    else:
        temp_time['date'] = str(ordered_time_slot[-1]['choose_date'])
        temp_time['time_id'] = ordered_time_slot[-1]['choose_time_id']

    cur.execute("""
        SELECT DISTINCT user_id FROM choose
        WHERE event_id = '%s'
        AND choose_date = date '%s'
        AND choose_time_id = %s;
    """ % (event_id, temp_time['date'], temp_time['time_id']))
    rows = cur.fetchall()
    present_user = []
    for row in rows:
        present_user.append(row[0])

    cur.execute("""
        SELECT user_id, user_name FROM people
        WHERE event_id = '%s';
    """ % (event_id))
    rows = cur.fetchall()
    all_user = []
    user_name = []
    for row in rows:
        all_user.append(row[0])
        user_name.append((row[0], row[1]))

    absent_user = []
    for au in all_user:
        pre = False
        for pu in present_user:
            if au == pu:
                pre = True
                break
        if pre == False:
            for un in user_name:
                if au == un[0]:
                    absent_user.append(un[1])
                    break
    temp_time['absent_user'] = absent_user

    present_user_name = []
    for pre in present_user:
        for un in user_name:
            if pre == un[0]:
                present_user_name.append(un[1])
    temp_time['present_user'] = present_user_name

    cur.execute("""
        SELECT count(distinct user_id) FROM choose
        WHERE choose_date = date '%s'
        AND choose_time_id = %s
        AND event_id = '%s';
    """ % (temp_time['date'], temp_time['time_id'], event_id))
    rows = cur.fetchall()
    voted_number = 0
    for row in rows:
        voted_number = row[0]
    temp_time['voted_number'] = voted_number

    arbitrate_result.append(temp_time)

    conn.commit()
    conn.close()

    return arbitrate_result


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
        event_attribute['dead'] = row[12]

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
        event_attribute['group_id'] = row[11]

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


def get_already_vote(event_id):
    '''
        This function returns people who have voted an event.
        Input:
            event_id: string
        Output:
            result: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_name FROM people
        WHERE event_id = '%s'
        AND done = True;
    """ % (event_id))

    result = []
    rows = cur.fetchall()
    for row in rows:
        result.append(row[0])

    conn.commit()
    conn.close()

    return result


def insert_member(user_id, user_name, group_id):
    '''
        This function inserts user into table member_list.
        Input:
            user_id: string
            user_name: string
            group_id: string
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO member_list VALUES ('%s', '%s', '%s');
        """ % (user_id, user_name, group_id))
    except:
        pass

    conn.commit()
    conn.close()


def get_members(group_id):
    '''
        This function returns members of a group.
        Input:
            group_id: string
        Output:
            member_list: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, user_name FROM member_list
        WHERE group_id = '%s';
    """ % (group_id))

    member_list = []
    rows = cur.fetchall()
    for row in rows:
        member = []
        member.append(row[0])
        member.append(row[1])
        member_list.append(member)

    conn.commit()
    conn.close()

    return member_list


def init_member_list():
    '''
        This function initialize table member_list.
    '''
    insert_member(user1_id, user1_name, user1_group_id)
    insert_member(user2_id, user2_name, user2_group_id)
    insert_member(user3_id, user3_name, user3_group_id)


def not_yet_vote(event_id):
    '''
        This function returns the numbers of people that not yet voted of an event.
        Input:
            event_id: string
        Output:
            no_vote_result: dict, {'no_vote_count':__, 'no_vote_people':__}
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT count(user_id) FROM people
        WHERE event_id = '%s'
        AND done = False;
    """ % (event_id))

    no_vote_result = {}
    rows = cur.fetchall()
    no_vote_count = int()
    for row in rows:
        no_vote_count = int(row[0])

    no_vote_result['no_vote_count'] = no_vote_count

    cur.execute("""
        SELECT user_id FROM people
        WHERE event_id = '%s'
        AND done = False;
    """ % (event_id))

    rows = cur.fetchall()
    no_vote_people = []
    for row in rows:
        no_vote_people.append(row[0])

    no_vote_result['no_vote_people'] = no_vote_people

    conn.commit()
    conn.close()

    return no_vote_result


def get_user_attribute(user_id, event_id):
    '''
        This function returns user's attribute of a given user_id.
        Input:
            user_id: string
        Output:
            user_attribute: dict, {'user_name':__, 'group_id':__, 'done':__, 'must_attend':__}
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_name, group_id, done, must_attend FROM people
        WHERE user_id = '%s'
        AND event_id = '%s';
    """ % (user_id, event_id))

    rows = cur.fetchall()
    user_attribute = {}
    for row in rows:
        user_attribute['user_name'] = row[0]
        user_attribute['group_id'] = row[1]
        user_attribute['done'] = row[2]
        user_attribute['must_attend'] = row[3]

    conn.commit()
    conn.close()

    return user_attribute


def get_event_dead(event_id):
    '''
        This function returns whether an event is dead.
        Input:
            event_id: string
        Output:
            dead: bool
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT dead FROM event
        WHERE event_id = '%s';
    """ % (event_id))

    rows = cur.fetchall()
    dead = rows[0][0]

    conn.close()

    return dead


def get_time(time_id):
    '''
        This function returns time_start and time_end of a time_id.
        Input:
            time_id: int
        Output:
            time_duration: list, [time_start, time_end]
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        SELECT time_start, time_end FROM time
        WHERE time_id = '%s';
    """ % (time_id))

    rows = cur.fetchall()
    time_duration = [rows[0][0], rows[0][1]]

    conn.commit()
    conn.close()

    return time_duration


def settle(event_id, event_name, group_id):
    '''
        This function arbitrates the result one time and returns arbitrated result.
        Input:
            event_id: string
            event_name: string
            group_id: string
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()
    cur.execute("""
        UPDATE event SET dead = True
        WHERE event_id = '%s'
    """ % (event_id))
    conn.commit()
    conn.close()

    result = arbitrate_first(event_id)
    print(result, len(result))
    if len(result) == 1:
        result_date = result[0]["date"]
        result_time = get_time(result[0]["time_id"])
        start_time = result_time[0].strftime("%H:%M")
        end_time = result_time[1].strftime("%H:%M")
        userstr = ""
        for i in get_already_vote(event_id):
            userstr += i + "\n"
        FlexMessage = json.load(
            open('normal_result.json', 'r', encoding='utf-8'))
        FlexMessage["body"]["contents"][1]["contents"][0]["contents"][1]["text"] = parse.unquote(event_name)
        FlexMessage["body"]["contents"][1]["contents"][1]["contents"][1]["text"] = result_date + \
            "\n" + start_time + "～" + end_time
        FlexMessage["body"]["contents"][1]["contents"][2]["contents"][1]["text"] = userstr
        FlexMessage["footer"]["contents"][0]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/display_result?event_id=" + event_id
        line_bot_api.push_message(
            group_id, FlexSendMessage('Scheduling Bot', FlexMessage))
    else:
        FlexMessage = json.load(open('judge.json', 'r', encoding='utf-8'))
        absent_set = []
        FlexMessage["body"]["contents"][1]["contents"][0]["text"] = "「" + parse.unquote(event_name) + "」\n目前最高票3個時段依序是："
        for i in range(3):
            FlexMessage["body"]["contents"][1]["contents"][i + 1]["contents"][1]["text"] = result[i]["date"] + "\n" + \
                get_time(result[i]["time_id"])[0].strftime("%H:%M") + "～" + get_time(result[i]["time_id"])[
                1].strftime("%H:%M") + "\n參與人數共 " + str(result[i]["voted_number"]) + " 人"
            for j in result[i]["absent_user"]:
                absent_set.append(j)
        absent_set = set(absent_set)
        members = ""
        for i in absent_set:
            members += "@" + i + " "
        FlexMessage["body"]["contents"][1]["contents"][4]["text"] = "請 " + \
            members + "針對以上時段再次確認是否能夠參與此活動！"
        FlexMessage["footer"]["contents"][0]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/vote?event_id=" + event_id
        FlexMessage["footer"]["contents"][1]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/display_result?event_id=" + event_id
        FlexMessage["footer"]["contents"][2]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/second_settle?event_id=" + \
            event_id + "&event_name=" + parse.quote(event_name) + "&group_id=" + group_id
        print("settle:")
        print(FlexMessage)
        line_bot_api.push_message(
            group_id, FlexSendMessage('Scheduling Bot', FlexMessage))


def check_and_end(time_date_now):
    '''
        This function demonstrate the final time slot of an event.
        Input:
            time_date_now: list
    '''
    conn = psycopg2.connect(database=database, user=user,
                            password=password, host=host, port=port)
    cur = conn.cursor()

    time_now = time_date_now[1]
    date_now = time_date_now[0]

    cur.execute("""
        SELECT event_id, event_name, group_id FROM event
        WHERE time '%s' >= deadline_time
        AND date '%s' = deadline_date
        AND dead = False;
    """ % (time_now, date_now))

    rows = cur.fetchall()
    conn.commit()
    conn.close()

    for row in rows:
        event_id = row[0]
        event_name = row[1]
        group_id = row[2]
        settle(event_id, event_name, group_id)


def test(event_id):
    #event_id = "3HyCHqhc"
    #event_name = "asgfasdfsadf"
    #group_id = "C36e166f739d14fffbd20c0ce7c772eef"
    result = arbitrate_first(event_id)
    print(result, len(result))
    result = arbitrate_second(event_id, result)
    print(result, len(result))
    """FlexMessage = json.load(open('judge.json', 'r', encoding='utf-8'))
    absent_set = []
    # for i in range(3):
    FlexMessage["body"]["contents"][1]["contents"][1]["contents"][1]["text"] = result[0]["date"] + " " + \
        get_time(result[0]["time_id"])[0].strftime("%H:%M") + \
        "\n參與人數共 " + str(result[0]["voted_number"]) + " 人"
    for j in result[0]["absent_user"]:
        absent_set.append(j)
    FlexMessage["body"]["contents"][1]["contents"][2]["contents"][1]["text"] = result[1]["date"] + " " + \
        get_time(result[1]["time_id"])[0].strftime("%H:%M") + \
        "\n參與人數共 " + str(result[1]["voted_number"]) + " 人"
    for j in result[1]["absent_user"]:
        absent_set.append(j)
    FlexMessage["body"]["contents"][1]["contents"][3]["contents"][1]["text"] = result[2]["date"] + " " + \
        get_time(result[2]["time_id"])[0].strftime("%H:%M") + \
        "\n參與人數共 " + str(result[2]["voted_number"]) + " 人"
    for j in result[2]["absent_user"]:
        absent_set.append(j)
    absent_set = set(absent_set)
    members = ""
    for i in absent_set:
        members += "@" + i + " "
    FlexMessage["body"]["contents"][1]["contents"][4]["text"] = "請 " + \
        members + "針對以上時段再次確認是否能夠參與此活動！"
    FlexMessage["footer"]["contents"][0]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/vote?event_id=" + event_id
    FlexMessage["footer"]["contents"][1]["action"]["uri"] = "https://scheduling-line-bot.herokuapp.com/display_result?event_id=" + event_id
    line_bot_api.push_message(
        group_id, FlexSendMessage('Scheduling Bot', FlexMessage))"""


test("ijBGaxjV")
