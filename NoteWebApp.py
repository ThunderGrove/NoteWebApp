import sqlite3

from flask import Flask

app = Flask(__name__)

DATABASE = '/db/dbfile.db'

def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = sqlite3.connect(DATABASE)
        db.execute('CREATE TABLE notes(id INT PRIMARY KEY NOT NULL,title TEXT PRIMARY KEY,note TEXT PRIMARY KEY')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(Flask, '_database', None)
    if db is not None:
        db.close()

htmlstart='<!DOCTYPE html><html><head><title>Notes in the Cloud</title></head><body>'
htmlend='</body></html>'

noteform='<form action="/TEMPACTION" method="post"><label for="title" value="">TEMPTITLE</label><input name="title" id="title"><textarea name="note" id="note"></textarea><input type="submit" value="Create note"></form>'

@app.route("/")
def index():
    indexform=noteform.replace('TEMPACTION','create')
    indexform=indexform.replace('TEMPTITLE','New Note')
    return htmlstart+"<p>Hello, World!</p>"+indexform+htmlend

@app.route("/create", methods=['POST', 'GET'])
def create():
    return "<p>Hello, World!</p>"
