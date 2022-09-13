import sqlite3

from flask import Flask, request
#from os.path

app = Flask(__name__)

DATABASE = 'db/dbfile.db'

def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        #if os.path.exists(DATABASE)
        db = Flask._database = sqlite3.connect(DATABASE)
        #db.execute('CREATE TABLE notes(id INT PRIMARY KEY NOT NULL,title TEXT PRIMARY KEY,note TEXT PRIMARY KEY')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(Flask, '_database', None)
    if db is not None:
        db.close()

def create_note(query):
    cur = get_db().execute(query)
    cur.close()
    return "done"

def get_note(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

htmlstart='<!DOCTYPE html><html><head><title>Notes in the Cloud</title></head><body>'
htmlend='</body></html>'

noteform='<form action="/TEMPACTION" method="post"><label for="title" >TEMPTITLE</label><input name="title" id="title" value=""><textarea name="note" id="note"></textarea><input type="submit" value="Create note"></form>'

@app.route("/")
def index():
    indexform=noteform.replace('TEMPACTION','create')
    indexform=indexform.replace('TEMPTITLE','New Note')
    return htmlstart+"<p>Hello, World!</p>"+indexform+htmlend

@app.route("/note/<note_id>")
def readnote(note_id):
    print(get_note("select * from notes where id="+note_id+";"))
    #indexform=noteform.replace('TEMPACTION','create')
    #indexform=indexform.replace('TEMPTITLE','New Note')
    return htmlstart+"<p>Hello, World!</p>"+noteform+htmlend

@app.route("/create", methods=['POST', 'GET'])
def create():
    print(request.form)
    if request.method == 'POST':
        create_note('insert into notes (title,note) values("'+request.form.get('title')+'","'+request.form.get('note')+'");');
    return "<p>Hello, World!</p>"
