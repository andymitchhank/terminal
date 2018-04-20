import peewee
import pytest

from models import User, FileSystemEntry as fse


def test_user_exists_returns_false_for_unknown_user():
	assert not User.exists(id=0) 
	assert not User.exists(username='unknown')


def test_user_exists_returns_true_for_root():
	assert User.exists(id=1)
	assert User.exists(username='root')


def test_user_exists_returns_none_with_no_params():
	assert not User.exists() 


def test_get_full_path_for_root_is_empty():
	assert fse.get_by_id(1).get_full_path() == '/'


def test_get_full_path_for_first():
	assert fse.get_by_id(2).get_full_path() == '/first'


def test_get_full_path_for_second():
	assert fse.get_by_id(3).get_full_path() == '/first/second'


def test_get_full_path_for_second_file():
	assert fse.get_by_id(5).get_full_path() == '/first/second/second_file'


def test_find_file_for_second_file():
	path = '/first/second/second_file'
	f = fse.find_file(path)
	assert f.get_full_path() == path
	assert f.name == 'second_file'
	assert not f.is_directory


def test_find_file_for_directory_returns_none():
	assert fse.find_file('/first') is None


def test_find_file_for_non_existant_file_returns_none():
	assert fse.find_file('/dne') is None


def test_find_directory_for_first():
	path = '/first'
	d = fse.find_dir(path)
	assert d.get_full_path() == path
	assert d.is_directory
	assert d.name == 'first'


def test_find_directory_for_second():
	path = '/first/second'
	d = fse.find_dir(path)
	assert d.get_full_path() == path
	assert d.is_directory
	assert d.name == 'second'


def test_find_directory_for_file_returns_none():
	assert fse.find_dir('/first/second/second_file') is None


def test_find_directory_for_non_existant_directory_returns_none():
	assert fse.find_dir('/dne') is None


def test_find_directory_for_root():
	path = '/'
	d = fse.find_dir(path)
	assert d.get_full_path() == '/'
	assert d.name == ''
	assert d.id == 1
	assert d.is_directory


def test_get_child_directory_when_exists():
	child = fse.get_child(1, 'first')
	assert child.get_full_path() == '/first'


def test_get_child_file_when_exists():
	child = fse.get_child(3, 'second_file')
	assert child.get_full_path() == '/first/second/second_file'


def test_get_child_returns_none_when_dne():
	assert fse.get_child(1, 'dne') is None


def test_get_entry_by_id_returns_when_valid():
	assert fse.get_by_id(1) is not None


def test_get_entry_by_id_fails_when_not_vaild():
	with pytest.raises(peewee.DoesNotExist):
		assert fse.get_by_id(0)