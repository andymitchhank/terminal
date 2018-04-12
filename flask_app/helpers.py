import os

from flask import session

from models import FileSystemEntry


is_dev = os.environ.get('IS_DEV', '') == '1' 


class FileSystem(object):

	@staticmethod
	def working():
		return session.get('working_directory_id', 1)

	@staticmethod
	def working_path():
		return FileSystemEntry.get_full_path(FileSystem.working())

	@staticmethod
	def working_dir():
		return FileSystemEntry.get(FileSystemEntry.id == FileSystem.working()).name
