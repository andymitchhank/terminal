from typing import NamedTuple
import os

import click
from flask import session
from markdown2 import markdown

from contexts import EditorContext
from models import FileSystemEntry as fse
from utils import abspath, help_option, authenticated


@click.command()
@help_option()
@click.argument('path')
@authenticated()
def mkdir(path):
	""" Make a directory, if the parent directory exists. """
	path = abspath(path, fse.get_working().get_full_path())
	parent_path, d = os.path.split(path)

	parent = fse.find_dir(parent_path)
	if parent: 
		entry = fse.create(name=d, parent=parent, depth=parent.depth+1, is_directory=True)
		return f'{path} created.'

	return f'{parent_path} does not exist.'


@click.command()
@help_option()
@click.argument('path')
@authenticated()
def touch(path):
	""" Create a file, if it doesn't exist, at the given path if the directory exists."""
	path = abspath(path, fse.get_working().get_full_path())
	f = fse.find_file(path, True)
	return f'Touched {path}' if f else f'{os.path.split(path)[0]} does not exist.'


@click.command()
@help_option()
@click.option('--directories', '-d', is_flag=True, default=False, help='Include directories')
@click.argument('paths', nargs=-1)
@authenticated()
def rm(directories, paths):
	""" Remove file or directories. Removing directories will delete all contents within the directory so be careful. """
	func = fse.find_entry if directories else fse.find_file
	entry_ids = [getattr(func(abspath(path, fse.get_working().get_full_path())), 'id', -1) for path in paths] 
	fse.delete().where(fse.id << entry_ids).execute()
	

@click.command()
@help_option()
@click.argument('path')
@click.argument('content')
@authenticated()
def save(path, content):
	""" Save a file given a path and content. Does not create a new file. """
	path = abspath(path, fse.get_working().get_full_path())
	f = fse.find_file(path)
	if f: 
		f.content = content
		f.save()
		return f'{path} updated.'

	path, _ = os.path.split(path)
	return f'{path} does not exist.'


@click.command()
@help_option()
@click.argument('path')
@authenticated()
def edit(path):
	""" Edit a file given it's path. Will create a new file if the directory exists."""
	path = abspath(path, fse.get_working().get_full_path())
	f = fse.find_file(path, True)
	if f: 
		return EditorContext(path, f.content)

	path, _ = os.path.split(path)
	return f'{path} does not exist.'


@click.command()
@help_option()
@click.argument('path')
def cd(path):
	""" Change directory to the provided directory name. Use .. or move down one directory at a time."""
	path = abspath(path, fse.get_working().get_full_path())
	d = fse.find_dir(path)

	if not d:
		return f'{path} does not exists or is not a directory.'

	fse.set_working(d)


@click.command()
@help_option()
def pwd():
	""" Returns the working directory path. """
	return fse.get_working().get_full_path()


@click.command()
@help_option()
def ls():
	""" Returns the working directory path. """
	children = (fse
					.select()
					.where(fse.parent == fse.get_working()))
	return "\n".join(sorted(child.name for child in children))


@click.command()
@help_option()
@click.argument('path')
def cat(path):
	path = abspath(path, fse.get_working().get_full_path())
	entry = fse.find_file(path)

	if not entry:
		return f'"{path}" not found'

	if entry.is_directory:
		return f'"{entry.name}" is a directory'	
		
	_, ext = os.path.splitext(path)
	content = entry.content or ''
	if ext == '.md':
		content = markdown(content)

	return content


def _redirect_io(path, append, stdout):
	path = abspath(path, fse.get_working().get_full_path())

	f = fse.find_file(path, True)
	if append and f.content is not None:
		stdout = f'{f.content}\n{stdout}'
	f.content = stdout
	f.save()


@click.command()
@help_option()
@click.argument('path')
@click.pass_context
@authenticated()
def redirect_io(ctx, path):
	""" A special command to handle > """
	_redirect_io(path, False, ctx.obj['stdout'])


@click.command()
@help_option()
@click.argument('path')
@click.pass_context
@authenticated()
def redirect_io_append(ctx, path):
	""" A special command to handle >> """
	_redirect_io(path, True, ctx.obj['stdout'])




