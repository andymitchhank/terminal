import os

import click
from flask import session

import click_utils
from models import FileSystemEntry
from helpers import FileSystem as fs


__all__ = ['pwd', 'cd', 'ls']


@click.command()
@click_utils.help_option()
@click.argument('dir_name')
def cd(dir_name):
	""" Change directory to the provided directory name. Use .. or move down one directory at a time."""
	working = fs.working()
	working_entry = fs.working_entry()

	if dir_name == '.':
		return

	if dir_name == "..":
		parent = working_entry.parent
		if parent:
			fs.set_working(parent.id)
		return

	child = FileSystemEntry.get_child(working, dir_name)

	if not child: 
		return f'Directory "{dir_name}" not found'

	if not child.is_directory:
		return f'"{child.name}" is not a directory'
		
	fs.set_working(child.id)


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

