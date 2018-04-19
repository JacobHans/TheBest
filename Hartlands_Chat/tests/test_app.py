import pytest
import app
import os
import tempfile
from flask import Flask, flash, redirect, render_template, request, session, abort, make_response
from tabledef import *

db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
application = app.app.test_client()

# test setting up database
def test_setUp():
    app.app.testing = True
		
def test_tearDown():
	os.close(db_fd)
	os.unlink(app.app.config['DATABASE'])

# test status code of HTTP GET request to the application	
def test_empty_db():
	rv = application.get('/')
	assert rv.status_code == 200
	
# test login with no user
def login(username, password):
	return application.post('/login', data=dict(
	    username=username,
	    password=password
	), follow_redirects=True)

def test_login():
	rv = login('admin', 'default')
	assert rv.data
	
# test adding new user
def test_user():
	user = User('admin', 'default') 
	assert user.username == 'admin'
	assert user.password == 'default'
	
# test orignate
def test_orignate():
	with app.app.app_context():
		response = app.orginate()
		assert response == '<h1>Sent!</h1>'
	
	
