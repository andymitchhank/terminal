import pytest

from models import FileSystemEntry as fse


auth_required = "Must be logged in to run command '{}'."


def test_mkdir_creates_dir_in_working(run_command):
	run_command('login root toor')

	dirname = 'mkdir_test_create'
	assert dirname not in run_command('ls')
	assert run_command(f'mkdir {dirname}') == f'/{dirname} created.'
	assert fse.find_dir(f'/{dirname}') is not None


def test_mkdir_create_dir_abspath(run_command):
	run_command('login root toor')

	dirname = '/mkdir_test_abs'
	assert dirname not in run_command('ls')
	assert run_command(f'mkdir {dirname}') == f'{dirname} created.'
	assert fse.find_dir(dirname) is not None


def test_mkdir_requires_auth(run_command):
	dirname = '/mkdir_test_auth'
	assert run_command(f'mkdir {dirname}') == auth_required.format('mkdir')
	assert fse.find_dir(dirname) is None


def test_mkdir_without_parent(run_command):
	run_command('login root toor')

	dirname = '/dne/mkdir_test'
	assert run_command(f'mkdir {dirname}') == '/dne does not exist.'
	assert fse.find_dir(dirname) is None


def test_touch_without_parent(run_command):
	run_command('login root toor')

	filename = '/dne/touch_test'
	assert run_command(f'touch {filename}') == '/dne does not exist.'
	assert fse.find_file(filename) is None


def test_touch_creates_file_in_working(run_command):	
	run_command('login root toor')

	filename = 'touch_test'
	assert filename not in run_command('ls')
	assert run_command(f'touch {filename}') == f'Touched /{filename}'
	assert fse.find_file(f'/{filename}') is not None


def test_touch_creates_file_abspath(run_command):
	run_command('login root toor')

	filename = '/touch_test_abs'
	assert run_command(f'touch {filename}') == f'Touched {filename}'
	assert fse.find_file(filename) is not None


def test_touch_requires_auth(run_command):
	filename = '/touch_test_auth'
	assert run_command(f'touch {filename}') == auth_required.format('touch')
	assert fse.find_file(filename) is None











