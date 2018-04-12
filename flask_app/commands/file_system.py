import os

import click
from flask import session

import click_utils
from models import FileSystemEntry


__all__ = ['pwd', 'cd', 'ls']


@click.command()
@click_utils.help_option()
@click.argument('directory_name')
def cd(directory_name):
	""" Change directory to the provided directory name. Use .. or move down one directory at a time."""
	working_directory_id = get_working_directory_id()

	if directory_name == '.':
		return

	#look up
	if directory_name == "..":
		if working_directory_id != 1:#magic number - root
			move_working_up(working_directory_id)
		return

	#look down
	if not FileSystemEntry.select().where((FileSystemEntry.name == directory_name) & (FileSystemEntry.parent_id == working_directory_id)).exists():
		return "Directory " + os.path.join(FileSystemEntry.get(FileSystemEntry.id == working_directory_id).get_full_path(), directory_name)+ " not found."
	else:	
		move_working_down(directory_name)


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
	current_and_up = ['.', '..'] if working_directory_id != 1 else ['.']

	children = FileSystemEntry.select().where(FileSystemEntry.parent_id == working_directory_id)

	if not children:
		return '\n'.join(current_and_up)
	else:
		return "\n".join(current_and_up + sorted(child.name for child in children if child.depth != 0))#handle root self-referencing for now


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
