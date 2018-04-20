import os

import flask
from flask_login import UserMixin
from peewee import *
from werkzeug.security import generate_password_hash


db = PostgresqlDatabase(
	'gonano', 
	user=os.environ['DATA_DB_USER'], 
	password=os.environ['DATA_DB_PASS'], 
	host=os.environ['DATA_DB_HOST'])


class BaseModel(Model):
	class Meta: 
		database = db


class User(BaseModel, UserMixin):
	username = CharField(unique=True)
	password_hash = CharField()

	def exists(username=None, id=None):
		if username is None and id is None:
			return False

		if id is not None:
			return User.select().where(User.id == id).exists()

		if username is not None:
			return User.select().where(User.username == username).exists()
	

class FileSystemEntry(BaseModel):
	parent = ForeignKeyField(model='self', field='id', null=True)
	name = CharField()
	depth = IntegerField()
	is_directory = BooleanField()
	content = CharField(null=True)
	extension = CharField(null=True)

	def get_full_path(self):
		entry = self
		parts = []
		while entry: 
			parts.append(entry.name)
			entry = entry.parent

		path = '/'.join(reversed(parts))
		return path if path else '/'

	def get_by_id(id):
		return FileSystemEntry.get(FileSystemEntry.id == id)

	def get_child(parent_id, child_name):
		query = (FileSystemEntry
				.select()
				.where(FileSystemEntry.name == child_name, 
					   FileSystemEntry.parent_id == parent_id))
		
		if query.exists():
			return query.get()

	def find_dir(path):
		if path[-1] == '/' and path != '/':
			path = path[:-1]

		directories = path.split('/')
		dir_name = directories[-1]
		depth = len(directories) - 1

		possible_dirs = FileSystemEntry.select().where(
			FileSystemEntry.name == dir_name and
			FileSystemEntry.depth == depth and 
			FileSystemEntry.is_directory == True)

		for d in possible_dirs:
			if d.get_full_path() == path:
				return d

		return None

	def find_file(path, create=False):
		dirs, file_name = os.path.split(path)
		dir_list = dirs.split('/')
		depth = len(dir_list)

		possible_files = FileSystemEntry.select().where(
			FileSystemEntry.name == file_name and 
			FileSystemEntry.depth == depth and
			FileSystemEntry.is_directory == False)

		for f in possible_files:
			if f.get_full_path() == path:
				return f

		if create:
			d = FileSystemEntry.find_dir(dirs)
			if not d:
				return

			return FileSystemEntry.create(
				parent=d.id, 
				name=file_name, 
				depth=d.depth+1, 
				is_directory=False)	

	@staticmethod
	def get_working():
		try: 
			entry = FileSystemEntry.get_by_id(flask.session.get('working_directory_id', 1))
		except DoesNotExist:
			entry = FileSystemEntry.get_by_id(1)

		return entry

	@staticmethod
	def set_working(entry):
		flask.session['working_directory_id'] = entry.id


models = [User, FileSystemEntry]

for model in models: 
	model.drop_table(fail_silently=True)
	model.create_table(fail_silently=True)

if not User.select().where(User.username == 'root').exists():
	User.create(username='root', password_hash=generate_password_hash('toor'))

if not FileSystemEntry.select().exists():
	FileSystemEntry.create(name='', depth=0, is_directory=True)


def create_test_data():
	FileSystemEntry.create(parent=1, name='first', depth=1, is_directory=True)
	FileSystemEntry.create(parent=2, name='second', depth=2, is_directory=True)
	FileSystemEntry.create(parent=1, name='first2', depth=1, is_directory=True)
	FileSystemEntry.create(parent=3, name='second_file', depth=3, is_directory=False)
	