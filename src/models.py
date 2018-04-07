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


models = [User]
for model in models: 
	model.create_table(fail_silently=True)

if not User.select().where(User.username == 'root').exists():
	User.create(username='root', password_hash=generate_password_hash('toor'))