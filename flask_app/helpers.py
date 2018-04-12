import os


class EnvironmentType(type):

	def __getattr__(cls, name):
		return os.environ.get(name.upper())


class env(object, metaclass=EnvironmentType):
	pass
