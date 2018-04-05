import shlex
import json

import click
from flask import Flask, render_template, jsonify, Blueprint, request

import commands


app = Flask(__name__)

commands_list = ['clear', 'echo']


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
	ctx = click_command.make_context('', command[1:])
	return click_command.invoke(ctx)


if __name__ == '__main__':
	app.run()
