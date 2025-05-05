import pytest
from api.app import app as flask_app


@pytest.fixture(scope="session")
def client():
    flask_app.config.update({"TESTING": True})
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def runner():
    """Example of invoking Flask CLI commands."""
    return flask_app.test_cli_runner()
