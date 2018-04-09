from flask_login import UserMixin
from peewee import *
from werkzeug.security import generate_password_hash

from helpers import env

import logging


db = PostgresqlDatabase('gonano', user=env.data_db_user, password=env.data_db_pass, host=env.data_db_host)


class BaseModel(Model):
	class Meta: 
		database = db


class User(BaseModel, UserMixin):
	username = CharField(unique=True)
	password_hash = CharField()
	working_directory = IntegerField()

	def exists(username=None, id=None):
		if username is None and id is None:
			return False

		if id is not None:
			return User.select().where(User.id == id).exists()

		if username is not None:
			return User.select().where(User.username == username).exists()


class Directory(BaseModel):
	id = IntegerField()
	parent = IntegerField()
	depth = IntegerField()
	name = CharField()

	def get_full_path(self):
		if self.id is not None:
			if self.id is not 0:
				return Directory.get(Directory.id == self.parent).get_full_path() + '\\' + self.name
			else:
				return self.name

#maybe what a File will look like
class File(BaseModel):
	id = IntegerField()
	directory_id = IntegerField()
	name = CharField()
	content = BlobField()
	extension = CharField()

models = [User, Directory, File]

for model in models: 
	model.drop_table(fail_silently=True)
	model.create_table(fail_silently=True)

if not User.select().where(User.username == 'root').exists():
	User.create(username='root', password_hash=generate_password_hash('toor'), working_directory=1)

#demo data for testing
if not Directory.select().where(Directory.id == 0 or Directory.id == 1 or Directory.id == 2 or Directory.id == 3).exists():
	Directory.create(id=0, parent=-1, depth=0, name='root')
	Directory.create(id=1, parent=0, depth=1, name='first')
	Directory.create(id=2, parent=1, depth=2, name='second')
	Directory.create(id=3, parent=0, depth=1, name='first2')