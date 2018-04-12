import pytest

from commands.utils import echo


def test_echo_returns_passed_in():
	to_echo = 'testing'
	result = echo.callback(['testing'], False)
	assert to_echo == result

