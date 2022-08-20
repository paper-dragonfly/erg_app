from logic import db_connect
import pdb

def create_erg_db():
    conn, cur = db_connect('create_dbs', True)
    cur.execute("SELECT datname FROM pg_database")
    db_list = cur.fetchall()
    if ('Erg',) in db_list:
        print('db exists')
    else:
        cur.execute("""CREATE DATABASE Erg""")
    cur.close()
    conn.close()


def create_test_db():
    conn, cur = db_connect('create_dbs', True)
    cur.execute("SELECT datname FROM pg_database")
    db_list = cur.fetchall()
    # pdb.set_trace()
    if ('erg_test',) in db_list:
        print('erg_tests db already exists')
    else:
        cur.execute("""CREATE DATABASE erg_test""")
    cur.close()
    conn.close()


def create_team_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS team(
        team_id SERIAL PRIMARY KEY,
        team_name VARCHAR(50) 
        ) """)


def create_users_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id SERIAL PRIMARY KEY,
        user_name VARCHAR(25) NOT NULL,
        age INTEGER,
        sex VARCHAR(1),
        team INTEGER,
        FOREIGN KEY (team) REFERENCES team(team_id)
        )""")
    

def create_workout_log_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS workout_log(
        workout_id SERIAL PRIMARY KEY,
        user_id INTEGER, 
        date DATE,
        distance INTEGER,
        time_sec INTEGER,
        split INTEGER,
        intervals INTEGER,
        comment VARCHAR(255),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""")


def create_interval_log_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS interval_log(
        interval_id SERIAL PRIMARY KEY,
        workout_id INTEGER,
        interval_type VARCHAR(10), 
        distance INTEGER,
        time_sec INTEGER,
        split INTEGER,
        rest INTEGER,
        FOREIGN KEY (workout_id) REFERENCES workout_log(workout_id))"""
    )


def initialize(db):
    try:
        conn, cur = db_connect(db,True)
        create_team_table(cur)
        create_users_table(cur)
        create_workout_log_table(cur)
        create_interval_log_table(cur) 
    finally:
        conn.close()
        cur.close()


if __name__ == "__main__":
    create_erg_db()
    create_test_db()
    initialize('erg')
    initialize('testing') 

