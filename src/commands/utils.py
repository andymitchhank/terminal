import re

import click
from flask import session
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

import click_utils
from models import User, FileSystemEntry

__all__ = ['echo', 'help', 'login', 'logout', 'passwd', 'pwd', 'cd', 'ls', 'grep']


@click.command()
@click_utils.help_option()
@click.pass_context
def help(ctx):
	""" Help text for the application. Type 'help' to view this message.

		Available Commands: 
		clear, echo, help	

		Use '[command] --help' for more information on a specific command. 
	"""
	click_utils.print_help(ctx, None, True)


@click.command()
@click_utils.help_option()
@click.option('-n', '--newline', is_flag=True, default=False)
@click.argument('text', nargs=-1)
def echo(text, newline):
	""" Echo back arguments passed in. Strips extra whitespace. """
	joiner = ' ' if not newline else '\n'
	return joiner.join(text)


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
	""" Change directory to the provided directory name. Use .. or move down one directory at a time."""
	working_directory_id = get_working_directory_id()
	#look up
	if directory_name == "..":
		if working_directory_id != 1:#magic number - root
			return move_working_up(working_directory_id)
		else:
			return "Working directory is already root."

	#look down
	if not FileSystemEntry.select().where((FileSystemEntry.name == directory_name) & (FileSystemEntry.parent_id == working_directory_id)).exists():
		return "Directory " + FileSystemEntry.get(FileSystemEntry.id == working_directory_id).get_full_path() + "\\" + directory_name + " not found."
	else:	
		return move_working_down(directory_name)

@click.command()
@click_utils.help_option()
def pwd():
	""" Returns the working directory path. """
	working_directory_id = get_working_directory_id()
	return FileSystemEntry.get(FileSystemEntry.id == working_directory_id).get_full_path()

@click.command()
@click_utils.help_option()
def ls():
	""" Returns the working directory path. """
	working_directory_id = get_working_directory_id()
	children = FileSystemEntry.select().where(FileSystemEntry.parent_id == working_directory_id)
	if not children:
		return "No children found."
	else:
		return "<br/>".join(sorted([child.get_full_path() for child in children if child.depth != 0]))#handle root self-referencing for now

def move_working_up(working_directory_id):
	parent_id = FileSystemEntry.get(FileSystemEntry.id == working_directory_id).parent_id
	set_working_directory_id(parent_id)
	return "Working directory is now " + FileSystemEntry.get(FileSystemEntry.id == parent_id).get_full_path()

def move_working_down(directory_name):
	working_directory_id = get_working_directory_id()
	child = FileSystemEntry.get((FileSystemEntry.name == directory_name) & (FileSystemEntry.parent_id == working_directory_id))
	set_working_directory_id(child.id)
	return "Working directory is now " + child.get_full_path()

def get_working_directory_id():
	if 'working_directory_id' not in session:
		set_working_directory_id(1)#this is a magic number and bad. current id for root dir (first auto-incremented primary key)
	return session['working_directory_id']

def set_working_directory_id(id):
	session['working_directory_id'] = id

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



