import click
from flask_login import current_user, logout_user
from werkzeug.security import generate_password_hash

import click_utils
from models import User


__all__ = ['echo', 'help', 'logout', 'passwd']


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
@click.argument('text')
def echo(text):
	""" Echo back whatever was passed in. """
	return text


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
