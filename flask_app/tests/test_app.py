import json

import pytest

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


def test_response_has_result_and_nextPrompt_attrs(client):
	resp = json.loads(flask_app.build_response('test').data)
	assert 'nextPrompt' in resp
	assert 'result' in resp


def test_response_is_not_found_when_unknown_command(run_command):
	unknown_command = 'unknown_command'
	result = run_command(unknown_command)
	assert result == f"Command '{unknown_command}' not found."


