import os

import click
from flask import session

import click_utils
from models import FileSystemEntry
from helpers import FileSystem as fs


__all__ = ['pwd', 'cd', 'ls', 'cat', 'redirect_io', 'redirect_io_append', 'edit', 'save']

@click.command()
@click_utils.help_option()
@click.argument('path')
@click.argument('content')
@click_utils.authenticated()
def save(path, content):
	""" Save a file given a path and content. Does not create a new file. """
	path = fs.get_absolute_path(path)
	f = FileSystemEntry.find_file(path)
	if f: 
		f.content = content
		f.save()
		return {
			'context': 'terminal',
			'result': f'{path} updated.'
		}

	path, _ = os.path.split(path)
	return {
		'context': 'terminal',
		'result': f'{path} does not exist.'
	}



@click.command()
@click_utils.help_option()
@click.argument('path')
@click_utils.authenticated()
def edit(path):
	""" Edit a file given it's path. Will create a new file if the directory exists."""
	path = fs.get_absolute_path(path)
	f = FileSystemEntry.find_file(path, True)
	if f: 
		return {
			'context': 'editor', 
			'editorContent': f.content,
			'editorPath': path
		}

	path, _ = os.path.split(path)
	return f'{path} does not exist.'



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


@click.command()
@click_utils.help_option()
@click.argument('filename')
def cat(filename):
	entry = FileSystemEntry.get_child(fs.working(), filename)

	if not entry:
		return f'"{filename}" not found'

	if entry.is_directory:
		return f'"{entry.name}" is a directory'	

	return entry.content


def _redirect_io(path, append, stdout):
	if path and path[0] != '/':
		path = os.path.join(fs.working_path(), path)

	f = FileSystemEntry.find_file(path, True)
	if append and f.content is not None:
		stdout = f'{f.content}\n{stdout}'
	f.content = stdout
	f.save()


@click.command()
@click_utils.help_option()
@click.argument('path')
@click.pass_context
@click_utils.authenticated()
def redirect_io(ctx, path):
	""" A special command to handle > """
	_redirect_io(path, False, ctx.obj['stdout'])


@click.command()
@click_utils.help_option()
@click.argument('path')
@click.pass_context
@click_utils.authenticated()
def redirect_io_append(ctx, path):
	""" A special command to handle >> """
	_redirect_io(path, True, ctx.obj['stdout'])




