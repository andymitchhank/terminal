import os

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

	def get_full_path(id):
		entry = FileSystemEntry.get(FileSystemEntry.id == id)
		parts = []
		while entry: 
			parts.append(entry.name)
			entry = entry.parent

		return '/'.join(reversed(parts))


	def get_by_id(id):
		return FileSystemEntry.get(FileSystemEntry.id == id)

	def find_dir(path):
		if path[-1] == '/':
			path = path[:-1]

		directories = path.split('/')
		dir_name = directories[-1]
		depth = len(directories) - 1

		possible_dirs = FileSystemEntry.select().where(
			FileSystemEntry.name == dir_name and
			FileSystemEntry.depth == depth and 
			FileSystemEntry.is_directory == True)

		for d in possible_dirs:
			print(d.get_full_path())
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
				raise Exception

			return FileSystemEntry.create(
				parent=d.id, 
				name=file_name, 
				depth=d.depth+1, 
				is_directory=False)	


models = [User, FileSystemEntry]

for model in models: 
	model.drop_table(fail_silently=True)
	model.create_table(fail_silently=True)

if not User.select().where(User.username == 'root').exists():
	User.create(username='root', password_hash=generate_password_hash('toor'))

#demo data for testing directories
FileSystemEntry.create(name='', depth=0, is_directory=True)#points at itself for now
FileSystemEntry.create(parent=1, name='first', depth=1, is_directory=True)
FileSystemEntry.create(parent=2, name='second', depth=2, is_directory=True)
FileSystemEntry.create(parent=1, name='first2', depth=1, is_directory=True)
FileSystemEntry.create(parent=3, name='second_file', depth=3, is_directory=False)

FileSystemEntry.find_file('/first/second/second_file')
FileSystemEntry.find_dir('/first')
FileSystemEntry.find_file('/first/create', True)