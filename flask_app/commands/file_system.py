import os

import click
from flask import session

import click_utils
from models import FileSystemEntry
from helpers import FileSystem as fs


@click.command()
@click_utils.help_option()
@click.argument('path')
@click_utils.authenticated()
def mkdir(path):
	""" Make a directory, if the parent directory exists. """
	path = fs.get_absolute_path(path)
	parent_path, d = os.path.split(path)

	parent = FileSystemEntry.find_dir(parent_path)
	if parent: 
		entry = FileSystemEntry.create(name=d, parent=parent, depth=parent.depth+1, is_directory=True)
		return f'{path} created.'

	return f'{parent_path} does not exist.'


@click.command()
@click_utils.help_option()
@click.argument('path')
@click_utils.authenticated()
def touch(path):
	""" Create a new file at the given path if the directory exists. If file exists, empties the file. """
	path = fs.get_absolute_path(path)
	f = FileSystemEntry.find_file(path, True)
	if f: 
		f.content = ''
		f.save()
		return f'Touched {path}'

	path, _ = os.path.split(path)
	return f'{path} does not exist.'


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
		return f'{path} updated.'

	path, _ = os.path.split(path)
	return f'{path} does not exist.'


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
@click.argument('path')
def cd(path):
	""" Change directory to the provided directory name. Use .. or move down one directory at a time."""
	path = fs.get_absolute_path(path)
	d = FileSystemEntry.find_dir(path)
	if d:
		fs.set_working(d.id)


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




