from helpers import * 


def test_fs_working_should_be_1_when_not_set(app):
	with app.app_context():
		assert FileSystem.working() == 1


def test_fs_working_should_be_set_value(app):
	with app.app_context():
		FileSystem.set_working(2)
		assert FileSystem.working() == 2


def test_fs_default_working_entry_is_root(app):
	with app.app_context():
		entry = FileSystem.working_entry()

		assert entry is not None
		assert entry.name == ''
		assert entry.id == 1


def test_fs_default_working_path_is_root(app):
	with app.app_context():
		assert FileSystem.working_path() == '/'


def test_fs_working_2_is_first(app):
	with app.app_context():
		FileSystem.set_working(2)
		entry = FileSystem.working_entry()
		path = FileSystem.working_path()

		assert entry is not None
		assert entry.name == 'first'
		assert entry.id == 2


def test_fs_working_2_path_is_first(app):
	with app.app_context():
		FileSystem.set_working(2)
		assert FileSystem.working_path() == '/first'


def test_fs_default_working_dir_is_root(app):
	with app.app_context():
		assert FileSystem.working_dir() == '/'


def test_fs_working_2_dir_is_first(app):
	with app.app_context():
		FileSystem.set_working(2)
		assert FileSystem.working_dir() == 'first'




