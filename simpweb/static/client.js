displayView = function(view) {
    document.getElementById("current-view").innerHTML = view.innerHTML;
};

window.onload = function() {
    welcomeView = document.getElementById("welcome-view");
    profileView = document.getElementById("profile-view");
    displayView(welcomeView);
};

function connectSocket() {
    console.log("creating socket connection");
    
    const websocket = new WebSocket("ws://"+location.host+"/websocket");
    console.log("websocket ", websocket)

    let token = localStorage.getItem("token");
    let email = localStorage.getItem("email");
    
    websocket.addEventListener('open', event => {
        console.log("Websocket connection open");
        let data = { "token" : token, "email" : email };
        websocket.send(JSON.stringify(data));
    });
    
    websocket.addEventListener('close', event => {
        console.log("Event " + event.code);
        console.log('WebSocket connection closed');
    });

    websocket.addEventListener('error', event => {
        console.error('WebSocket error', event);
    });

    websocket.addEventListener('message', event => {
        data = JSON.parse(event.data);
        if(data.message == "logout") {
            websocket.send("close")
            localStorage.removeItem("token");
            displayView(welcomeView);
        }
        if(data.message == "close") {
            websocket.send("close")
        }
    });
}

function signup() {
    let errorDiv = document.getElementById("error-message-signup");
    let email = document.forms["signup-form"]["email"].value;
    let password = document.forms["signup-form"]["password"].value;
    let passwordRepeat = document.forms["signup-form"]["repeat-password"].value;
    let fname = document.forms["signup-form"]["firstname"].value;
    let lname = document.forms["signup-form"]["familyname"].value;
    let gender = document.forms["signup-form"]["gender"].value;
    let city = document.forms["signup-form"]["city"].value;
    let country = document.forms["signup-form"]["country"].value;

    if(fname == "" || lname == "" || gender == "" || city == "" || country == "") {
        errorDiv.innerHTML = "Must enter all fields";
        return false;
    }

    if(!validateEmail(email)) {
        errorDiv.innerHTML = "Invalid email";
        return false;
    }

    if (password.length <= 5) {
        console.log("Lösenordet är för kort");
        errorDiv.innerHTML = "Password is too short";
        return false;
    }

    if(password !== passwordRepeat) {
        console.log("Matchar inte passwords");
        errorDiv.innerHTML = "Password do not match";
        return false;
    }

    let user = {
        'email' : email,
        'password' : password,
        'firstname' : fname,
        'familyname' : lname,
        'gender' : gender,
        'city' : city,
        'country' : country
    };

    let request = new XMLHttpRequest();
    request.open("POST", "/signup/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    
    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(request.responseText);
            if (this.status == 201) {
                // Göra något här?
                errorDiv.innerHTML = response.message;
            } else {
                errorDiv.innerHTML = response.message;
            }
        }
    }
    request.send(JSON.stringify(user));
}

const valid_email = new RegExp(/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/);
function validateEmail(email){
    if (!email.match(valid_email)){
        return false;
    }
    return true;
}

function login() {
    let errorDiv = document.getElementById("error-message-login");
    let email = document.forms["login-form"]["email"].value;
    let pass = document.forms["login-form"]["password"].value;
    
    let request = new XMLHttpRequest();
    request.open("POST", "/signin/", true)
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    request.onreadystatechange = function() {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if(this.status == 200) {
                let token = response.data;
                console.log("token:" + token);
                localStorage.setItem("email", email);
                localStorage.setItem("token", token);
                connectSocket();
                displayView(profileView);
                changeTab("home");
                setupProfile();
                updateMessagesHome();
            }
            errorDiv.innerHTML = response.message;
        } 
    };
    request.send(JSON.stringify({ "email": email, "password": pass}));
    
}

function logout() {
    let token = localStorage.getItem("token");
    let email = localStorage.getItem("email")
    let errorDiv = document.getElementById("error-message");
    let request = new XMLHttpRequest();
    request.open("POST", "/signout/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(email, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText)
            if (this.status == 200) {
                localStorage.removeItem("token");
                localStorage.removeItem("email");
                displayView(welcomeView);
                console.log(response.message);
            } else {
                errorDiv.innerHTML(response.message);
                console.log(response.message);
            }
        }
    }
    
    request.send(JSON.stringify({"email" : email}));
    return false;
}

function changePassword() {
    let errorDiv = document.getElementById("error-message-account");
    let oldPassword = document.forms["change-password-form"]["old-password"].value;
    let newPassword = document.forms["change-password-form"]["new-password"].value;
    let repeatNewPassword = document.forms["change-password-form"]["repeat-new-password"].value;
    let token = localStorage.getItem("token");
    let email = localStorage.getItem("email");

    if(newPassword < 5) {
        errorDiv.innerHTML = "Password is too short";
        return false;
    }

    if(newPassword !== repeatNewPassword) {
        errorDiv.innerHTML = "Password does not match";
        return false;
    }

    let request = new XMLHttpRequest();
    request.open("POST", "/changepassword/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(email + newPassword + oldPassword, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if (this.status == 200) {
                console.log("changed password");
                errorDiv.innerHTML = response.message;
            } 
            errorDiv.innerHTML = response.message;
        }
    }
    request.send(JSON.stringify({"email" : email, "old_password" : oldPassword, "new_password" : newPassword }));
}


function changeTab(tab) {
    let view = document.getElementsByClassName("profile-content");
    for(let i = 0; i < view.length; i++) {
        view[i].style.display = "none";
    }
    let buttons = document.getElementsByClassName("tab-button");
    for(let i = 0; i < buttons.length; i++) {
        buttons[i].style.backgroundColor = "";
    }

    document.getElementById(tab).style.display = "block";
    document.getElementById(tab + "-tab").style.backgroundColor = "lightblue";
}

