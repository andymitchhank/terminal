import os


class EnvironmentType(type):

	def __getattr__(cls, name):
		return os.environ.get(name.upper(), None)


class env(object, metaclass=EnvironmentType):
	pass


is_dev = env.is_dev == '1' 
