import shlex
import json

import click
from flask import Flask, render_template, jsonify, Blueprint, request
from flask_login import LoginManager, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

import commands
from click_utils import HelpMessage
from helpers import env
import models

app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = env.secret_key

commands_list = ['clear', 'login', 'logout'] + commands.__all__


@login_manager.user_loader
def load_user(username):
	if not models.User.select().where(models.User.username == username).exists():
		return

	return models.User.get(models.User.username == username)


@app.route('/login', methods=['POST'])
def login():
	username = request.form.get('username')
	if not models.User.select().where(models.User.username == username).exists():
		return 'No such user'

	user = models.User.get(models.User.username == username)

	if check_password_hash(user.password_hash, request.form.get('password')):
		login_user(user)
		return 'Logged in'

	return 'Bad login'


@app.route('/logout', methods=['POST'])
def logout():
	logout_user()
	return 'Logged out'


@app.route('/')
def index():
	username = 'guest'
	prompt = f'{username}@{request.host} $ '
	return render_template('index.html', commands=json.dumps(commands_list), prompt=prompt)


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

	return result


if __name__ == '__main__':
	app.run('0.0.0.0', 5000)
