import click
import pytest

import commands


def test_fix_redirect_leaves_string_alone_when_no_redirect():
	c = 'echo -n 123 456'
	assert c == commands.fix_redirect(c)


def test_fix_redirect_replaces_append():
	c = 'echo 123 >> test'
	assert 'echo 123 | redirect_io_append  test' == commands.fix_redirect(c)


def test_fix_redirect_replace_overwrite():
	c = 'echo 123 > test'
	assert 'echo 123 | redirect_io  test' == commands.fix_redirect(c)


def test_get_command_return_click_command():
	c = commands.get_command('echo')
	assert isinstance(c, click.Command)


def test_get_command_raises_for_unknown_command():
	with pytest.raises(AttributeError):
		commands.get_command('unknown_command')


def test_get_command_raises_for_non_command():
	with pytest.raises(AttributeError):
		commands.get_command('get_command')


def test_run_runs_command(client):
	assert commands.run('echo 123')['stdout'] == '123'


def test_run_pipes_commands(client):
	assert commands.run('echo 123 | echo')['stdout'] == '123'
