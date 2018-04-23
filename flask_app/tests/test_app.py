import json

import pytest
from flask_login import current_user

import app as flask_app


def test_prompt_contains_guest_when_not_logged_in(client):
	prompt = flask_app.get_prompt()
	assert 'guest' in prompt


def test_prompt_contains_username_when_logged_in(root_login):
	prompt = flask_app.get_prompt()
	assert 'root' in prompt
	assert 'guest' not in prompt


def test_prompt_contains_username_when_logged_in_after_command_run(root_login, run_command):
	run_command('echo test')
	prompt = flask_app.get_prompt()
	assert 'root' in prompt
	assert 'guest' not in prompt


def test_prompt_working_is_root_directory_before_cd(client):
	prompt = flask_app.get_prompt()
	directory = prompt.split(' ')[0].split(':')[1]
	assert directory == '/'


def test_prompt_working_is_not_root_after_cd(run_command):
	run_command('cd first')
	prompt = flask_app.get_prompt()
	directory = prompt.split(' ')[0].split(':')[1]
	assert directory == 'first'


def test_response_is_not_found_when_unknown_command(run_command):
	unknown_command = 'unknown_command'
	result = run_command(unknown_command)
	assert result == f"Command '{unknown_command}' not found."


def test_result_contains_command_result_when_found(run_command):
	result = run_command('echo testing')
	assert result == 'testing'


def test_ioredirection_creates_new_file(run_command):
	run_command('login root toor')

	test_file = 'test_ioredirection_overwrite.txt'
	assert test_file not in run_command('ls')
	
	run_command(f'echo 123 > {test_file}')
	assert test_file in run_command('ls')


def test_ioredirection_appends_file_creates_first(run_command):
	run_command('login root toor')

	test_file = 'test_ioredirection_append_create'
	assert test_file not in run_command('ls')

	run_command(f'echo 123 >> {test_file}')
	assert test_file in run_command('ls')


def test_ioredirection_appends_file(run_command):
	run_command('login root toor')
	
	test_file = 'test_ioredirection_append'

	run_command(f'echo 123 >> {test_file}')
	run_command(f'echo 456 >> {test_file}')
	assert test_file in run_command('ls')
	assert '123\n456' == run_command(f'cat {test_file}')


def test_pipe_forwards_stdout_to_command(run_command):
	result = run_command('echo 123 | echo')
	assert result == '123'


def test_current_user_is_none_when_not_logged_in(client):
	assert not current_user.is_authenticated
	

def test_current_user_is_not_none_when_logged_in(run_command):
	assert not current_user.is_authenticated

	run_command('login root toor')
	assert current_user.is_authenticated 
	assert current_user.username == 'root'


def test_load_user_returns_none_when_not_found():
	assert flask_app.load_user(0) is None


def test_load_user_is_not_none_when_found():
	user = flask_app.load_user(1)
	assert user is not None


def test_help_message_returned_when_raised(run_command):
	result = run_command('echo --help')
	assert 'Usage:' in result


def test_is_dev_proxy_to_react_process(monkeypatch):
	def proxy_patch():
		return 'patched'
	monkeypatch.setattr(flask_app, 'is_dev', True)
	monkeypatch.setattr(flask_app, '_proxy', proxy_patch)

	assert flask_app.serve_react('') == 'patched'


def test_not_dev_serves_from_static_path(monkeypatch):
	def serve_patch(_):
		return 'patched'
	monkeypatch.setattr(flask_app, 'is_dev', False)
	monkeypatch.setattr(flask_app, 'serve_react_file', serve_patch)

	assert flask_app.serve_react('') == 'patched'


def test_serve_react_serves_index_with_no_path(monkeypatch):
	def serve_patch(path):
		return path
	monkeypatch.setattr(flask_app, 'is_dev', False)
	monkeypatch.setattr(flask_app, 'serve_react_file', serve_patch)

	assert flask_app.serve_react('') == 'index.html'


def test_serve_react_serves_path_passed_in(monkeypatch):
	def serve_patch(path):
		return path
	monkeypatch.setattr(flask_app, 'is_dev', False)
	monkeypatch.setattr(flask_app, 'serve_react_file', serve_patch)
	monkeypatch.setattr(flask_app, 'react_path_exists', lambda _: True)

	path = '/some/path/to/file.html'
	assert flask_app.serve_react(path) == path

