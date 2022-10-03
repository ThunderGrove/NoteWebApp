import sqlite3

#Requires Python module Flask and Flask-session.
from flask import Flask, request, session

app = Flask(__name__)

#Used for cryptographically-sign the cookies used for storing the session data. For production use the secret key should be a random string of text.
app.secret_key = 'BAD_SECRET_KEY'

#Path to SQLite db file
DATABASE = 'db/dbfile.db'

#Finds and loads SQLite db file.
def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = sqlite3.connect(DATABASE)
    return db

#Creates a note in db.
def create_note(inputData):
	dbconn=get_db()
	cur = dbconn.cursor()
	cur.execute(''' insert into notes (title,note) values(?,?) ''', inputData)
	dbconn.commit()
	return "done"

#Get a user in db.
def get_user(inputData, args=(), one=True):
	dbconn=get_db()
	cur=dbconn.cursor()
	result=cur.execute(''' select * from users where uname="?" ''', inputData).fetchone()
	dbconn.commit()
	return (result)

#Creates a user in db.
def create_user(inputData):
	dbconn=get_db()
	cur = dbconn.cursor()
	cur.execute(''' insert into users (uname,password,name) values(?,?,?) ''', inputData)
	dbconn.commit()
	return "done"

#Update a note in db.
def update_note(inputData, args=(), one=False):
	dbconn=get_db()
	cur = dbconn.cursor()
	cur.execute(''' update notes SET title=?,note=? where id=? ''', inputData)
	dbconn.commit()
	return "done"

#Get a note in db.
def get_note(inputData, args=(), one=False):
	dbconn=get_db()
	cur=dbconn.cursor()
	result=cur.execute(''' select * from notes where id=? ''', inputData).fetchall()
	dbconn.commit()
	return (result)

#Delete a note in db.
def delete_note(inputData, args=(), one=False):
	dbconn=get_db()
	cur=dbconn.cursor()
	result=cur.execute(''' delete note where id=? ''', inputData).fetchall()
	dbconn.commit()
	return (result)

#Contains base HTML used on all pages.
htmlstart='<!DOCTYPE html><html><head><title>Notes in the Cloud</title><style>*{margin:0;padding:0;}#banner{background:#222;height:5vh;color:#ddd;font-size:2vh;}#banner a{color:#ddd;}#main{display:block;background:#ddd;height:95vh;width:100vw}</style></head><body>'
htmlend='</body></html>'

noteform='<div id="main"><form action="/TEMPACTION" method="post"><label for="title">TEMPTITLE</label><input name="title" id="title" value=""><textarea name="note" id="note"></textarea><input type="submit" value="Create note"></form></div>'

#Code to generate topbanner
def generateBanner():
	bannercode='<div id=banner>'
	if "uname" in session:
		bannercode=bannercode+'User name: '+session['name']
	else:
		bannercode=bannercode+'<a href="/cUser">Create user</a>'
	bannercode=bannercode+'</div>'
	return bannercode

#Frontpage
@app.route("/")
def index():
	print(session)
	if "uname" in session:
		indexform=noteform.replace('TEMPACTION','create')
		indexform=indexform.replace('TEMPTITLE','New Note')
		return htmlstart+generateBanner()+indexform+htmlend
	else:
		return htmlstart+generateBanner()+'<div id="main"><form action="/login" method="post"><table><tr><td><lable for="uname">Username:</td><td><input name="uname" id="uname"></td></tr><tr><td><lable for="pword">Password:</td><td><input name="pword" id="pword"></td></tr><tr><td></td><td><input type="submit" value="Log in"></td></tr></table></form></div>'+htmlend
		
#Login
@app.route("/login", methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		postedUname=[request.form.get('uname')]
		user=get_user(postedUname)
		if user[2]==str(hash(request.form.get('pword')+"salt")):
			session['id']=user[0]
			session['uname']=user[1]
			session['name']=user[3]
	return htmlstart+generateBanner()+htmlend

#Create User
@app.route("/cUser")
def createUser():
    return htmlstart+generateBanner()+'<div id="main"><form action="/cUserBackend" method="post"><table><tr><td><lable for="uname">Username:</td><td><input name="uname" id="uname"></td></tr><tr><td><lable for="pword">Password:</td><td><input name="pword" id="pword"></td></tr><tr><td><lable for="pword2">Password again:</td><td><input name="pword2" id="pword2"></td></tr><tr><td></td><td><input type="submit" value="Create user"></td></tr></table></form></div>'+htmlend

#Create note page
@app.route("/note")
def note():
    indexform=noteform.replace('TEMPACTION','create')
    indexform=indexform.replace('TEMPTITLE','New Note')
    return htmlstart+generateBanner()+indexform+htmlend

#Show a note page
@app.route("/note/<note_id>")
def readnote(note_id):
	theNote=get_note(note_id)
	indexform=noteform.replace('TEMPACTION','update/'+note_id)
	indexform=indexform.replace('TEMPTITLE','Note: ')
	indexform=indexform.replace('id="title" value="','id="title" value="'+theNote[0][2])
	indexform=indexform.replace('</textarea>',theNote[0][3]+'</textarea>')
	return htmlstart+generateBanner()+indexform+htmlend

#Create a user process
@app.route("/cUserBackend", methods=['POST', 'GET'])
def createUserBackend():
	print(request.form)
	if request.method == 'POST':
		if request.form.get('pword')==request.form.get('pword2'):
			inputData=[request.form.get('uname'),str(hash(request.form.get('pword')+"salt")),request.form.get('uname')]
			create_user(inputData);
			user=get_user(request.form.get('uname'))
			print(user)
			session['id']=user[0]
			session['uname']=user[1]
			session['name']=user[3]
			return '<p>User made</p>'
	return "<p>Failed to make user</p>"

#Create a note process
@app.route("/create", methods=['POST', 'GET'])
def createnote():
	print(request.form)
	if request.method == 'POST':
		inputData=[request.form.get('title'),request.form.get('note')]
		create_note(inputData);
	return "<p>Hello, World!</p>"

#Update a note process
@app.route("/update/<note_id>", methods=['POST', 'GET'])
def updatenote(note_id):
	print(request.form)
	if request.method == 'POST':
		inputData=[request.form.get('title'),request.form.get('note'),note_id]
		update_note(inputData);
	return "<p>Hello, World!</p>"

#Delete a note process
@app.route("/delete/<note_id>", methods=['POST', 'GET'])
def deletenote(note_id):
	print(request.form)
	if request.method == 'POST':
		inputData=[note_id]
		update_note(inputData)
	return "<p>Hello, World!</p>"
