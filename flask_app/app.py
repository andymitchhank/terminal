from functools import partial
import json
import shlex
import os
from urllib.parse import urlparse

import click
from flask import Flask, render_template, jsonify, Blueprint, request, send_from_directory, Response
from flask_login import LoginManager, current_user
from flask_sockets import Sockets
import requests

import commands as available_commands
from click_utils import HelpMessage
from helpers import env, is_dev, FileSystem as fs
from models import FileSystemEntry, User

app = Flask(__name__, static_folder=None)
sockets = Sockets(app)
login_manager = LoginManager(app)
app.secret_key = env.secret_key

react_app_build = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../react_app/build'))
serve_react_file = partial(send_from_directory, react_app_build)


commands_list = ['clear'] + available_commands.__all__


def get_prompt():
	""" Build a prompt based on the current logged in user or guest """
	username = 'guest'
	if current_user.is_authenticated:
		username = current_user.username
	return f'{username}@{request.host}:{fs.working_dir()} $ '


def build_response(result):
	""" Build a response that includes the given result and next prompt """
	return jsonify({
			'result': result,
			'nextPrompt': get_prompt()
		})


@login_manager.user_loader
def load_user(id):
	if not User.exists(id):
		return
	return User.get(User.id == id)	
	

@app.route('/prompt', methods=['GET'])
def prompt():
	return get_prompt()


def _redirect_io(path, append, stdout):
	if path and path[0] != '/':
		path = os.path.join(fs.working_path(), path)

	f = FileSystemEntry.find_file(path, True)
	if append and f.content is not None:
		stdout = f'{f.content}\n{stdout}'
	f.content = stdout
	f.save()


@app.route('/run', methods=['POST'])
def run_command():
	commands = request.get_json()["command"].split('|')

	stdin = None
	stdout = None
	stderr = None

	redirect_io = None
	final_command = commands[-1]
	if '>>' in final_command:
		c, f = final_command.split('>>', 1)
		redirect_io = partial(_redirect_io, f.strip(), True)
		commands[-1] = c

	if '>' in final_command:
		c, f = final_command.split('>', 1)
		redirect_io = partial(_redirect_io, f.strip(), False)
		commands[-1] = c


	for command, *stdin in (shlex.split(c) for c in commands):

		if command not in commands_list:
			stderr = f"Command '{command}' not found."
		else:
			click_command = getattr(available_commands, command)
			try: 
				obj = {'stdout': stdout}
				stdout = click_command.main(args=stdin, standalone_mode=False, obj=obj)
			except HelpMessage as m:
				stderr = str(m)

		if stderr is not None:
			return build_response(stderr)


	if redirect_io is not None:
		redirect_io(stdout)
		stdout = None
		
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


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
	if is_dev:
		return _proxy()

	if not path or not os.path.exists(os.path.join(react_app_build, path)):
		return serve_react_file('index.html')
	return serve_react_file(path)


if __name__ == '__main__':
	app.run('0.0.0.0', 5000)
