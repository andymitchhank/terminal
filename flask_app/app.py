from functools import partial
import shlex
import os
from urllib.parse import urlparse

from flask import Flask, Response, jsonify, request, send_from_directory 
from flask_login import LoginManager, current_user
from flask_sockets import Sockets
import requests

import commands as available_commands
from click_utils import HelpMessage, AuthenticationException, authenticated
from helpers import is_dev, FileSystem as fs
from models import FileSystemEntry, User

app = Flask(__name__, static_folder=None)
sockets = Sockets(app)
login_manager = LoginManager(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

react_app_build = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../react_app/build'))
serve_react_file = partial(send_from_directory, react_app_build)


commands_list = ['clear'] + available_commands.__all__


@app.route('/prompt', methods=['GET'])
def get_prompt():
	""" Build a prompt based on the current logged in user or guest """
	username = 'guest'
	if current_user.is_authenticated:
		username = current_user.username
	return f'{username}@{request.host}:{fs.working_dir()} $ '


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


@login_manager.user_loader
def load_user(user_id):
	if not User.exists(id=user_id):
		return
	return User.get(User.id == user_id)	
	

@app.route('/run', methods=['POST'])
def run_command():
	commands = (request.get_json()["command"]
				.replace('>>', '| redirect_io_append ')
				.replace('>', '| redirect_io ')
				.split('|'))

	stdin = None
	stdout = None
	stderr = None

	for command, *stdin in (shlex.split(c) for c in commands):

		if command not in commands_list:
			stderr = f"Command '{command}' not found."
		else:
			click_command = getattr(available_commands, command)
			try: 
				obj = {'stdout': stdout}
				stdout = click_command.main(args=stdin, standalone_mode=False, obj=obj)
			except (HelpMessage, AuthenticationException) as e:
				stderr = str(e)

		if stderr is not None:
			return build_response(stderr)

	if isinstance(stdout, dict):
		return build_response(**stdout)

	return build_response(stdout if stdout else '')


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
