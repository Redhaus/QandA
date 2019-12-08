from flask import g
import sqlite3

# connect to sql db
def connect_db():
    # provide db path
    sql = sqlite3.connect('/Users/redbook/PycharmProjects/QandA/questions.db')
    # set return to be dict
    sql.row_factory = sqlite3.Row

    return sql

# adds connect_db to global name space for easy access
def get_db():
    # if not on global namespace it adds it
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    # opens a connection to db everytime it is called
    return g.sqlite_db
