DROP TABLE IF EXISTS loggedin;

CREATE TABLE IF NOT EXISTS user (
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    firstname TEXT NOT NULL,
    familyname TEXT NOT NULL,
    gender TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    PRIMARY KEY (email)
);

CREATE TABLE IF NOT EXISTS message(
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    receiver TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender) REFERENCES user (email) ON DELETE CASCADE,
    FOREIGN KEY (receiver) REFERENCES user (email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS loggedin(
    token TEXT NOT NULL PRIMARY KEY,
    email TEXT NOT NULL,
    FOREIGN KEY (email) REFERENCES user (email) ON DELETE CASCADE
);