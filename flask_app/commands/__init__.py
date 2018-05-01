import shlex
import sys

import click
from click.exceptions import ClickException

import contexts
from utils import CommandException, get_prompt

from .file_system import *
from .utility import *
from .group_example import *


def fix_redirect(s):
	return s.replace('>>', '| redirect_io_append ').replace('>', '| redirect_io ')


def split(s):
	return s.split('|')	


def get_command(name):
	c = getattr(sys.modules[__name__], name)
	if not isinstance(c, click.Command):
		raise AttributeError
	return c


def run(commands_string):
	commands = split(fix_redirect(commands_string))

	stdin = None
	stdout = None
	stderr = None

	for name, *stdin in (shlex.split(c) for c in commands):

		try:
			command = get_command(name)
		except AttributeError:
			stderr = f"Command '{name}' not found."
		else:
			obj = {'stdout': stdout if isinstance(stdout, str) or not stdout else ''}
			try: 
				stdout = command(args=stdin, standalone_mode=False, obj=obj)
			except (CommandException, ClickException) as e:
				stderr = str(e)
			except Exception as e:
				print(e)
				stderr = 'Unable to process command'

		if stderr is not None:
			stdout = stderr
			break

	if isinstance(stdout, str) or not stdout:
		return contexts.TerminalContext(stdout, get_prompt())._asdict()

	return stdout._asdict()
