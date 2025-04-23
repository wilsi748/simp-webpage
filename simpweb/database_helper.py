#This file will contain all the functions that access and control the database and shall contain some SQL
#scripts. This file will be used by the server to access the database. This file shall NOT contain any
#domain functions like signin or signup and shall only contain data-centric functionality like
#find_user(), remove_user(), create_post() and … . E.g. Implementing sign_in() in server.py shall
#involve a call to find_user() implemented in database_helper.py .

import sqlite3
from flask import g

DATABASE_URI = 'database.db'

# g is a special object that is unique for each request. 
# It is used to store data that might be accessed by multiple functions during the request. 
# The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_URI)
    db.row_factory = sqlite3.Row
    return db

def sql_query(sql_string, data, one=False):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(sql_string, data)
    connection.commit()
    if not one:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()
    cursor.close()
    close_db()
    return result

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def add_user(json):
    user = [json["email"], json["password"], json["firstname"], json["familyname"], json["gender"], json["city"], json["country"]]
    sql_string = """INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?)"""
    try:
        sql_query(sql_string, user)
        return True
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
        return False

def find_user_by_email(email):
    sql_string = """SELECT * FROM user WHERE email = ?"""
    try:
        return sql_query(sql_string, [email], True)
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
        return False

def change_password(email, old_password, new_password):
    sql_string = """UPDATE user SET password = ? WHERE email = ? and password = ?"""
    try:
        sql_query(sql_string, [new_password, email, old_password])
        return True
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False

def get_user_messages_by_email(email):
    sql_string = """SELECT * FROM message WHERE receiver = ?"""
    try:
        return sql_query(sql_string, [email], False)
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False
    
def post_message(sender, message, receiver):
    sql_string = """INSERT INTO message (sender, message, receiver) VALUES (?, ?, ?)"""
    try:
        sql_query(sql_string, [sender, message, receiver])
        return True
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False
    
def get_hashed_password_by_email(email):
    sql_string = """SELECT password FROM user WHERE email = ?"""
    try:
        res = sql_query(sql_string, [email], True)
        return res[0]
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False
    
def add_logged_in_user(token, email):
    sql_string = """INSERT INTO loggedin VALUES (?, ?)"""
    try:
        sql_query(sql_string, [token, email])
        return True
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False
    
def remove_logged_in_user(token):
    sql_string = """SELECT email FROM loggedin WHERE token = ?"""
    try:
        res = sql_query(sql_string, [token])
        if res:
            sql_string = """DELETE FROM loggedin WHERE token = ?"""
            sql_query(sql_string, [token])
            return True
        return False
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False

def get_email_by_token(token):
    sql_string = """SELECT email FROM loggedin WHERE token = ?"""
    try:
        res = sql_query(sql_string, [token,], True)
        return res[0]
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False
    
def get_token_by_email(email):
    sql_string = """SELECT token FROM loggedin WHERE email = ?"""
    try:
        res = sql_query(sql_string, [email], False)
        if res:
            return res[0][0]
        return False
    except sqlite3.Error as error:
        print("Failed to input data from sqlite table", error)
        return False

