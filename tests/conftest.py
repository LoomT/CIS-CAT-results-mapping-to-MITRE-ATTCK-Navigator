import pytest
from api.app import app as flask_app


# scope="session" means it creates one instance for the entire test run
@pytest.fixture(scope="session")
def client():
    flask_app.config.update({"TESTING": True})
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def runner():
    return flask_app.test_cli_runner()
