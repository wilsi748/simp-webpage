#This file shall contain all the server side remote procedures, implemented using Python and Flask.
from gevent import monkey
monkey.patch_all()
from flask import Flask, jsonify, request
import database_helper
import re
import secrets
import json
from flask_sock import Sock
from gevent.pywsgi import WSGIServer
from flask_bcrypt import Bcrypt
import hashlib, hmac

app = Flask(__name__)
sockets = Sock(app)
bcrypt = Bcrypt(app)

#secret key
app.secret_key = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf'

regex_email = '^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$'

curr_sockets = {}


@app.route("/")
def root():
    database_helper.init_db(app)
    return app.send_static_file('client.html')

@sockets.route("/websocket")
def socket(ws):
    message = ws.receive()
    data = json.loads(message)
    email = data["email"]
    # Check if this user already has a socket connection
    if email in curr_sockets.keys():
        # If so, close that socket connection
        try:
            curr_sockets[email].send(json.dumps({"message" : "logout"}))
            print("logging out user from other login")
        except:
            print("websocket closed due to reload")
        
        del curr_sockets[email]

    # Save this new socket connection
    curr_sockets[email] = ws

    while True:
        # Listen to the client
        message = ws.receive()
        # Socket connection has been closed
        if message == "close":
            # User is no longer logged in
            break

@app.route("/signin/", methods = ["POST"])
def sign_in():
    json = request.get_json() 
    if not json:
        return jsonify({"success": False, "message": "No json was recieved", "data": {}}), 400 
    if not json["email"] or not json["password"]:
        return jsonify({"success": False, "message": "No email or password was entered", "data": {}}), 400  # Bad input kan va 422 eventuellt om man vill
    
    email = json["email"]
    password = json["password"]
    
    if validate_email(email) and password != "":
        user = database_helper.find_user_by_email(email)
        if user:
            token = database_helper.get_token_by_email(email)
            if token:
                print("removing already logged in user from table")
                database_helper.remove_logged_in_user(token)
            hashed_password = database_helper.get_hashed_password_by_email(email)
            token = secrets.token_hex(16)
            if bcrypt.check_password_hash(hashed_password, password) and database_helper.add_logged_in_user(token, email):
                app.logger.info("logging in")
                return jsonify({"success": True, "message": "Logged in!", "data": token}), 200
            return jsonify({"success": False, "message": "Wrong password", "data": {}}), 401
        return jsonify({"success": False, "message": "No user found", "data": {}}), 404
    return jsonify({"success": False, "message": "Invalid email or password", "data": {}}), 400 # Bad input kan va 422 eventuellt om man vill

@app.route("/signup/", methods = ["POST"])
def sign_up():
    json = request.get_json()
    if not json:
        return jsonify({"success": False, "message": "No json was recieved", "data": {}}), 400
    if not json["email"]:
        return jsonify({"success": False, "message": "No email was entered", "data": {}}), 400  # Bad input kan va 422 eventuellt om man vill
    email = json["email"]
    if database_helper.find_user_by_email(email):
        return jsonify({"success": False, "message": "User already exists", "data": {}}), 409
    if not validate_user_input(json):
        return jsonify({"success": False, "message": "Invalid user input", "data": {}}), 400
    password = json["password"]
    hashed_password = bcrypt.generate_password_hash(password, 10)
    json["password"] = hashed_password
    if database_helper.add_user(json):
        return jsonify({"success": True, "message": "User has been created!", "data": {}}), 201
    return jsonify({"success": False, "message": "Unable to create user", "data": {}}), 500


