import pytest
import app
import os
import tempfile
from flask import Flask, flash, redirect, render_template, request, session, abort


db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
application = app.app.test_client()

def test_setUp():
    app.app.testing = True
		
def test_tearDown():
	os.close(db_fd)
	os.unlink(app.app.config['DATABASE'])
	
def test_empty_db():
	rv = application.get('/')
	assert rv.data 
	
def login(username, password):
	return application.post('/login', data=dict(
	    username=username,
	    password=password
	), follow_redirects=True)
	
def test_login():
	rv = login('admin', 'default')
	assert rv.data
	rv = login('admin', 'defaultx')
	assert rv.data
	
	
