from flask_login import UserMixin
from peewee import *
from werkzeug.security import generate_password_hash

from helpers import env

db = PostgresqlDatabase('gonano', user=env.data_db_user, password=env.data_db_pass, host=env.data_db_host)


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
	parent = ForeignKeyField(model='self', field='id', index=True)
	name = CharField()
	depth = IntegerField()
	is_directory = BooleanField()
	content = BlobField(null = True)
	extension = CharField(null = True)

	def get_full_path(self):
		if self.id is not 1:#magic number root id
			return f'{FileSystemEntry.get(FileSystemEntry.id == self.parent).get_full_path()}\{self.name}'
		else:
			return self.name

models = [User, FileSystemEntry]

for model in models: 
	model.drop_table(fail_silently=True)
	model.create_table(fail_silently=True)

if not User.select().where(User.username == 'root').exists():
	User.create(username='root', password_hash=generate_password_hash('toor'))

#demo data for testing directories
FileSystemEntry.create(parent=1, name='root', depth=0, is_directory=True)#points at itself for now
FileSystemEntry.create(parent=1, name='first', depth=1, is_directory=True)
FileSystemEntry.create(parent=2, name='second', depth=2, is_directory=True)
FileSystemEntry.create(parent=1, name='first2', depth=1, is_directory=True)