#Basic libs used.
import sqlite3
import redis #Needed for storing storing sessions in memory instead of as a cookie in client Webbrowser or as file on the server (that may end up not been deleted)

#The build in hash function does not return the same result from the same value between runs.
import hashlib

#Requires Python module Flask and Flask-session.
from flask import Flask, request, session
from flask_session import Session

app = Flask(__name__)

#Config for get serverside sessions to work.
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:5000')

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
	cur.execute(''' insert into notes (title,note,ownerid,key,IV) values(?,?,?,?,?) ''', inputData)
	dbconn.commit()
	return "done"

#Get a user in db.
def get_user(inputData, args=(), one=True):
	dbconn=get_db()
	cur=dbconn.cursor()
	#Note: Do not use quotes around the ? char.
	result=cur.execute(''' select * from users where uname=? ''', inputData).fetchone()
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
	cur.execute(''' update notes SET title=?,note=?,ownerid=?,key=?,IV=? where id=? ''', inputData)
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
htmlstart='<!DOCTYPE html><html><head><title>Notes in the Cloud</title><style>*{margin:0;padding:0;}#banner{background:#222;height:5vh;color:#ddd;font-size:2vh;}#banner a{color:#ddd;}#main{display:block;background:#ddd;height:95vh;width:100vw}</style></head><body><script>function getMsgEncoding(){var msgBox=document.getElementById("note").value;var msg=msgBox.value;var enc=new TextEncoder();return enc.encode(msg);}async function encode(){var encoded=getMsgEncoding();var iv=window.crypto.getRandomValues(new Uint8Array(16));document.getElementById("iv").value=iv;var key=await window.crypto.subtle.generateKey({name:"AES-CBC",length:256},true,["encrypt","decrypt"]);var exported=await window.crypto.subtle.exportKey("raw",key);var exportedKeyBuffer=new Uint8Array(exported);document.getElementById("key").value=exportedKeyBuffer;var result=await window.crypto.subtle.encrypt({name:"AES-CBC",iv:iv},key,encoded);var decoder=new TextDecoder("utf-8");var cipherTextRaw=decoder.decode(result);var buffer=new Uint8Array(result);var cipherTextArr=`${buffer}...[${result.byteLength} bytes total]`;	document.getElementById("note").value=buffer;}async function decode(){var msg=document.getElementById("note").value;var key=Array.from(document.getElementById("key").value);var iv=document.getElementById("iv").value;iv=Array.from(iv);var uArray=new Uint8Array([...msg].map((char)=>char.charCodeAt(0)));var algorithm={name:"AES-GCM",iv:iv,};alert(Array.from(document.getElementById("key").value));var imported=window.crypto.subtle.importKey("raw",key,"AES-GCM",true,["encrypt","decrypt"]);var decryptedData=await window.crypto.subtle.decrypt(algorithm,imported,uArray);alert("Yes");document.getElementById("note").value=new TextDecoder().decode(decryptedData);}</script>'
htmlend='</body></html>'

noteform='<div id="main"><form action="/TEMPACTION" method="post" id="noteform"><label for="title">TEMPTITLE</label><input name="title" id="title" value=""><textarea name="note" id="note"></textarea><input type="hidden" name="key" id="key" value=""><input type="hidden" name="iv" id="iv" value=""><input type="button" onclick="encode()" value="Create note"></form></div>'

#Code to generate topbanner
def generateBanner():
	bannercode='<div id="banner">'
	print(session)
	if 'uname' in session:
		bannercode=bannercode+'User name: '+session['name']
	else:
		bannercode=bannercode+'<a href="/cUser">Create user</a>'
	bannercode=bannercode+'</div>'
	return bannercode

#Frontpage
@app.route("/")
def index():
	print(session)
	if 'uname' in session:
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
		pwordsalt=request.form.get('pword')+"salt"
		pwordsalt=pwordsalt.encode()
		print(user[2]+" - "+hashlib.sha512(pwordsalt).hexdigest())
		if user[2]==hashlib.sha512(pwordsalt).hexdigest():
			session['id']=user[0]
			session['uname']=user[1]
			session['name']=user[3]
		print(session)
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
			pwordsalt=request.form.get('pword')+"salt"
			pwordsalt=pwordsalt.encode()
			inputData=[request.form.get('uname'),hashlib.sha512(pwordsalt).hexdigest(),request.form.get('uname')]
			create_user(inputData);
			user=get_user(request.form.get('uname'))
			session['id']=user[0]
			session['uname']=user[1]
			session['name']=user[3]
			return '<p>User made</p>'
	return "<p>Failed to make user</p>"

#Create a note process
@app.route("/create", methods=['POST', 'GET'])
def createnote():
	print(request.form.get('iv'))
	if request.method == 'POST':
		inputData=[request.form.get('title'),request.form.get('note'),session['id'],request.form.get('key'),request.form.get('iv')]
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
