import pytest
from flask_login import current_user

from models import User
from commands.utility import echo, grep


def test_echo_returns_passed_in(run_command):
	result = run_command('echo testing')
	assert result == 'testing' 


def test_echo_returns_stdout_with_no_params():
	to_echo = 'testing'
	obj = {'stdout': to_echo}
	result = echo.main(args=[], standalone_mode=False, obj=obj)
	assert to_echo == result


def test_echo_ignores_stdout_with_params():
	to_echo = 'testing'
	stdout = 'stdout'
	obj = {'stdout': stdout}
	result = echo.main(args=[to_echo], standalone_mode=False, obj=obj)
	assert to_echo != stdout
	assert to_echo == result


def test_grep_returns_processed_stdout_when_no_files(run_command):
	to_grep = '\n'.join(['123', '456', '123', '789'])
	obj = {'stdout': to_grep}
	result = grep.main(args=['1'], standalone_mode=False, obj=obj)
	assert 2 == len(result.split('\n'))


def test_login_returns_bad_login(run_command):
	assert run_command('login dne ???') == 'Bad login.'
	assert run_command('login root ???') == 'Bad login.'


def test_login_sets_current_user(run_command):
	assert not current_user.is_authenticated
	
	run_command('login root toor')
	assert current_user.is_authenticated
	assert current_user.username == 'root'


def test_logout_unsets_current_user(run_command):
	run_command('login root toor')
	assert current_user.is_authenticated

	run_command('logout')
	assert not current_user.is_authenticated


def test_passwd_requires_authentication(run_command):
	assert run_command('passwd ???') == "Must be logged in to run command 'passwd'."


def _get_hash():
	return User.get(User.username == 'root').password_hash


def test_passwd_changes_password(run_command):
	run_command('login root toor')

	prev_hash = _get_hash()
	assert run_command('passwd test') == 'Password changed.'
	assert prev_hash != _get_hash()

	run_command('passwd toor')


def test_passwd_same_password_different_hash(run_command):
	run_command('login root toor')

	prev_hash = _get_hash()
	run_command('password toor')

	assert prev_hash != _get_hash