@app.route("/signout/", methods = ["POST"])
def sign_out():
    hashdata = request.headers.get("hashdata")
    if not request.json:
        return jsonify({"success": False, "message": "No json was recieved", "data": {}}), 400
    if not request.json["email"]:
        return jsonify({"success": False, "message": "No email was sent", "data": {}}), 400
    email = request.json['email']
    token = database_helper.get_token_by_email(email)
    serverhash = server_hash_function(email, email)
    if(hashdata == serverhash):
        if database_helper.remove_logged_in_user(token):
            del curr_sockets[email]
            app.logger.info("logging out")
            return jsonify({"success": True, "message": "User has successfully logged out", "data": {}}), 200
        return jsonify({"success": False, "message": "User is not signed in", "data": {}}), 401
    return jsonify({"success": False, "message": "Couldnt authenticate", "data": {}}), 401
    

@app.route("/changepassword/", methods = ["POST"])
def change_password():
    json = request.get_json()
    if not json:
        return jsonify({"success": False, "message": "No json was recieved", "data": {}}), 400
    if not json["old_password"] or not json["new_password"] or not json["email"]:
        return jsonify({"success": False, "message": "No password or email was sent", "data": {}}), 400
    hashdata = request.headers.get("hashdata")
    email = json['email']
    old_password = json["old_password"]
    new_password = json["new_password"]
    data = email + new_password + old_password
    serverhashdata = server_hash_function(data, email)
    if hashdata == serverhashdata:
        hashed_password = database_helper.get_hashed_password_by_email(email)
        if bcrypt.check_password_hash(hashed_password, old_password):
            if validate_password(new_password):
                new_hashed_password = bcrypt.generate_password_hash(new_password)
                user = database_helper.find_user_by_email(email)
                if user:
                    if database_helper.change_password(user[0], hashed_password, new_hashed_password):
                        return jsonify({"success": True, "message": "Password has been changed", "data": {}}), 200
                    return jsonify({"success": False, "message": "Changing password has failed", "data": {}}), 500
                return jsonify({"success": False, "message": "No user found", "data": {}}), 404
            return jsonify({"success": False, "message": "Invalid new password", "data": {}}), 400
        return jsonify({"success": False, "message": "Wrong old password", "data": {}}), 401 # 400, 422 vet inte riktigt, tog 401 för att de är fel input
    return jsonify({"success": False, "message": "Couldnt Authenticate", "data": {}}), 401

@app.route("/getdatabytoken/", methods = ["POST"])
def get_user_data_by_token():
    hashdata = request.headers.get("hashdata")
    if not request.json["email"]:
        return jsonify({"success": False, "message": "User is not signed in", "data": {}}), 401
    email = request.json["email"]
    server_hash_data = server_hash_function(email, email)
    if hashdata == server_hash_data:
        user = database_helper.find_user_by_email(email)
        if user:
            userdata = { "email" : user[0], "firstname" : user[2], "familyname" : user[3], "gender" : user[4], "city" : user[5], "country" : user[6] }
            return jsonify({"success" : True, "message" : "user data has been found", "data" : userdata})
        return jsonify({"success": False, "message": "User was not found", "data": {}}), 500
    return jsonify({"success": False, "message": "User is not signed in", "data": {}}), 401
    

@app.route("/getdatabyemail/", methods = ["POST"])
def get_user_data_by_email():
    hashdata = request.headers.get("hashdata")
    if not request.json["email"] or not request.json["to_email"]:
        return jsonify({"success": False, "message": "No json was sent", "data": {}}), 400
    email = request.json["email"]
    to_email = request.json["to_email"]
    serverhash = server_hash_function(email+to_email, email)
    if serverhash == hashdata:
        user = database_helper.find_user_by_email(to_email)
        if user:
            userdata = { "email" : user[0], "firstname" : user[2], "familyname" : user[3], "gender" : user[4], "city" : user[5], "country" : user[6]}
            return jsonify({"success" : True, "message" : "user data has been found", "data" : userdata}), 200
        return jsonify({"success": False, "message": "User was not found", "data": {}}), 500
    return jsonify({"success": False, "message": "Unable to authenticate", "data": {}}), 401
    

