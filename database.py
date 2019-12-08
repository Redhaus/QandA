# database.py

from flask import g
import sqlite3

# import lib to convert between python and postgres
import psycopg2

# extra to allow data returned as dict instead of tuples
from psycopg2.extras import DictCursor


def connect_db():
    # create connection provide path and make return as dict
    # conn = psycopg2.connect(uri, cursor_factory=DictCursor)
    conn = psycopg2.connect(
        'postgres://bxogjpgehibbwc:6d7eb4ca464df53aec6fd958a3fa2e744e07d868148163f230347a3922c26a8c@ec2-174-129-255-76.compute-1.amazonaws.com:5432/d5lmk2tvthtj79',
        cursor_factory=DictCursor)

    # set autocommit to true so you don't have to commit all changes'
    # connection obj & cursor obj are separate in postgres
    # The commit is on the connection in postgres
    # But you run queries on the cursor
    # Setting autocommit to true means it will commit everytime you do something
    conn.autocommit = True

    # create connection to run queries on the cursor
    sql = conn.cursor()

    # return tuple of both the conn=connection and the sql=cursor
    return conn, sql


def get_db():
    db = connect_db()

    # db connection
    # if not on global namespace it adds connection to it
    # create connection on global var db[0] = conn in tuple above

    if not hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn = db[0]

    # db Cursor
    # create connection on global var db[1] = sql in tuple above

    if not hasattr(g, 'postgres_db_cur'):
        g.postgres_db_cur = db[1]

    # connection there but not work with it directly because it auto commits

    return g.postgres_db_cur


# initialize function to create tables and db schema
def init_db():
    db = connect_db()

    # on the sql cursor execute schema query by reading sql file
    db[1].execute(open('schema.sql', 'r').read())
    db[1].close()  # close cursor

    db[0].close()  # close connection


def init_admin():
    db = connect_db()

    db[1].execute('update users set admin = True where name = %s', ('admin',))

    db[1].close()
    db[0].close()

# OLD SQL Code


# SQLLITE3 EG
# # connect to sql db
# def connect_db():
#     # provide db path
#     sql = sqlite3.connect('/Users/redbook/PycharmProjects/QandA/questions.db')
#     # set return to be dict
#     sql.row_factory = sqlite3.Row
#
#     return sql
#
# # adds connect_db to global name space for easy access
# def get_db():
#     # if not on global namespace it adds it
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = connect_db()
#     # opens a connection to db everytime it is called
#     return g.sqlite_db