function setupProfile() {
    let token = localStorage.getItem("token");
    let email = localStorage.getItem("email");
    let request = new XMLHttpRequest();
    request.open("POST", "/getdatabytoken/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(email, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if (this.status == 200) {
                setUpRightSide(response.data);
            }
            console.log(response.message)
        }
    }
    request.send(JSON.stringify({"email" : email}));
}

function setUpRightSide(data) {
    document.getElementById("userName").innerHTML = data.firstname + " " + data.familyname
    document.getElementById("userGender").innerHTML = data.gender
    document.getElementById("userCity").innerHTML = data.city
    document.getElementById("userCountry").innerHTML = data.country
    document.getElementById("userEmail").innerHTML = data.email
}

function sendMessageHome() {
    console.log("twiddar home");
    let msg = document.forms["home-message"]["message"].value;
    let token = localStorage.getItem("token");
    let email = localStorage.getItem("email");
    let request = new XMLHttpRequest();
    request.open("POST", "/postmessage/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(email + email + msg, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if (this.status == 201) {
                document.forms["home-message"]["message"].value = "";
                updateMessagesHome();
            } 
        }
    }
    request.send(JSON.stringify( { "sender" : email, "message" : msg, "receiver" : email } ));
}

function updateMessagesHome() {
    let token = localStorage.getItem("token");
    let email = localStorage.getItem("email");
    let request = new XMLHttpRequest();
    request.open("POST", "/getusermessagesbytoken/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(email, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if (this.status == 200) {
                let homeFeed = document.getElementById("twidds-home");
                homeFeed.innerHTML = "";
                createTwidds(token, response.data, homeFeed);
            }
            console.log(response.message);
        }
    }
    request.send(JSON.stringify({"email" : email}));
}

function sendMessageBrowse() {
    let token = localStorage.getItem("token");
    let sender = localStorage.getItem("email");
    let msg = document.forms["browse-message"]["message"].value;
    let receiver = document.forms["browse-from-visit-user"]["email"].value;
    let errorDiv = document.getElementById("error-message");
    
    if (!validateEmail(receiver)) {
        errorDiv.innerHTML = "Please enter a valid email!";
        return false;
    }
    
    let request = new XMLHttpRequest();
    request.open("POST", "/postmessage/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(sender + receiver + msg, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if (this.status == 201) {
                document.forms["home-message"]["message"].value = "";
                updateMessagesBrowse();
            } else {
                errorDiv.innerHTML = response.message;
            }
        }
    }
    request.send(JSON.stringify({"sender" : sender, "message" : msg, "receiver" : receiver}));
}

function updateMessagesBrowse() {
    let to_email = document.forms["browse-from-visit-user"]["email"].value;
    let email = localStorage.getItem("email");
    let token = localStorage.getItem("token");
    let request = new XMLHttpRequest();

    let errorDiv = document.getElementById("error-message");
    
    if (!validateEmail(to_email)) {
        errorDiv.innerHTML = "Please enter a valid email!";
        return false;
    }

    request.open("POST", "/getusermessagesbyemail/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(email + to_email, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if (this.status == 200) {
                let browseFeed = document.getElementById("twidds-browse");
                browseFeed.innerHTML = "";
                createTwidds(token, response.data, browseFeed);
            } else {
                errorDiv.innerHTML = response.message;
            }
        }
    }
    request.send(JSON.stringify({"email" : email, "to_email" : to_email}));
}

function getUserInfo() {
    let to_email = document.forms["browse-from-visit-user"]["email"].value;
    let email = localStorage.getItem("email");
    let token = localStorage.getItem("token");
    let request = new XMLHttpRequest();
    let errorDiv = document.getElementById("error-message");
    console.log("to " + to_email);
    if(!validateEmail(email)) {
        errorDiv.innerHTML = "Please enter a valid email!";
    }

    request.open("POST", "/getdatabyemail/", true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("hashdata", hash_function(email + to_email, token));

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            let response = JSON.parse(this.responseText);
            if (this.status == 200) {
                setUpRightSide(response.data);
            } else {
                errorDiv.innerHTML = response.message;
                console.log("hitta ej user data ");
            }
        }
    }
    request.send(JSON.stringify({"email" : email, "to_email" : to_email}));
    updateMessagesBrowse();
}


function createSlug(name, lastname) {
    return "@"+name+lastname;
}

function createTwidds(token, data, feed) {
    data["messages"].map(msg => 
        {
            let userdata;
            let req = new XMLHttpRequest();
            let email = localStorage.getItem("email");
            req.open("POST", "/getdatabyemail/", true);
            req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            console.log("token " + token);
            req.setRequestHeader("hashdata", hash_function(email + msg.sender, token));
            
            req.onreadystatechange = function() {
                if (this.readyState == 4) {
                    let response = JSON.parse(this.responseText);
                    if(this.status == 200) {
                        userdata = response.data;
                        let author_slug = createSlug(userdata["firstname"], userdata["familyname"]);
                        feed.innerHTML +=
                        '<div class="twidd">' + 
                        '<div class="twidd-header">' + 
                        '<div class="twidd-author-name">' + msg.sender + '</div>' +
                        '<div class="twidd-author-slug">' + author_slug + '</div>' +
                        '<div class="twidd-publish-time">' + msg.timestamp + '</div>' +
                        '</div>' +
                        '<div class="twidd-content">' + msg.message + '</div>' + 
                        '</div>';
                    }
                } 
            };
            req.send(JSON.stringify({"email" : email, "to_email" : msg.sender}));
        }
    );
}

function hash_function(data, token) {
    //key + message to hash
    let hash = sha256(data+token);
    return hash;
}