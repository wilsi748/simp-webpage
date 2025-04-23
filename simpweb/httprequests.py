import telnetlib
import json
import requests
from requests.structures import CaseInsensitiveDict


headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["Authorization"] = ""



sign_up_data = json.dumps(json.loads('{ "email" : "willesid@gmail.com", "password" : "tjena", "firstname" : "William","familyname" : "Sid","gender" : "Male","city" : "Linkoping","country" : "Sweden"}'))

sign_in_data = json.dumps(json.loads('{ "email" : "willesid@gmail.com","password" : "tjena"} '))




def test_request_sign_up(url, data):
    response = requests.put(url, headers=headers, data=data)
    print(response.status_code)
    print(response.text)

def test_request_sign_in(url, data):
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    
    
def test_sign_in_out(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)

    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token

    response = requests.delete(url2, headers=headers, data={})
    print(response.status_code)
    print(response.text)

def test_change_password(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    change_password_data ='{ "old_password" : "tjena", "new_password" : "hejhej" }'
    data_dict = json.loads(change_password_data)
    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token
    response = requests.post(url2, headers=headers, data=json.dumps(data_dict))
    print(response.status_code)
    print(response.text)

    # Testa logga in med gamla lösenordet
    test_request_sign_in("http://127.0.0.1:5000/signin", sign_in_data)

    change_password_data ='{ "old_password" : "hejhej", "new_password" : "tjena" }'
    data_dict = json.loads(change_password_data)

    response = requests.post(url2, headers=headers, data=json.dumps(data_dict))
    print(response.status_code)
    print(response.text)

def test_get_userdata_by_token(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token

    response = requests.get(url2, headers=headers, data={})
    print(response.status_code)
    print(response.text)

def test_get_userdata_by_token(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token

    response = requests.get(url2, headers=headers, data={})
    print(response.status_code)
    print(response.text)

def test_get_userdata_by_email(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token
    response = requests.get(url2, headers=headers, data={})
    print(response.status_code)
    print(response.text)

def test_get_messages_by_token(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token
    response = requests.get(url2, headers=headers, data={})
    print(response.status_code)
    print(response.text)

def test_get_messages_by_email(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token
    response = requests.get(url2, headers=headers, data={})
    print(response.status_code)
    print(response.text)

def test_post_message(url1, url2, data):
    response = requests.post(url1, headers=headers, data=data)
    print(response.status_code)
    print(response.text)

    message_data ='{ "sender" : "willesid@gmail.com","message" : "Hej Wille Från Wille", "receiver" : "willesid@gmail.com"}'
    data_dict = json.loads(message_data)

    json_resp = response.json()
    headers["Authorization"] = json_resp["data"] #hämta token

    response = requests.post(url2, headers=headers, data=json.dumps(data_dict))
    print(response.status_code)
    print(response.text)



test_request_sign_up("http://127.0.0.1:5000/signup", sign_up_data)
test_request_sign_in("http://127.0.0.1:5000/signin", sign_in_data)
test_change_password("http://127.0.0.1:5000/signin", "http://127.0.0.1:5000/changepassword", sign_in_data)
test_sign_in_out("http://127.0.0.1:5000/signin", "http://127.0.0.1:5000/signout", sign_in_data)
test_get_userdata_by_token("http://127.0.0.1:5000/signin","http://127.0.0.1:5000/getdatabytoken/", sign_in_data)
test_get_userdata_by_email("http://127.0.0.1:5000/signin","http://127.0.0.1:5000/getdatabyemail/willesid@gmail.com", sign_in_data)
test_post_message("http://127.0.0.1:5000/signin", "http://127.0.0.1:5000/postmessage", sign_in_data)
test_get_messages_by_token("http://127.0.0.1:5000/signin","http://127.0.0.1:5000/getusermessagesbytoken/", sign_in_data)
test_get_messages_by_email("http://127.0.0.1:5000/signin","http://127.0.0.1:5000/getusermessagesbyemail/willesid@gmail.com", sign_in_data)

########################################################

host = "127.0.0.1"
port = "5000"
tn = telnetlib.Telnet(host, port, timeout = 5)

post_request_sign_up = b"""POST /signup/ HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json
Content-Length: 196

{ 
    \"email\" : \"willesid@gmail.com\",
    \"password\" : \"tjena\", 
    \"firstname\" : \"William\",
    \"familyname\" : \"Sid\",
    \"gender\" : \"Male\",
    \"city\" : \"Linkoping\",
    \"country\" : \"Sweden\"
}
"""

post_request_sign_in = b"""POST /signin/ HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json
Content-Length: 65

{ 
    "email" : "willesid@gmail.com",
    "password" : "tjena"
}
"""

post_request_sign_out = b"""POST /signout/ HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json
"""

def telnet_test_request():
    tn.write(post_request_sign_up)
    response = tn.read_all()
    print(response)
