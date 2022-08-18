import sqlite3


def db_connection():
    con = None
    try:
        con = sqlite3.connect('user.db')
    except Exception as e:
        print(e)
    return con
