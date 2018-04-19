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

#Make directory
#basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
manager = Manager(app)

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
app.config['MYSQL_PASSWORD'] = 'guest'
app.config['MYSQL_DB'] = 'ChatHelper'
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

	if result > 0:
		return render_template('articles.html', articles=articles)
	else:
		msg = 'No Articles Found'
		return render_template('articles.html', msg=msg)

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

	return render_template('article.html', article=article)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

# Register Form Class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min = 1, max = 50)])
	username = StringField('Username', [validators.Length(min = 4, max = 25)])
	email = StringField('Email', [validators.Length(min = 6, max = 50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match.')
		])
	confirm = PasswordField('Confirm Passord')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		#password = form.password.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#Create Cursor
		cur = mysql.connection.cursor()

		#Excute query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name, email, username, password))

		#Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('You are now registered and can log in', 'success')

		return redirect(url_for('login'))
	return render_template('register.html', form = form)

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
			error = 'Username not found'
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
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	# Create Cursor
	cur = mysql.connection.cursor()

	#Get Articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()

	if result > 0:
		return render_template('dashboard.html', articles=articles)
	else:
		msg = 'No Articles Found'
		return render_template('dashboard.html', msg=msg)

	#Close Connection
	cur.close()

# Article Form Class
class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min = 1, max = 200)])
	body = TextAreaField('Body', [validators.Length(min = 30)])

#Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		# Create Cursor
		cur = mysql.connection.cursor()

		#Execute
		cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

		# Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('Article Created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_article.html', form=form)

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

#test user/name
@app.route('/user/<name>')
def user(name):
	return'<h1>Hello, %s!</h1>' % name


if __name__ == '__main__':
	#app.secret_key = os.environ.get('SECRET_KEY')
	app.secret_key='secret123'
	manager.run()
