import pytest

from commands.utils import echo


def test_echo_returns_passed_in():
	to_echo = 'testing'
	result = echo.main(args=[to_echo], standalone_mode=False)
	assert to_echo == result


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
