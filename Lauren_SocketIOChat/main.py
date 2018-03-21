""" Need to install flask_socketio and flask_sqlalchemy
https://www.youtube.com/watch?v=pigpDSOBNMc
"""
from flask import Flask
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

# link to database?
engine = create_engine('mysql+mysqldb://lamc8684:database@localhost/chat')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://lamc8684:database@localhost/chat'
db = SQLAlchemy(app)

class History(db.Model):
	id = db.Column('id', db.Integer, primary_key=True)
	message = db.Column('message', db.String(500))

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	
	message = History(message=msg)
	db.session.add(message)
	db.session.commit()
	
	send(msg, broadcast=True)
	
@app.route('/')
def index():
	# ****put our html file name here ****
	messages = History.query.all()
	return render_template('index.html', messages=messages)
	
if __name__ == '__main__':
	socketio.run(app)
