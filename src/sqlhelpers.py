import sqlite3
import sys

def create_connection(db_file):
    ''' create a connection to SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    '''

    conn = None

    try:
        conn = sqlite3.connect(db_file)
    except IOError as io:
        print(io)
    except:
        print("Unexpected error")

    return conn


def update_break(conn, task):
    '''
    Update master media, shoot day
    :param conn:
    :param task:
    :return: project id
    '''

    sql ='''UPDATE latest_media
            SET camera_masters = ?,
                sound_masters = ?,
                shoot_day = ?
            WHERE project_id = ?
            AND break = ?'''

    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()


def create_break(conn, values):
    '''
    create row in  
    ''' 
    sql ='''INSERT INTO
                latest media
            VALUES
                (?,?,?,?,?)'''
    
    cur = conn.cursor()

    cur.execute(sql, values)
    cur.commit()
