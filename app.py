import json

from flask import Flask, render_template, jsonify, Blueprint, request


app = Flask(__name__)
commands = Blueprint('commands', 'commands')
app.register_blueprint(commands, url_prefix='/command')

commands_list = ['clear']


@app.route('/')
def index():
	username = 'guest'
	prompt = f'{username}@{request.host} $ '
	return render_template('index.html', commands=json.dumps(commands_list), prompt=prompt)


if __name__ == '__main__':
	app.run()
