import os

from flask import session

from models import FileSystemEntry


is_dev = os.environ.get('IS_DEV', '') == '1' 


class FileSystem(object):

	def working():
		return session.get('working_directory_id', 1)

	def working_path():
		path = FileSystemEntry.get_full_path(FileSystem.working())
		return path if path else '/'

	def working_dir():
		name = FileSystem.working_entry().name
		return name if name else '/'

	def working_entry():
		return FileSystemEntry.get_by_id(FileSystem.working())

	def set_working(id):
		session['working_directory_id'] = id

	def get_absolute_path(path):
		if not path: 
			return '/'

		if path[0] != '/':
			path = os.path.join(FileSystem.working_path(), path)

		return os.path.abspath(path)
