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
from helpers import env, is_dev
import models

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
	working_directory_id = available_commands.file_system.get_working_directory_id()
	working_directory_path = models.FileSystemEntry.get(models.FileSystemEntry.id == working_directory_id).name
	if current_user.is_authenticated:
		username = current_user.username
	return f'{username}@{request.host}:{working_directory_path} $ '


def build_response(result):
	""" Build a response that includes the given result and next prompt """
	return jsonify({
			'result': result,
			'nextPrompt': get_prompt()
		})


@login_manager.user_loader
def load_user(id):
	if not models.User.select().where(models.User.id == id).exists():
		return

	return models.User.get(models.User.id == id)	
	

# @app.route('/')
# def index():
# 	return render_template('index.html', commands=json.dumps(commands_list), prompt=get_prompt())

@app.route('/prompt', methods=['GET'])
def prompt():
	return get_prompt()


@app.route('/run', methods=['POST'])
def run_command():
	commands = request.get_json()["command"].split('|')

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
			except HelpMessage as m:
				stderr = str(m)

		if stderr is not None:
			return build_response(stderr)

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
