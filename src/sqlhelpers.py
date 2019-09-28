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

def get_show_code(conn, values):
    '''
    returns show code
    :param connection:
    :param values - project id and user id:
    '''
    sql ='''SELECT 
                project_code, 
                project_name 
            FROM 
                projects 
            WHERE 
                project_id = ? 
            AND 
                user_id = ?'''
    
    cur = conn.cursor()

    cur.execute(sql, values)
    
    rows = cur.fetchall()

    show_code = rows[0][0]
    
    return show_code


def get_show_name(conn, values):
    '''
    returns show name
    :param connection:
    :param values - project id, user id: 
    '''

    sql ='''SELECT 
                project_code, 
                project_name 
            FROM 
                projects 
            WHERE 
                project_id = ? 
            AND 
                user_id = ?''' 

    cur = conn.cursor()

    cur.execute(sql, values)

    rows = cur.fetchall()

    show_name = rows[0][1]

    return show_name


def get_distro(conn, distro, values):
    """Get distro list for dailies email.

    Arguments:
        conn {string} -- Database connection
        distro {string} -- Dailies email
        values {string} -- Project ID

    Returns:
        string -- A list of emails for selected dailies email.
    """
    
    sql =f'''SELECT
                email
            FROM
                crew
            WHERE
                project_id = ?
            AND
                {distro} = 1'''
    
    cur = conn.cursor()

    cur.execute(sql, values)

    rows = cur.fetchall()

    crew = ''
    for item in rows:
        crew += item[0] + " "

    return crew