import os

import click
from flask import session

import click_utils
from models import FileSystemEntry
from helpers import FileSystem as fs


__all__ = ['pwd', 'cd', 'ls']


@click.command()
@click_utils.help_option()
@click.argument('directory_name')
def cd(directory_name):
	""" Change directory to the provided directory name. Use .. or move down one directory at a time."""
	working = fs.working()

	if directory_name == '.':
		return

	if directory_name == "..":
		if working != 1:#magic number - root
			move_working_up(working)
		return

	if not FileSystemEntry.has_child(working, directory_name):
		path = os.path.join(fs.working_path(), directory_name)
		return f"Directory {path} not found."
	else:	
		move_working_down(directory_name)


@click.command()
@click_utils.help_option()
def pwd():
	""" Returns the working directory path. """
	return FileSystemEntry.get_full_path(fs.working())


@click.command()
@click_utils.help_option()
def ls():
	""" Returns the working directory path. """
	children = (FileSystemEntry
					.select()
					.where(FileSystemEntry.parent_id == fs.working()))
	return "\n".join(sorted(child.name for child in children))


def move_working_up(working):
	parent_id = FileSystemEntry.get(FileSystemEntry.id == working).parent_id
	fs.set_working(parent_id)


def move_working_down(directory_name):
	child = (FileSystemEntry
				.get(
					FileSystemEntry.name == directory_name, 
					FileSystemEntry.parent_id == fs.working()))
	fs.set_working(child.id)