@app.route("/getusermessagesbytoken/", methods = ["POST"])
def get_user_messages_by_token():
    hashdata = request.headers.get("hashdata")
    if not request.json["email"]:
        return jsonify({"success": False, "message": "No json was sent", "data": {}}), 400
    email = request.json["email"]
    serverhash = server_hash_function(email, email)
    if serverhash == hashdata:
        messages = database_helper.get_user_messages_by_email(email)
        if messages:
            messageData = {"messages" : []}
            for msg in messages:
                messageData["messages"].append({"sender" : msg[0], "message" : msg[1], "receiver" : msg[2], "timestamp" : msg[3]})
            return jsonify({"success" : True, "message" : "message for user has been found", "data" : messageData}), 200
        return jsonify({"success": False, "message": "No messages was found", "data": {}}), 204
    return jsonify({"success": False, "message": "User is not signed in", "data": {}}), 401


@app.route("/getusermessagesbyemail/", methods = ["POST"])
def get_user_messages_by_email():
    hashdata = request.headers.get("hashdata")
    if not request.json["email"] or not request.json["to_email"]:
        return jsonify({"success": False, "message": "No json was sent", "data": {}}), 400
    email = request.json["email"]
    to_email = request.json["to_email"]
    if to_email != "" and not validate_email(to_email):
        return jsonify({"success": False, "message": "Incorrect email", "data": {}}), 400
    serverhash = server_hash_function(email+to_email, email)
    if serverhash == hashdata:
        if database_helper.find_user_by_email(to_email):
            messages = database_helper.get_user_messages_by_email(to_email)
            if messages:
                messageData = {"messages" : []}
                for msg in messages:
                    messageData["messages"].append({"sender" : msg[0], "message" : msg[1], "receiver" : msg[2], "timestamp" : msg[3]})
                return jsonify({"success" : True, "message" : "message for user has been found", "data" : messageData}), 200
            return jsonify({"success": False, "message": "No messages was found", "data": {}}), 204
        return jsonify({"success": False, "message": "User was not found", "data": {}}), 500
    return jsonify({"success": False, "message": "Unable to authenticate", "data": {}}), 401
    

@app.route("/postmessage/", methods = ["POST"])
def post_message():
    json = request.get_json()
    if not json:
        return jsonify({"success": False, "message": "No json was sent", "data": {}}), 400
    if not json["sender"] or not json["message"] or not json["receiver"]:
        return jsonify({"success": False, "message": "No sender, message or receiver was sent", "data": {}}), 400
    hashdata = request.headers.get("hashdata")
    serverhash = server_hash_function(json["sender"] + json["receiver"] + json["message"], json["sender"])
    if serverhash == hashdata:
        if validate_email(json["sender"]) and validate_email(json["receiver"]) and json["message"] != "":
            if database_helper.find_user_by_email(json["receiver"]):
                if database_helper.post_message(json["sender"], json["message"], json["receiver"]):
                    return jsonify({"success" : True, "message" : "message has been posted", "data" : {}}), 201
                return jsonify({"success" : False, "message" : "was not able to post message", "data" : {}}), 500
            return jsonify({"success" : False, "message" : "was not able to find user", "data" : {}}), 400
        return jsonify({"success" : False, "message" : "invalid input", "data" : {}}), 400
    
    return jsonify({"success" : False, "message" : "Unable to authenticate", "data" : {}}), 401


def validate_email(email):
    return re.search(regex_email, email)

def validate_password(password):
    return password != "" and 100 > len(password) > 4 

def validate_user_input(json):
    if validate_email(json["email"]) and validate_password(json["password"]) and json["firstname"] != "" and json["familyname"] != "" and json["gender"] != "" and json["city"] != "" and json["country"] != "":
        return True
    return False

def server_hash_function(data, email):
    # key - token
    # data - message to hash
    token = database_helper.get_token_by_email(email)
    hash_str = hashlib.sha256((data + token).encode('utf-8')).hexdigest()
    return hash_str

if __name__ == '__main__':
    app.debug = True
    WSGIServer(('', 5000), app).serve_forever()