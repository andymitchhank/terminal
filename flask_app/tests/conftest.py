import pytest

from app import app as flask_app
from models import create_test_data


create_test_data()


@pytest.fixture
def app():
	return flask_app
