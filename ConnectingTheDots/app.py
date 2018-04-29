from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, make_response
#from data import Articles
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import os
from flask_socketio import SocketIO, send, emit

#Make directory
#basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "TheBestCSCI3308"
manager = Manager(app)
users = {}
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

#Config SQL ALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#class Role(db.Model):
#	__tablename__ = 'roles'
#	id = db.Column(db.Integer, primary_key=True)
#	name = db.Column(db.String(64), unique=True)
#	#Provides a relationship one to many role to users
#	users = db.relationship('User', backref='role')
#
#	#Give string representation for debugging
#	def __repr__(self):
#		return '<Role %r' % self.name

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True, index=True)
	#Provide Role to the user
	#role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

	def __repr__(self):
		return '<User %r' % self.name

db.create_all()
#db.relationship() defines the reverse direction of the relationship
#useful to use instead of role_id


#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'toor'
app.config['MYSQL_DB'] = 'TheBest'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

#Articles = Articles()

#HomePage
@app.route('/')
def index():
	#user_agent = request.headers.get('User-Agent')
	#return '<p> Browser is %s</p>' %user_agent
	return render_template('home.html')

# About
@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/articles')
def articles():
	# Create Cursor
	cur = mysql.connection.cursor()

	#Get Articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()
	username=session['username']

	if result > 0:
		return render_template('articles.html', articles=articles, username=username)
	else:
		msg = 'No Articles Found'
		return render_template('articles.html', msg=msg, username=username)

	#Close Connection
	cur.close()

#Single Article
@app.route('/article/<string:id>/')
def article(id):
	# Create Cursor
	cur = mysql.connection.cursor()

	#Get Article
	result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

	article = cur.fetchone()
	username=session['username']

	return render_template('article.html', article=article, username=username)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		username = request.form['username']
		confirm = sha256_crypt.encrypt(str(request.form['confirm']))
		
		#Create Cursor
		cur = mysql.connection.cursor()

		#Excute query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name, email, username, confirm))

		#Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('You are now registered and can log in', 'success')

		return redirect(url_for('login'))
	return render_template('register.html')
 

#User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# Get Form Fields
		username = request.form['username']
		# Get the actual password
		password_candidate = request.form['password']

		# Create Cursor
		cur = mysql.connection.cursor()

		# Get Select username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		if result > 0:
			# Get stored hash value
			data = cur.fetchone()
			password = data['password']

			# Compare passwords
			if sha256_crypt.verify(password_candidate, password):
				#Password accepted
				session['logged_in'] = True
				session['username'] = username
				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))
			else:
				error = 'Invalid login'
				return render_template('login.html', error=error)
			# Close connection
			cur.close()
		else:
			error = 'Invalid login'
			return render_template('login.html', error=error)
	return render_template('login.html')

#Check if user logged in
def is_logged_in(f):
	@wraps(f)
	#capture input agruments and use them for function
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap

#Logout
@app.route('/logout')
@is_logged_in
def logout():
	del users[session['username']]
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@app.route('/dashboard/<string:username1>')
@is_logged_in
def dashboard(username1=None):

	# if request.method == 'POST':
	# 	username = request.form['username1']
	# 	message = request.form['message']
	# 	cur = mysql.connection.cursor()
	# 	cur.execute("INSERT INTO messages(username1, username2, message) VALUES(%s, %s, %s)", (session['username'], username, message))

	# 	mysql.connection.commit()

	# 	#Close connection
	# 	cur.close()
	cur = mysql.connection.cursor()
	username = session['username']
	result = cur.execute("SELECT username from users where name != %s", [username])
	data = cur.fetchall()
	usernames = []
	for names in data:
		if names['username'] != session['username']:
			usernames.append(names['username'])
	#get messages and sort them by order they were sent
	if(username1 == None):
		cur.execute("SELECT * from messages where username1 = %s and username2 = %s", (username, usernames[0]))
		messages = cur.fetchall()
		cur.execute("SELECT * from messages where username1 = %s and username2 = %s", (usernames[0], username))
		messages += cur.fetchall()
		messages = sorted(messages, key=lambda i:i['id'])
		convo = usernames[0]
	else :
		cur.execute("SELECT * from messages where username1 = %s and username2 = %s", (username, username1))
		messages = cur.fetchall()
		cur.execute("SELECT * from messages where username1 = %s and username2 = %s", (username1, username))
		messages += cur.fetchall()
		messages = sorted(messages, key=lambda i:i['id'])
		convo = username1
	return render_template('dashboard.html', usernames=usernames, username=username, convo=convo, messages=messages, users=users)
	
@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():
	username = session['username']
	cur = mysql.connection.cursor()
	cur.execute("SELECT email, name, register_date from users where username = %s", [username])
	content = cur.fetchall()
	print(content)
	return render_template('userprofile.html', content=content, username=username)

# Article Form Class
class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min = 1, max = 200)])
	body = TextAreaField('Body', [validators.Length(min = 30)])

#Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
	
	username = session['username']
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']

		# Create Cursor
		cur = mysql.connection.cursor()

		#Execute
		cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

		# Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('Article Created', 'success')

		return redirect(url_for('articles'))

	return render_template('add_article.html', username=username)

#Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
	# Create Cursor
	cur = mysql.connection.cursor()

	#Get the article by ID
	result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

	article = cur.fetchone()

	#Get Form
	form = ArticleForm(request.form)

	#Populate article form fields
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		# Create Cursor
		cur = mysql.connection.cursor()

		#Execute
		cur.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))

		# Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('Article Updated', 'success')

		return redirect(url_for('dashboard'))

	return render_template('edit_article.html', form=form)

#Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
	#Create Cursor
	cur = mysql.connection.cursor()

	# Execute
	cur.execute("DELETE FROM articles WHERE id = %s", [id])

	# Commit to DB
	mysql.connection.commit()

	#Close connection
	cur.close()

	flash('Article Deleted', 'success')

	return redirect(url_for('dashboard'))

# @socketio.on('username', namespace='/private')
# def receive_username(username):
#     users[username] = request.sid
    #users.append({username : request.sid})
@socketio.on('connected')
def receove_connect(username):
   users[username] = request.sid
   #users.append({username : request.sid})

@socketio.on('private_message', namespace='/private')
def private_message(payload):
	message = payload['message']
	
	username = payload['username']
	cur = mysql.connection.cursor()
	cur.execute("INSERT INTO messages(username1, username2, message) VALUES(%s, %s, %s)", (payload['sentname'], username, message))

	mysql.connection.commit()

		#Close connection
	cur.close()
	recipient_session_id = users[payload['username']]

	emit('new_private_message', username, room=recipient_session_id, broadcast=True)

if __name__ == '__main__':
	#app.secret_key = os.environ.get('SECRET_KEY')
	app.secret_key='secret123'
	manager.run()
	socketio.run(app)