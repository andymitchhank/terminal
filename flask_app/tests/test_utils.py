import pytest

from commands.utils import echo, grep


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
