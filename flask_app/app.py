from functools import partial
import os
from urllib.parse import urlparse

from flask import Flask, Response, jsonify, request, send_from_directory 
from flask_login import LoginManager, current_user
from flask_sockets import Sockets
import requests

import commands
from models import FileSystemEntry as fse, User
from utils import is_dev, get_prompt

app = Flask(__name__, static_folder=None)
sockets = Sockets(app)
login_manager = LoginManager(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

react_app_build = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../react_app/build'))
serve_react_file = partial(send_from_directory, react_app_build)


@app.route('/prompt', methods=['GET'])
def prompt():
	""" Build a prompt based on the current logged in user or guest """

def build_response(result='', context='terminal', editorContent='', editorPath=''):
	""" Build a response that includes the given result and next prompt """
	res = jsonify({
			'result': result,
			'nextPrompt': get_prompt(),
			'context': context,
			'editorContent': editorContent,
			'editorPath': editorPath
		})
	return res
	return get_prompt()


@login_manager.user_loader
def load_user(user_id):
	if not User.exists(id=user_id):
		return
	return User.get(User.id == user_id)	
	

@app.route('/run', methods=['POST'])
def run_command():
	rv = commands.run(request.get_json()["command"])

	if isinstance(rv, dict):
		return build_response(**rv)

	return build_response(rv if rv else '')


def _proxy():
	hostname = urlparse(request.url).netloc

	resp = requests.request(
		method = request.method,
		url=request.url.replace(hostname, 'localhost:3000'),
		headers={key: value for key, value in request.headers if key != 'Host'},
		data=request.get_data(),
		cookies=request.cookies,
		allow_redirects=True)

	excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
	headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]

	return Response(resp.content, resp.status_code, headers)


def react_path_exists(path):
	return os.path.exists(os.path.join(react_app_build, path))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
	if is_dev:
		return _proxy()

	if not path or not react_path_exists(path):
		return serve_react_file('index.html')
	return serve_react_file(path)


if __name__ == '__main__':
	app.run('0.0.0.0', 5000)
