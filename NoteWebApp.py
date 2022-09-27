import sqlite3

from flask import Flask, request, session
#from flask.ext.session import Session

app = Flask(__name__)

#Used for cryptographically-sign the cookies used for storing the session data. For production use the secret key should be a random string of text.
app.secret_key = 'BAD_SECRET_KEY'

#SESSION_TYPE = 'redis'
#app.config.from_object(__name__)
#Session(app)

DATABASE = 'db/dbfile.db'

def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = sqlite3.connect(DATABASE)
    return db

def create_note(inputData):
	dbconn=get_db()
	cur = dbconn.cursor()
	cur.execute(''' insert into notes (title,note) values(?,?) ''', inputData)
	dbconn.commit()
	return "done"

def update_note(inputData, args=(), one=False):
	dbconn=get_db()
	cur = dbconn.cursor()
	cur.execute(''' update notes SET title=?,note=? where id=? ''', inputData)
	dbconn.commit()
	return "done"

def get_note(inputData, args=(), one=False):
	dbconn=get_db()
	cur=dbconn.cursor()
	result=cur.execute(''' select * from notes where id=? ''', inputData).fetchall()
	dbconn.commit()
	return (result)

def delete_note(inputData, args=(), one=False):
	dbconn=get_db()
	cur=dbconn.cursor()
	result=cur.execute(''' delete note where id=? ''', inputData).fetchall()
	dbconn.commit()
	return (result)

htmlstart='<!DOCTYPE html><html><head><title>Notes in the Cloud</title></head><body>'
htmlend='</body></html>'

noteform='<form action="/TEMPACTION" method="post"><label for="title">TEMPTITLE</label><input name="title" id="title" value=""><textarea name="note" id="note"></textarea><input type="submit" value="Create note"></form>'

@app.route("/")
def index():
	print(session)
	if "uname" in session:
		indexform=noteform.replace('TEMPACTION','create')
		indexform=indexform.replace('TEMPTITLE','New Note')
		return htmlstart+""+indexform+htmlend
	else:
		return htmlstart+'<form action="/login" method="post"><table><tr><td><lable for="uname">Username:</td><td><input name="uname" id="uname"></td></tr><tr><td><lable for="pword">Password:</td><td><input name="pword" id="pword"></td></tr><tr><td></td><td><input type="submit" value="Log in"></td></tr></table></form>'+htmlend
		

@app.route("/login")
def login():
	
    return htmlstart+""+htmlend

@app.route("/note")
def note():
    indexform=noteform.replace('TEMPACTION','create')
    indexform=indexform.replace('TEMPTITLE','New Note')
    return htmlstart+"<p>Hello, World!</p>"+indexform+htmlend

@app.route("/note/<note_id>")
def readnote(note_id):
	theNote=get_note(note_id)
	indexform=noteform.replace('TEMPACTION','update/'+note_id)
	indexform=indexform.replace('TEMPTITLE','Note: ')
	indexform=indexform.replace('id="title" value="','id="title" value="'+theNote[0][2])
	indexform=indexform.replace('</textarea>',theNote[0][3]+'</textarea>')
	return htmlstart+"<p>Hello, World!</p>"+indexform+htmlend

@app.route("/create", methods=['POST', 'GET'])
def createnote():
	print(request.form)
	if request.method == 'POST':
		inputData=[request.form.get('title'),request.form.get('note')]
		create_note(inputData);
	return "<p>Hello, World!</p>"

@app.route("/update/<note_id>", methods=['POST', 'GET'])
def updatenote(note_id):
	print(request.form)
	if request.method == 'POST':
		inputData=[request.form.get('title'),request.form.get('note'),note_id]
		update_note(inputData);
	return "<p>Hello, World!</p>"

@app.route("/delete/<note_id>", methods=['POST', 'GET'])
def deletenote(note_id):
	print(request.form)
	if request.method == 'POST':
		inputData=[note_id]
		update_note(inputData)
	return "<p>Hello, World!</p>"
