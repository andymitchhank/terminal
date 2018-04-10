import json
import shlex

import click
from flask import Flask, render_template, jsonify, Blueprint, request
from flask_login import LoginManager, current_user

import commands as available_commands
from click_utils import HelpMessage
from helpers import env
import models

app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = env.secret_key

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
			'next_prompt': get_prompt()
		})


@login_manager.user_loader
def load_user(id):
	if not models.User.select().where(models.User.id == id).exists():
		return

	return models.User.get(models.User.id == id)	
	

@app.route('/')
def index():
	return render_template('index.html', commands=json.dumps(commands_list), prompt=get_prompt())


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


if __name__ == '__main__':
	app.run('0.0.0.0', 5000)
