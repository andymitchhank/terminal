import re

import click
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from utils import help_option, authenticated, print_help
from models import User


@click.command()
@help_option()
@click.pass_context
def help(ctx):
	""" Help text for the application. Type 'help' to view this message.

		Available Commands: 
		clear, echo, help	

		Use '[command] --help' for more information on a specific command. 
	"""
	print_help(ctx, None, True)


@click.command()
@help_option()
@click.option('-n', '--newline', is_flag=True, default=False)
@click.argument('text', nargs=-1)
@click.pass_context
def echo(ctx, text, newline):
	""" Echo back arguments passed in. Strips extra whitespace. """
	if not text: 
		text = [ctx.obj['stdout']]

	joiner = ' ' if not newline else '\n'
	return joiner.join(text)


@click.command()
@help_option()
@click.argument('username')
@click.argument('password')
def login(username, password):
	""" Login a user given username and password. """
	if not User.exists(username=username):
		return "Bad login."

	user = User.get(User.username == username)
	if check_password_hash(user.password_hash, password):
		login_user(user)
		return 'Logged in.'

	return "Bad login."


@click.command()
@help_option()
@authenticated()
def logout():
	""" Logout the current user. """
	logout_user()
	return "Logged out."


@click.command()
@help_option()
@click.argument('new_pass')
@authenticated()
def passwd(new_pass):
	""" Update the current logged in user password. """
	current_user.password_hash = generate_password_hash(new_pass)
	current_user.save()
	return "Password changed."


def _grep(pattern, text):
	return '\n'.join(line for line in text.split('\n') if re.search(pattern, line))


@click.command()
@help_option()
@click.argument('pattern')
@click.argument('filenames', nargs=-1)
@click.pass_context
def grep(ctx, pattern, filenames):
	""" Search for a pattern in files or stdout if piped """
	if not filenames:
		return _grep(pattern, ctx.obj['stdout'])

	return "Grepping files not implemented"



