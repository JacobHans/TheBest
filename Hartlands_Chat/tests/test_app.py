import pytest
import app
import os
import tempfile

db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()

def test_setUp():
    app.app.testing = True
    application = app.app.test_client()
    #with app.app.app_context():
		#app.init_db()
		
def test_tearDown():
	os.close(db_fd)
	os.unlink(app.app.config['DATABASE'])
