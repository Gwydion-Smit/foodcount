DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS RECIPES;

CREATE TABLE USERS (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT, carboncost FLOAT, carbonsaved FLOAT, history TEXT);

CREATE TABLE RECIPES (id INTEGER PRIMARY KEY AUTOINCREMENT, ingredients TEXT, carboncost FLOAT, carbonsaved FLOAT)

CREATE TABLE INGREDIENTS (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, name TEXT, userid integer FOREIGN KEY REFERENCES USERS(id))