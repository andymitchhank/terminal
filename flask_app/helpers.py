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
		pieces = path.split('/')
		if pieces[0] == '/':#start from root
			return('/' + build_absolute_path(pieces))
		else:
			return('/' + build_absolute_path([working_path().split('/')] + pieces))

	def build_absolute_path(pieces):
		absolute_path = []
		for piece in pieces:
			if piece == '.':
				continue
			elif piece == '..':
				if len(absolute_path) > 0:
					absolute_path = absolute_path[:-1]
			else:
				absolute_path += [piece]
		return '/'.join(absolute_path)



		

