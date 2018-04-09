import click
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

import click_utils
from models import User, Directory


__all__ = ['echo', 'help', 'login', 'logout', 'passwd', 'working', 'cd', 'ls']


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
@click.argument('directory_name')
def cd(directory_name):
	""" Change directory to the provided directory_name. """
	if not current_user.is_authenticated:
		return "Must be logged in to change directories."

	#look up
	if directory_name == "..":
		if current_user.working_directory != 0:
			return move_working_up()
		else:
			return "Working directory is already root."

	#look down
	if not Directory.select().where((Directory.name == directory_name) & (Directory.parent == current_user.working_directory)).exists():
		return "Directory " + Directory.get(Directory.id == current_user.working_directory).get_full_path() + "\\" + directory_name + " not found."
	else:	
		return move_working_down(directory_name)

@click.command()
@click_utils.help_option()
def working():
	""" Returns the current working directory path. """
	if not current_user.is_authenticated:
		return "Must be logged in to check current working directory path."

	return Directory.get(Directory.id == current_user.working_directory).get_full_path()

@click.command()
@click_utils.help_option()
def ls():
	""" Returns the current working directory path. """
	if not current_user.is_authenticated:
		return "Must be logged in to check current working directory path."

	children = Directory.select().where(Directory.parent == current_user.working_directory)
	if not children:
		return "No child directories found."
	else:
		return "</br>".join([child.get_full_path() for child in children])

	return Directory.get(Directory.id == current_user.working_directory).get_full_path()


def move_working_up():
	parent_id = Directory.get(Directory.id == current_user.working_directory).parent
	current_user.working_directory = parent_id
	current_user.save()
	return "Working directory is now " + Directory.get(Directory.id == parent_id).get_full_path()

def move_working_down(directory_name):
	child = Directory.get((Directory.name == directory_name) & (Directory.parent == current_user.working_directory))
	current_user.working_directory = child.id
	current_user.save()
	return "Working directory is now " + child.get_full_path()