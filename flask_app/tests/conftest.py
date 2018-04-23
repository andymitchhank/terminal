import json

from flask import url_for
import pytest

from app import app as flask_app
from models import create_test_data


create_test_data()


@pytest.fixture
def app():
	return flask_app


@pytest.fixture
def run_command(client):
	def run(c):
		return json.loads(client.post(url_for('run_command'), data=json.dumps(dict(command=c)), content_type='application/json').data)['stdout']
	return run


@pytest.fixture
def root_login(run_command):
	run_command('login root toor')





