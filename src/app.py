import shlex
import json

import click
from flask import Flask, render_template, jsonify, Blueprint, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

import commands
from click_utils import HelpMessage
from helpers import env
import models

app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = env.secret_key

commands_list = ['clear', 'login', 'logout'] + commands.__all__


def get_prompt():
	""" Build a prompt based on the current logged in user or guest """
	username = 'guest'
	if current_user.is_authenticated:
		username = current_user.username
	return f'{username}@{request.host} $ '


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


@app.route('/login', methods=['POST'])
def login():
	username = request.form.get('username')
	if not models.User.select().where(models.User.username == username).exists():
		return build_response('Bad login')

	user = models.User.get(models.User.username == username)

	if check_password_hash(user.password_hash, request.form.get('password')):
		login_user(user)
		return build_response('Logged in')
	
	return build_response('Bad login')


@app.route('/logout', methods=['POST'])
def logout():
	logout_user()
	return build_response('Logged out')


@app.route('/')
def index():
	return render_template('index.html', commands=json.dumps(commands_list), prompt=get_prompt())


@app.route('/run', methods=['POST'])
def run_command():
	command = shlex.split(request.get_json()["command"])

	if command[0] not in commands_list:
		return f"Command '{command[0]}' not found."

	click_command = getattr(commands, command[0])

	try: 
		ctx = click_command.make_context('', command[1:])
		result = click_command.invoke(ctx)
	except HelpMessage as m:
		result = str(m)

	return build_response(result)


if __name__ == '__main__':
	app.run('0.0.0.0', 5000)
