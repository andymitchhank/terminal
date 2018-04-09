import re

import click
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

import click_utils
from models import User


__all__ = ['echo', 'help', 'login', 'logout', 'passwd', 'grep']


@click.command()
@click_utils.help_option()
@click.pass_context
def help(ctx):
	""" Help text for the applicaiton. Type 'help' to view this message.

		Available Commands: 
		clear, echo, help	

		Use '[command] --help' for more information on a specific command. 
	"""
	click_utils.print_help(ctx, None, True)


@click.command()
@click_utils.help_option()
@click.argument('text', nargs=-1)
def echo(text):
	""" Echo back arguments passed in. Strips extra whitespace. """
	return ' '.join(text)


@click.command()
@click_utils.help_option()
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
@click_utils.help_option()
def logout():
	""" Logout the current user. """
	logout_user()
	return "Logged out."


@click.command()
@click_utils.help_option()
@click.argument('new_pass')
def passwd(new_pass):
	""" Update the current logged in user password. """
	if not current_user.is_authenticated:
		return "Must be logged in to change password."

	current_user.password_hash = generate_password_hash(new_pass)
	current_user.save()
	return "Password changed."


@click.command()
@click_utils.help_option()
@click.argument('pattern')
@click.argument('filename')
def grep(pattern, filename):
	content = filename
	if False: # @TODO after filesystem is implemented, check if filename exists, load content from filename
		pass

	print(content)
	print(content.split('\n'))

	return '\n'.join(line for line in content.split('\n') if re.search(pattern, line))




